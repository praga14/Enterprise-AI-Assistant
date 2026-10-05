from sqlalchemy.orm import Session

from app.services.access_query_service import get_document_access_by_name
from app.services.access_service import  find_user_by_name

from sqlalchemy import select

from app.models.role import Role
from app.models.document import Document
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission


from app.services.document_access_service import (
    grant_document_access,
    revoke_document_access,
)
from app.services.audit_service import create_audit_log


def answer_access_question(
    db: Session,
    document_name: str,
) -> dict:
    access_info = get_document_access_by_name(
        db=db,
        document_name=document_name,
    )

    users = access_info["users"]

    if not users:
        answer = f"No users currently have access to {access_info['document_name']}."
    else:
        user_details = []

        for user in users:
            if user["access_type"] == "role":
                access_description = f"through the {user['role_name']} role"
            elif user["access_type"] == "direct":
                access_description = "through direct user access"
            else:
                access_description = (
                    f"through the {user['role_name']} role "
                    "and direct user access"
                )

            user_details.append(
                f"{user['full_name']} ({user['username']}) "
                f"{access_description}"
            )

        answer = (
            f"The following users have access to "
            f"{access_info['document_name']}: "
            + ", ".join(user_details)
            + "."
        )

    return {
        "question_type": "document_access",
        "document_id": access_info["document_id"],
        "document_name": access_info["document_name"],
        "answer": answer,
        "users": users,
    }

def get_user_permissions(
    db: Session,
    user_id: int,
):
    statement = (
        select(Permission)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .join(
            UserRole,
            UserRole.role_id == RolePermission.role_id,
        )
        .where(
            UserRole.user_id == user_id,
            Permission.is_active.is_(True),
        )
        .distinct()
    )

    return list(db.scalars(statement).all())

def build_permission_summary(permissions) -> str:
    """
    Convert technical permission records into a natural-language
    capability summary for the user.
    """

    capabilities = []

    permission_names = {
        permission.name
        for permission in permissions
    }

    # Documents
    if "document.read" in permission_names:
        capabilities.append("view and retrieve authorized company documents")

    if "document.access.read" in permission_names:
        capabilities.append("see who has access to company documents")

    # Code
    if "code.read" in permission_names:
        if "code.write" in permission_names:
            capabilities.append("read and modify source code")
        else:
            capabilities.append("read source code")
    elif "code.write" in permission_names:
        capabilities.append("modify source code")

    # Users
    if "user.manage" in permission_names:
        capabilities.append("manage user accounts")
    elif "user.read" in permission_names:
        capabilities.append("view user accounts")

    # Roles
    if "role.manage" in permission_names:
        capabilities.append("manage roles and role assignments")
    elif "role.read" in permission_names:
        capabilities.append("view roles and role assignments")

    # Permissions
    if "permission.manage" in permission_names:
        capabilities.append("manage system permissions")
    elif "permission.read" in permission_names:
        capabilities.append("view system permissions")

    # Document access management
    if "access.grant" in permission_names:
        capabilities.append("grant access to resources")

    # Audit
    if "audit.read" in permission_names:
        capabilities.append("view audit activity")

    if not capabilities:
        return "You currently don't have any active capabilities assigned to you."

    if len(capabilities) == 1:
        return f"You can {capabilities[0]}."

    if len(capabilities) == 2:
        return f"You can {capabilities[0]} and {capabilities[1]}."

    return (
        "You can "
        + ", ".join(capabilities[:-1])
        + f", and {capabilities[-1]}."
    )


def build_role_permission_summary(
    role_name: str,
    permissions,
) -> str:
    summary = build_permission_summary(permissions)

    if summary.startswith("You can "):
        summary = summary[len("You can "):]

    return f"The {role_name} role can {summary}"



def answer_my_permissions(
    db: Session,
    user_id: int,
) -> dict:
    permissions = get_user_permissions(
        db=db,
        user_id=user_id,
    )

    permission_details = [
        {
            "name": permission.name,
            "description": permission.description,
            "resource": permission.resource,
            "action": permission.action,
        }
        for permission in permissions
    ]

    answer = build_permission_summary(permissions)

    return {
        "question_type": "my_permissions",
        "answer": answer,
        "permissions": permission_details,
    }


def answer_access_management_question(
    db: Session,
    document_name: str | None = None,
):
    permission_name = "access.grant"

    if document_name:
        statement = (
            select(Document)
            .where(Document.name.ilike(document_name))
            .limit(1)
        )

        document = db.scalar(statement)

        if document is None:
            return {
                "question_type": "access_management",
                "document_name": document_name,
                "permission": permission_name,
                "users": [],
                "answer": (
                    f"I could not find a document named {document_name}."
                ),
            }

    statement = (
        select(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .where(
            Permission.name == permission_name,
            Permission.is_active.is_(True),
            User.is_active.is_(True),
        )
        .distinct()
    )

    users = list(db.scalars(statement).all())

    if not users:
        return {
            "question_type": "access_management",
            "document_name": document_name,
            "permission": permission_name,
            "users": [],
            "answer": (
                "No active users currently have permission "
                "to grant or revoke access."
            ),
        }

    user_names = [
        f"{user.full_name} ({user.username})"
        for user in users
    ]

    document_text = (
        f" to {document.name}"
        if document_name
        else " to documents"
    )

    return {
        "question_type": "access_management",
        "document_id": document.id if document_name else None,
        "document_name": document.name if document_name else None,
        "permission": permission_name,
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
            }
            for user in users
        ],
        "answer": (
            "The following users have permission to grant or revoke "
            f"access{document_text}: "
            + ", ".join(user_names)
            + "."
        ),
    }


def perform_document_access_action(
    db: Session,
    action: str,
    username: str,
    document_name: str,
    actor_user_id: int,
):
        # Backend authorization
    permission_statement = (
        select(Permission)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .join(
            UserRole,
            UserRole.role_id == RolePermission.role_id,
        )
        .where(
            UserRole.user_id == actor_user_id,
            Permission.name == "access.grant",
            Permission.is_active.is_(True),
        )
    )

    permission = db.scalar(permission_statement)

    if permission is None:
        return {
            "question_type": "document_access_action",
            "success": False,
            "answer": "You do not have permission to grant or revoke document access.",
        }
    user = find_user_by_name(db, username)

    if user is None:
        return {
            "question_type": "document_access_action",
            "success": False,
            "answer": f"User '{username}' not found.",
        }

    document_statement = (
        select(Document)
        .where(
            Document.name.ilike(f"%{document_name.strip()}%")
        )
        .limit(1)
    )
    document = db.scalar(document_statement)

    if document is None:
        return {
            "question_type": "document_access_action",
            "success": False,
            "answer": f"Document '{document_name}' not found.",
        }

    if action in ("grant", "give"):
        changed = grant_document_access(
            db=db,
            user_id=user.id,
            document_id=document.id,
        )

        if not changed:
            return {
                "question_type": "document_access_action",
                "success": False,
                "answer": (
                    f"{user.username} already has direct access "
                    f"to '{document.name}'."
                ),
            }

        create_audit_log(
            db=db,
            actor_user_id=actor_user_id,
            action="document.access.grant",
            resource_type="DOCUMENT",
            resource_id=document.id,
            target_user_id=user.id,
            details=(
                f"Granted direct access to document "
                f"'{document.name}' for user '{user.username}'"
            ),
        )

        return {
            "question_type": "document_access_action",
            "success": True,
            "action": "grant",
            "username": user.username,
            "document_name": document.name,
            "answer": (
                f"Granted direct access to '{document.name}' "
                f"for {user.username}."
            ),
        }

    if action in ("revoke", "remove"):
        changed = revoke_document_access(
            db=db,
            user_id=user.id,
            document_id=document.id,
        )

        if not changed:
            return {
                "question_type": "document_access_action",
                "success": False,
                "answer": (
                    f"{user.username} does not have direct access "
                    f"to '{document.name}'."
                ),
            }

        create_audit_log(
            db=db,
            actor_user_id=actor_user_id,
            action="document.access.revoke",
            resource_type="DOCUMENT",
            resource_id=document.id,
            target_user_id=user.id,
            details=(
                f"Revoked direct access to document "
                f"'{document.name}' from user '{user.username}'"
            ),
        )

        return {
            "question_type": "document_access_action",
            "success": True,
            "action": "revoke",
            "username": user.username,
            "document_name": document.name,
            "answer": (
                f"Revoked direct access to '{document.name}' "
                f"from {user.username}."
            ),
        }

    return {
        "question_type": "document_access_action",
        "success": False,
        "answer": f"Unsupported document access action: {action}",
    }

def answer_role_question(
    db: Session,
    username: str | None = None,
    role_name: str | None = None,
):
    if username:
        user_statement = (
            select(User)
            .where(
                (User.username.ilike(username))
                | (User.full_name.ilike(username))
            )
            .limit(1)
        )

        user = db.scalar(user_statement)

        if user is None:
            return {
                "question_type": "role_query",
                "username": username,
                "roles": [],
                "answer": f"I could not find a user named {username}.",
            }

        statement = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id)
        )

        roles = list(db.scalars(statement).all())

        return {
            "question_type": "role_query",
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                }
                for role in roles
            ],
            "answer": (
                f"{user.full_name} ({user.username}) has the following roles: "
                + (
                    ", ".join(role.name for role in roles)
                    if roles
                    else "No roles assigned."
                )
                + "."
            ),
        }

    if role_name:
        statement = (
            select(User, Role)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.name.ilike(role_name))
        )

        rows = db.execute(statement).all()

        if not rows:
            return {
                "question_type": "role_query",
                "role_name": role_name,
                "users": [],
                "answer": f"I could not find users with the {role_name} role.",
            }

        users = []
        for user, role in rows:
            users.append({
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
            })

        return {
            "question_type": "role_query",
            "role_id": rows[0][1].id,
            "role_name": rows[0][1].name,
            "users": users,
            "answer": (
                f"The following users have the {rows[0][1].name} role: "
                + ", ".join(
                    f"{user['full_name']} ({user['username']})"
                    for user in users
                )
                + "."
            ),
        }

    return {
        "question_type": "role_query",
        "answer": "Please specify a user or role.",
    }

def answer_role_membership_question(
    db: Session,
    username: str,
    role_name: str,
):
    user_statement = (
        select(User)
        .where(
            (User.username.ilike(username))
            | (User.full_name.ilike(username))
        )
        .limit(1)
    )

    user = db.scalar(user_statement)

    if user is None:
        return {
            "question_type": "role_membership",
            "username": username,
            "role_name": role_name,
            "has_role": False,
            "answer": f"I could not find a user named {username}.",
        }

    role_statement = (
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(
            UserRole.user_id == user.id,
            Role.name.ilike(role_name),
        )
        .limit(1)
    )

    role = db.scalar(role_statement)

    has_role = role is not None

    return {
        "question_type": "role_membership",
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role_name": role_name,
        "has_role": has_role,
        "answer": (
            f"Yes, {user.full_name} ({user.username}) has the "
            f"{role.name} role."
            if has_role
            else f"No, {user.full_name} ({user.username}) does not have "
            f"the {role_name} role."
        ),
    }

def perform_role_management_action(
    db: Session,
    action: str,
    username: str,
    role_name: str,
    actor_user_id: int,
):
    user_statement = (
        select(User)
        .where(
            (User.username.ilike(username))
            | (User.full_name.ilike(username))
        )
        .limit(1)
    )

    user = db.scalar(user_statement)

    if user is None:
        return {
            "question_type": "role_management",
            "action": action,
            "username": username,
            "role_name": role_name,
            "success": False,
            "answer": f"I could not find a user named {username}.",
        }

    role_statement = (
        select(Role)
        .where(Role.name.ilike(role_name))
        .limit(1)
    )

    role = db.scalar(role_statement)

    if role is None:
        return {
            "question_type": "role_management",
            "action": action,
            "username": user.username,
            "role_name": role_name,
            "success": False,
            "answer": f"I could not find a role named {role_name}.",
        }

    existing = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
    )

    if action == "grant":
        if existing is not None:
            return {
                "question_type": "role_management",
                "action": action,
                "user_id": user.id,
                "username": user.username,
                "role_id": role.id,
                "role_name": role.name,
                "success": False,
                "answer": (
                    f"{user.full_name} ({user.username}) already has "
                    f"the {role.name} role."
                ),
            }

        db.add(
            UserRole(
                user_id=user.id,
                role_id=role.id,
            )
        )
        db.commit()

        create_audit_log(
            db=db,
            actor_user_id=actor_user_id,
            action="role.grant",
            resource_type="role",
            resource_id=role.id,
            target_user_id=user.id,
            details=f"Assigned role {role.name} to user {user.username}",
        )

        return {
            "question_type": "role_management",
            "action": action,
            "user_id": user.id,
            "username": user.username,
            "role_id": role.id,
            "role_name": role.name,
            "success": True,
            "answer": (
                f"The {role.name} role was assigned to "
                f"{user.full_name} ({user.username})."
            ),
        }

    if action == "remove":
        if existing is None:
            return {
                "question_type": "role_management",
                "action": action,
                "user_id": user.id,
                "username": user.username,
                "role_id": role.id,
                "role_name": role.name,
                "success": False,
                "answer": (
                    f"{user.full_name} ({user.username}) does not have "
                    f"the {role.name} role."
                ),
            }

        db.delete(existing)
        db.commit()

        create_audit_log(
            db=db,
            actor_user_id=actor_user_id,
            action="role.remove",
            resource_type="role",
            resource_id=role.id,
            target_user_id=user.id,
            details=f"Removed role {role.name} from user {user.username}",
        )

        return {
            "question_type": "role_management",
            "action": action,
            "user_id": user.id,
            "username": user.username,
            "role_id": role.id,
            "role_name": role.name,
            "success": True,
            "answer": (
                f"The {role.name} role was removed from "
                f"{user.full_name} ({user.username})."
            ),
        }

    return {
        "question_type": "role_management",
        "action": action,
        "success": False,
        "answer": f"Unsupported role action: {action}.",
    }


def answer_user_query(
    db: Session,
    username: str,
):
    user = find_user_by_name(db, username)

    if user is None:
        return {
            "question_type": "user_query",
            "success": False,
            "answer": f"User '{username}' not found.",
        }

    return {
        "question_type": "user_query",
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
        },
        "answer": (
            f"User {user.full_name} ({user.username}) is "
            f"{'active' if user.is_active else 'inactive'}."
        ),
    }

def answer_user_status_query(db: Session, username: str):
    user = find_user_by_name(db, username)

    if user is None:
        return {
            "question_type": "user_status_query",
            "success": False,
            "answer": f"User '{username}' not found.",
        }

    status = "active" if user.is_active else "inactive"

    return {
        "question_type": "user_status_query",
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
        },
        "answer": f"User {user.full_name} ({user.username}) is {status}.",
    }

def perform_user_status_action(
    db: Session,
    action: str,
    username: str,
    actor_user_id: int,
):
    user = find_user_by_name(db, username)

    if user is None:
        return {
            "question_type": "user_status_action",
            "success": False,
            "answer": f"User '{username}' not found.",
        }

    if action == "activate":
        if user.is_active:
            return {
                "question_type": "user_status_action",
                "success": False,
                "answer": f"User {user.full_name} ({user.username}) is already active.",
            }

        user.is_active = True
        audit_action = "user.activate"
        details = f"Activated user '{user.username}'"

    elif action == "deactivate":
        if not user.is_active:
            return {
                "question_type": "user_status_action",
                "success": False,
                "answer": f"User {user.full_name} ({user.username}) is already inactive.",
            }

        user.is_active = False
        audit_action = "user.deactivate"
        details = f"Deactivated user '{user.username}'"

    else:
        return {
            "question_type": "user_status_action",
            "success": False,
            "answer": "Invalid user status action.",
        }

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        actor_user_id=actor_user_id,
        action=audit_action,
        resource_type="user",
        resource_id=user.id,
        target_user_id=user.id,
        details=details,
    )

    return {
        "question_type": "user_status_action",
        "success": True,
        "action": action,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
        },
        "answer": (
            f"User {user.full_name} ({user.username}) was "
            f"{'activated' if action == 'activate' else 'deactivated'} successfully."
        ),
    }

def answer_user_intelligence_query(
    db: Session,
    username: str,
):
    user = find_user_by_name(db, username)

    if user is None:
        return {
            "question_type": "user_intelligence",
            "success": False,
            "answer": f"User '{username}' not found.",
        }

    roles_statement = (
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    )

    roles = list(db.scalars(roles_statement).all())

    permissions_statement = (
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(
            UserRole.user_id == user.id,
            Permission.is_active.is_(True),
        )
        .distinct()
    )

    permissions = list(db.scalars(permissions_statement).all())

    return {
        "question_type": "user_intelligence",
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
        },
        "roles": [
            {
                "id": role.id,
                "name": role.name,
            }
            for role in roles
        ],
        "permissions": [
            {
                "id": permission.id,
                "name": permission.name,
                "description": permission.description,
            }
            for permission in permissions
        ],
        "answer": (
            f"User {user.full_name} ({user.username}) is "
            f"{'active' if user.is_active else 'inactive'}, "
            f"has {len(roles)} role(s), and "
            f"{len(permissions)} permission(s)."
        ),
    }


def answer_permission_query(
    db: Session,
    role_name: str,
):
    statement = (
        select(Permission)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .join(
            Role,
            Role.id == RolePermission.role_id,
        )
        .where(
            Role.name.ilike(role_name)
        )
        .distinct()
    )

    permissions = list(
        db.scalars(statement).all()
    )

    if not permissions:
        role_statement = (
            select(Role)
            .where(Role.name.ilike(role_name))
        )

        role = db.scalar(role_statement)

        if role is None:
            return {
                "question_type": "permission_query",
                "success": False,
                "answer": f"Role '{role_name}' not found.",
            }

    permission_details = [
        {
            "id": permission.id,
            "name": permission.name,
            "description": permission.description,
            "resource": permission.resource,
            "action": permission.action,
        }
        for permission in permissions
    ]

    answer = build_role_permission_summary(
        role_name,
        permissions,
    )

    return {
        "question_type": "permission_query",
        "success": True,
        "role_name": role_name,
        "permissions": permission_details,
        "answer": answer,
    }