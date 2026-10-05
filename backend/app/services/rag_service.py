from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import (
    generate_answer,
    generate_general_answer,
    generate_chat_history_answer,
)
from app.models.user_role import UserRole
from app.models.role import Role

from app.services.chat_service import (
    get_chat_history,
    save_message,
    search_chat_history,
)

from app.services.intent_classifier import classify_query_with_llm
from app.models.chat_message import ChatMessage

from app.services.access_intelligence_service import (
    answer_my_permissions,
    answer_user_query,
    answer_access_question,
    answer_access_management_question,
    perform_document_access_action,
    answer_role_question,
    answer_role_membership_question,
    perform_role_management_action,
    answer_user_intelligence_query,
    answer_user_status_query,
    perform_user_status_action,
    answer_permission_query,
)

from app.services.access_service import (
    user_can_access_document,
    user_has_permission,
    find_user_by_name,
)

from app.services.access_query_service import find_document_by_name

from app.services.login_activity_service import answer_login_activity

from app.services.audit_intelligence_service import (
    answer_recent_audit_activity,
    answer_audit_activity_by_date,
)


def build_rag_context(
    db: Session,
    query: str,
    user_id: int,
    top_k: int = 5,
    similarity_threshold: float = 0.30,
    relevance_threshold: float = 0.40,
) -> dict:

    results = search_similar_chunks(
        db=db,
        query=query,
        user_id=user_id,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
        relevance_threshold=relevance_threshold,
    )

    documents = {}
    sources = []

    for chunk, score in results:

        document_id = chunk.document_id
        document_name = chunk.document.name

        if document_id not in documents:
            documents[document_id] = {
                "document_name": document_name,
                "chunks": [],
            }

        documents[document_id]["chunks"].append(
            {
                "chunk_id": chunk.id,
                "content": chunk.content,
                "similarity": float(score),
            }
        )

        sources.append(
            {
                "document_id": document_id,
                "document_name": document_name,
                "chunk_id": chunk.id,
                "similarity": float(score),
            }
        )

    context_parts = []

    for document in documents.values():

        context_parts.append(
            f"DOCUMENT: {document['document_name']}\n"
            f"{'-' * 60}"
        )

        for index, chunk in enumerate(document["chunks"], start=1):

            context_parts.append(
                f"\nRelevant section {index} "
                f"(similarity: {chunk['similarity']:.3f}):\n"
                f"{chunk['content']}"
            )

    context = "\n\n".join(context_parts)

    return {
        "query": query,
        "context": context,
        "results_count": len(results),
        "documents_count": len(documents),
        "sources": sources,
    }

def ask_rag(
    db: Session,
    question: str,
    user_id: int,
    top_k: int = 5,
    similarity_threshold: float = 0.30,
) -> dict:

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")

    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError(
            "similarity_threshold must be between 0.0 and 1.0"
        )

    intent_result = classify_query_with_llm(question)

    query_type = intent_result.get("intent")

    username = intent_result.get("username")
    role_name = intent_result.get("role_name")
    document_name = intent_result.get("document_name")
    action = intent_result.get("action")
    topic = intent_result.get("topic")

    if query_type == "chat_history_query":

        # Topic-based conversation search
        if topic:

            history = search_chat_history(
                db=db,
                user_id=user_id,
                search_terms=[topic],
                limit=30,
            )

        # General conversation-history request
        else:

            history = get_chat_history(
                db=db,
                user_id=user_id,
                limit=20,
            )

        if not history:

            answer = (
                "I couldn't find any relevant previous "
                "conversation history."
            )

            save_message(
                db=db,
                user_id=user_id,
                role="user",
                content=question,
            )

            save_message(
                db=db,
                user_id=user_id,
                role="assistant",
                content=answer,
            )

            return {
                "question": question,
                "question_type": "chat_history_query",
                "success": True,
                "answer": answer,
                "sources": [],
            }

        question_lower = question.lower()

        exact_previous_question = any(
            phrase in question_lower
            for phrase in [
                "previous question",
                "previous message",
                "last question",
                "last message",
                "what did i ask before",
                "what was i asking before",
            ]
        )

        if exact_previous_question:

            previous_user_messages = [
                message
                for message in history
                if message.role == "user"
            ]

            if previous_user_messages:

                answer = (
                    f'Your previous question was: '
                    f'"{previous_user_messages[-1].content}"'
                )

            else:

                answer = (
                    "I couldn't find a previous question "
                    "in our conversation history."
                )

        else:

            history_text = "\n".join(
                f"{message.role}: {message.content}"
                for message in history
            )

            answer = generate_chat_history_answer(
                question=question,
                chat_history=history_text,
            )

        save_message(
            db=db,
            user_id=user_id,
            role="user",
            content=question,
        )

        save_message(
            db=db,
            user_id=user_id,
            role="assistant",
            content=answer,
        )

        return {
            "question": question,
            "question_type": "chat_history_query",
            "success": True,
            "answer": answer,
            "sources": [],
        }

    if query_type == "general_conversation":

        chat_history = get_chat_history(
            db=db,
            user_id=user_id,
            limit=10,
        )

        history_text = "\n".join(
            f"{message.role}: {message.content}"
            for message in chat_history
        )

        save_message(
            db=db,
            user_id=user_id,
            role="user",
            content=question,
        )

        answer = generate_general_answer(
            question=question,
            chat_history=history_text,
        )

        save_message(
            db=db,
            user_id=user_id,
            role="assistant",
            content=answer,
        )

        return {
            "question": question,
            "question_type": "general_conversation",
            "answer": answer,
            "sources": [],
        }

    if query_type == "login_activity":

        if not user_has_permission(
            db,
            user_id,
            "audit.read",
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission required: audit.read",
            )

        return answer_login_activity(
            db=db,
            question=question,
        )

    if query_type == "recent_audit_activity":

        if not user_has_permission(
            db,
            user_id,
            "audit.read",
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission required: audit.read",
            )

        return answer_recent_audit_activity(
            db=db,
            question=question,
            resource_type=intent_result.get("resource_type"),
        )

    if query_type == "today_audit_activity":

        if not user_has_permission(
            db,
            user_id,
            "audit.read",
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission required: audit.read",
            )

        return answer_audit_activity_by_date(
            db=db,
            question=question,
            resource_type=intent_result.get("resource_type"),
            username=intent_result.get("username"),
        )

    if query_type == "my_permissions":

        return answer_my_permissions(
            db=db,
            user_id=user_id,
        )

    if query_type == "permission_query":

        if not role_name:
            return {
                "question_type": "permission_query",
                "success": False,
                "answer": (
                    "I could not identify the role in "
                    "the permission query."
                ),
            }

        return answer_permission_query(
            db=db,
            role_name=role_name,
        )

    if query_type == "role_membership":

        if not username or not role_name:
            return {
                "question_type": "role_membership",
                "has_role": False,
                "answer": (
                    "I could not identify both the user "
                    "and role."
                ),
            }

        return answer_role_membership_question(
            db=db,
            username=username,
            role_name=role_name,
        )

    if query_type == "role_management":

        if not action or not username or not role_name:
            return {
                "question_type": "role_management",
                "success": False,
                "answer": (
                    "I could not understand the role "
                    "management request."
                ),
            }

        if not user_has_permission(
            db,
            user_id,
            "role.manage",
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission required: role.manage",
            )

        return perform_role_management_action(
            db=db,
            action=action,
            username=username,
            role_name=role_name,
            actor_user_id=user_id,
        )

    if query_type == "role_assignment_check":

        if not username or not role_name:
            return {
                "question_type": "role_assignment_check",
                "success": False,
                "answer": (
                    "I could not identify both the user "
                    "and role."
                ),
            }

        target_user = find_user_by_name(
            db=db,
            name=username,
        )

        if target_user is None:
            return {
                "question_type": "role_assignment_check",
                "success": False,
                "username": username,
                "role_name": role_name,
                "answer": (
                    f"I could not find a user named "
                    f"{username}."
                ),
            }
        
        role = db.query(Role).filter(
            Role.name.ilike(role_name)
        ).first()

        if role is None:
            return {
                "question_type": "role_assignment_check",
                "success": False,
                "username": target_user.username,
                "role_name": role_name,
                "answer": (
                    f"I could not find a role named "
                    f"{role_name}."
                ),
            }

        existing_assignment = db.query(UserRole).filter(
            UserRole.user_id == target_user.id,
            UserRole.role_id == role.id,
        ).first()

        if existing_assignment:
            return {
                "question_type": "role_assignment_check",
                "success": True,
                "username": target_user.username,
                "role_name": role.name,
                "assigned": True,
                "answer": (
                    f"{target_user.full_name} "
                    f"({target_user.username}) already has "
                    f"the {role.name} role."
                ),
            }

        return {
            "question_type": "role_assignment_check",
            "success": True,
            "username": target_user.username,
            "role_name": role.name,
            "assigned": False,
            "answer": (
                f"{target_user.full_name} "
                f"({target_user.username}) does not currently "
                f"have the {role.name} role."
            ),
        }

    if query_type == "role_query":

        return answer_role_question(
            db=db,
            username=username,
            role_name=role_name,
        )

    if query_type == "user_intelligence":

        if not username:
            return {
                "question_type": "user_intelligence",
                "success": False,
                "answer": (
                    "I could not identify the user "
                    "in your question."
                ),
            }

        return answer_user_intelligence_query(
            db=db,
            username=username,
        )

    if query_type == "user_query":

        if not username:
            return {
                "question_type": "user_query",
                "success": False,
                "answer": (
                    "I could not identify the user "
                    "in your question."
                ),
            }

        return answer_user_query(
            db=db,
            username=username,
        )

    if query_type == "user_status_action":

        if not action or not username:
            return {
                "question_type": "user_status_action",
                "success": False,
                "answer": (
                    "I could not understand the user "
                    "status action."
                ),
            }

        if not user_has_permission(
            db,
            user_id,
            "user.manage",
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission required: user.manage",
            )

        return perform_user_status_action(
            db=db,
            action=action,
            username=username,
            actor_user_id=user_id,
        )

    if query_type == "user_status_query":

        if not username:
            return {
                "question_type": "user_status_query",
                "success": False,
                "answer": (
                    "I could not identify the user "
                    "in your question."
                ),
            }

        return answer_user_status_query(
            db=db,
            username=username,
        )

    if query_type == "document_access":

        if not document_name:
            return {
                "question_type": "document_access",
                "success": True,
                "answer": (
                    "Document access can be provided through role-based access "
                    "or direct user access. Role-based access gives users access "
                    "through their assigned roles, while direct access grants "
                    "access to a specific user."
                ),
                "sources": [],
            }

        return answer_access_question(
            db=db,
            document_name=document_name,
        )
    if query_type == "document_access_action":

        if not action or not username or not document_name:
            return {
                "question_type": "document_access_action",
                "success": False,
                "answer": (
                    "I could not understand the document "
                    "access action."
                ),
            }

        if not user_has_permission(
            db,
            user_id,
            "access.grant",
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission required: access.grant",
            )

        return perform_document_access_action(
            db=db,
            action=action,
            username=username,
            document_name=document_name,
            actor_user_id=user_id,
        )

    if query_type == "access_management":

        return answer_access_management_question(
            db=db,
            document_name=document_name,
        )

    if query_type == "document_access_check":

        if not document_name:
            return {
                "question_type": "document_access_check",
                "has_access": False,
                "answer": (
                    "I could not identify the document "
                    "in your question."
                ),
            }

        document = find_document_by_name(
            db=db,
            document_name=document_name,
        )

        if document is None:
            return {
                "question_type": "document_access_check",
                "document_name": document_name,
                "has_access": False,
                "answer": (
                    f"I could not find a document named "
                    f"{document_name}."
                ),
            }

        if username:

            target_user = find_user_by_name(
                db=db,
                name=username,
            )

            if target_user is None:
                return {
                    "question_type": "document_access_check",
                    "document_id": document.id,
                    "document_name": document.name,
                    "has_access": False,
                    "answer": (
                        f"I could not find a user named "
                        f"{username}."
                    ),
                }

            has_access = user_can_access_document(
                db=db,
                user_id=target_user.id,
                document_id=document.id,
            )

            if has_access:
                answer = (
                    f"Yes, {target_user.full_name} "
                    f"({target_user.username}) has access "
                    f"to {document.name}."
                )
            else:
                answer = (
                    f"No, {target_user.full_name} "
                    f"({target_user.username}) does not have "
                    f"access to {document.name}."
                )

            return {
                "question_type": "document_access_check",
                "document_id": document.id,
                "document_name": document.name,
                "target_user_id": target_user.id,
                "target_username": target_user.username,
                "has_access": has_access,
                "answer": answer,
            }

        has_access = user_can_access_document(
            db=db,
            user_id=user_id,
            document_id=document.id,
        )

        if has_access:
            answer = (
                f"Yes, you have access to "
                f"{document.name}."
            )
        else:
            answer = (
                f"No, you do not have access to "
                f"{document.name}."
            )

        return {
            "question_type": "document_access_check",
            "document_id": document.id,
            "document_name": document.name,
            "has_access": has_access,
            "answer": answer,
        }

    if query_type == "document_rag":

        chat_history = get_chat_history(
            db=db,
            user_id=user_id,
            limit=10,
        )

        history_text = "\n".join(
            f"{message.role}: {message.content}"
            for message in chat_history
        )

        save_message(
            db=db,
            user_id=user_id,
            role="user",
            content=question,
        )

        rag_context = build_rag_context(
            db=db,
            query=question,
            user_id=user_id,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            relevance_threshold=0.40,
        )

        if not rag_context["context"] and not history_text:

            answer = (
                "I don't have enough information "
                "in the provided documents."
            )

            save_message(
                db=db,
                user_id=user_id,
                role="assistant",
                content=answer,
            )

            return {
                "question": question,
                "answer": answer,
                "sources": [],
            }

        answer = generate_answer(
            question=question,
            context=rag_context["context"],
            chat_history=history_text,
        )

        save_message(
            db=db,
            user_id=user_id,
            role="assistant",
            content=answer,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": rag_context["sources"],
        }

    return {
        "question": question,
        "answer": (
            "I could not determine what you are asking. "
            "Please try asking in a different way."
        ),
        "sources": [],
    }