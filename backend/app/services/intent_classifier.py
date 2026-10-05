import json
from app.services.llm_service import client, MODEL_NAME


INTENTS = [
    "my_permissions",
    "login_activity",
    "recent_audit_activity",
    "today_audit_activity",
    "permission_query",
    "role_membership",
    "role_management",
    "role_query",
    "document_access_action",
    "access_management",
    "document_access_check",
    "document_access",
    "user_intelligence",
    "user_status_action",
    "user_status_query",
    "user_query",
    "document_rag",
    "chat_history_query",
    "general_conversation",
    "role_assignment_check",
]


def classify_query_with_llm(question: str) -> dict:

    prompt = f"""
You are the intent classifier for an Enterprise AI Assistant.

Your ONLY job is to understand what the user wants.

Do NOT:
- answer the user
- perform database operations
- invent information
- explain your decision
- return markdown

Return ONLY valid JSON.

============================================================
AVAILABLE INTENTS
============================================================

1. my_permissions

Use when the CURRENT logged-in user asks about their own
permissions or capabilities.

Examples:
- "What are my permissions?"
- "What can I do?"
- "What access do I have?"
- "What am I allowed to do?"

IMPORTANT:
"My permissions" means the CURRENT logged-in user.

------------------------------------------------------------

2. login_activity
   User asks who logged in or login activity.

3. recent_audit_activity
   User asks about recent audit activity.

4. today_audit_activity
   User asks about today's audit activity.

   If the user specifies a resource/category, extract it as
   resource_type.

   Supported resource types include:
   - role
   - user
   - document
   - auth
   - permission
   - code

   Examples:

   "Show me today's audit history"
   → intent: today_audit_activity
   → resource_type: null

   "Show me today's audit history on roles"
   → intent: today_audit_activity
   → resource_type: role

   "What role changes happened today?"
   → intent: today_audit_activity
   → resource_type: role

   "Show today's user audit history"
   → intent: today_audit_activity
   → resource_type: user

   "What document access changes happened today?"
   → intent: today_audit_activity
   → resource_type: document
------------------------------------------------------------

5. permission_query

Use when the user asks what permissions or capabilities
a ROLE has.

Examples:
- "What permissions does Developer have?"
- "What can the Developer role do?"
- "Show Developer permissions."
- "What is Developer allowed to do?"

For this intent:
role_name = the role being discussed.

------------------------------------------------------------

6. role_membership

Use when the user asks whether a USER CURRENTLY HAS
or currently belongs to a ROLE.

This is a READ-ONLY current-state question.

Examples:
- "Is John a Developer?"
- "Does John have the Developer role?"
- "Does John currently have Developer access?"
- "Is the Developer role assigned to John?"
- "Is John assigned to Developer?"
- "Does John belong to the Developer role?"

IMPORTANT:

These questions ask about the CURRENT STATE of the
assignment.

They do NOT request a role change.

------------------------------------------------------------

7. role_management

Use when the user wants the system to ACTUALLY CHANGE
a user's role assignment.

This includes:
- assigning a role
- giving a role
- adding a role
- granting a role
- removing a role
- revoking a role
- taking a role away

ACTION NORMALIZATION:

- give -> grant
- assign -> grant
- add -> grant
- grant -> grant
- remove -> remove
- revoke -> remove
- take away -> remove

The action MUST be either:

"grant"

or

"remove"

NEVER return:
- "add"
- "give"
- "assign"
- "revoke"

Examples:

"Give John the Developer role."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: grant

"Assign Developer to John."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: grant

"Add John to the Developer role."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: grant

"Grant John the Developer role."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: grant

"Can we give John the Developer role?"

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: grant

"Can I assign Developer to John?"

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: grant

"Please give John Developer access."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: grant

"Remove Developer from John."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: remove

"Revoke Developer from John."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: remove

"Take the Developer role away from John."

-> intent: role_management
-> username: John
-> role_name: Developer
-> action: remove


IMPORTANT DISTINCTION:

The presence of words such as:

"Can"
"Could"
"Can we"
"Can I"
"Please"

does NOT automatically mean role_assignment_check.

You must determine what the user is asking.

If the user is asking to PERFORM the assignment:

"Can we give John Developer?"
"Can I assign Developer to John?"
"Can you give John Developer?"
"Could you add John to Developer?"

-> role_management
-> action = grant


------------------------------------------------------------

8. role_assignment_check

Use ONLY when the user is asking whether a role assignment
is ALLOWED, PERMITTED, AUTHORIZED, or POSSIBLE according
to system rules, authorization, policy, or eligibility.

This is READ-ONLY.

The user is NOT asking the system to perform the assignment.

For this intent:

action MUST be:

"check"

Examples:

"Is John allowed to get the Developer role?"

-> intent: role_assignment_check
-> username: John
-> role_name: Developer
-> action: check

"Is John permitted to have the Developer role?"

-> intent: role_assignment_check
-> username: John
-> role_name: Developer
-> action: check

"Is John authorized to receive the Developer role?"

-> intent: role_assignment_check
-> username: John
-> role_name: Developer
-> action: check

"Are we allowed to assign Developer to John?"

-> intent: role_assignment_check
-> username: John
-> role_name: Developer
-> action: check

"Is John eligible for the Developer role?"

-> intent: role_assignment_check
-> username: John
-> role_name: Developer
-> action: check

"According to policy, can John be assigned Developer?"

-> intent: role_assignment_check
-> username: John
-> role_name: Developer
-> action: check


IMPORTANT DISTINCTION:

Compare these carefully:

"Can we GIVE John the Developer role?"

This asks to PERFORM the assignment.

-> role_management
-> action = grant


"Is John ALLOWED to GET the Developer role?"

This asks whether the assignment is PERMITTED.

-> role_assignment_check
-> action = check


"Can I ASSIGN Developer to John?"

This asks to PERFORM the assignment.

-> role_management
-> action = grant


"Is John AUTHORIZED to receive Developer?"

This asks about authorization.

-> role_assignment_check
-> action = check


"Does John HAVE the Developer role?"

This asks about current membership.

-> role_membership


------------------------------------------------------------

9. role_query

Use when the user asks about roles or role membership
in a general way.

Examples:
- "What role does John have?"
- "Which roles does John have?"
- "Who has the Developer role?"
- "Who belongs to Developer?"

------------------------------------------------------------

10. document_access_action

Use when the user wants to ACTUALLY GRANT or REVOKE
access to a document.

Actions:

- grant
- revoke

Examples:

"Give John access to HR Policy."

-> intent: document_access_action
-> username: John
-> document_name: HR Policy
-> action: grant

"Grant John access to HR Policy."

-> intent: document_access_action
-> username: John
-> document_name: HR Policy
-> action: grant

"Remove John's access to HR Policy."

-> intent: document_access_action
-> username: John
-> document_name: HR Policy
-> action: revoke

"Revoke John's access to HR Policy."

-> intent: document_access_action
-> username: John
-> document_name: HR Policy
-> action: revoke

------------------------------------------------------------

11. access_management

Use when the user asks WHO HAS ACCESS to a document.

This is a READ-ONLY query.

Example:

"Who has access to HR Policy?"

-> intent: access_management
-> document_name: HR Policy

------------------------------------------------------------

12. document_access_check

Use when the user asks whether a user CURRENTLY CAN ACCESS
a document.

Examples:

"Can John access HR Policy?"

"Does John have access to HR Policy?"

"Is John allowed to access HR Policy?"

"Do I have access to HR Policy?"

Action:

"check"

------------------------------------------------------------

13. document_access

Use for general document access information that does not
fit the specific document access action/check intents.

------------------------------------------------------------

14. user_intelligence

Use when the user asks detailed information about a user.

Examples:
- "Tell me about John."
- "Show me John's details."
- "Show John's permissions."
- "Give me information about John."

IMPORTANT:

"John's permissions" is NOT my_permissions.

The current logged-in user's permissions are only
my_permissions.

------------------------------------------------------------

15. user_status_action

Use when the user wants to ACTUALLY CHANGE a user's
active/inactive status.

Actions:

- activate
- deactivate

Examples:

"Activate John."

-> intent: user_status_action
-> username: John
-> action: activate

"Deactivate John."

-> intent: user_status_action
-> username: John
-> action: deactivate

------------------------------------------------------------

16. user_status_query

Use when the user asks whether a user is currently
active or inactive.

Examples:
- "Is John active?"
- "Is John inactive?"
- "What's John's current status?"

Action:

"check"

------------------------------------------------------------

17. user_query

Use when the user asks basic information about a user.

Examples:
- "What is John's username?"
- "Show John's user information."
- "What is John's full name?"

------------------------------------------------------------

18. document_rag

Use when the user asks questions that should be answered
from company documents, policies, knowledge, code, or
other indexed enterprise content.

Examples:
- "What is the company leave policy?"
- "Explain the HR policy."
- "What does our security policy say?"
- "How does our authentication code work?"

------------------------------------------------------------

19. general_conversation

Use for normal conversation that does not require
enterprise data.

Examples:
- "Hello"
- "How are you?"
- "Good morning"
- "Thank you"
- "What can you help me with?"

------------------------------------------------------------

20. IMPORTANT — CHAT HISTORY INTENT

Use "chat_history_query" when the user is asking about previous
conversation messages with this AI assistant.

This means the user wants information from the conversation history
stored for their account, NOT information directly from the enterprise
database.

Examples:

"Can I get details on our previous chats?"
→ chat_history_query

"What was my previous question?"
→ chat_history_query

"What did we discuss earlier?"
→ chat_history_query

"What did we discuss about John?"
→ chat_history_query

"What did we talk about regarding permissions?"
→ chat_history_query

"Show me our conversation history"
→ chat_history_query

"What did you tell me earlier?"
→ chat_history_query

"What was the last thing we discussed?"
→ chat_history_query

"Continue from our previous discussion"
→ chat_history_query

Important distinction:

"What did we discuss about John?"
→ chat_history_query

"Who is John?"
→ user_intelligence

"What roles does John have?"
→ role_membership

"What permissions does John have?"
→ user_intelligence or the appropriate enterprise intent

If the user refers to something we previously discussed using phrases
such as:
- previous
- earlier
- before
- last question
- previous question
- previous chat
- past chat
- conversation history
- what did we discuss
- what did we talk about
- what did you tell me
- continue from before

prefer "chat_history_query" when the question is about the conversation
with the AI assistant.

For audit-related intents, extract resource_type.

    Allowed values:
    - role
    - user
    - document
    - auth
    - permission
    - code

    Examples:
    "Show me today's audit history on roles"
    → today_audit_activity, resource_type: role

    "Show me today's audit history"
    → today_audit_activity, resource_type: null

    "What role changes happened today?"
    → today_audit_activity, resource_type: role


chat_history_query:
Questions about the user's previous conversation with this AI assistant.
This retrieves information from stored chat messages.

general_conversation:
Normal greetings, casual conversation, explanations, and questions
that do not require enterprise data or previous chat history.

============================================================
IMPORTANT ENTITY RULES
============================================================

- A role name such as Developer goes into role_name.
- A person's name such as John goes into username.
- A document name such as HR Policy goes into document_name.
- Do not confuse a role with a user.
- Do not invent missing entities.
- If an entity is not present, return null.

============================================================
IMPORTANT ROLE DECISION RULE
============================================================

When deciding between role_membership,
role_management, and role_assignment_check, determine
the user's INTENTION rather than looking only at words.

A. CURRENT STATE:

"Does John have Developer?"
"Is Developer assigned to John?"
"Is John a Developer?"

-> role_membership


B. PERFORM A CHANGE:

"Give John Developer."
"Can we give John Developer?"
"Can I assign Developer to John?"
"Please add John to Developer."

-> role_management
-> action = grant


C. ASK WHETHER IT IS PERMITTED:

"Is John allowed to have Developer?"
"Is John authorized for Developer?"
"Is John permitted to receive Developer?"
"According to policy, can John be assigned Developer?"

-> role_assignment_check
-> action = check

============================================================
RETURN FORMAT
============================================================

Return exactly this structure:

{{
    "intent": "one_of_available_intents",
    "username": null,
    "role_name": null,
    "document_name": null,
    "action": null
}}

topic:
For chat_history_query, extract the main person, role, document,
permission, or subject the user is asking about.

Examples:

"What did we discuss about John?"
→ topic: "John"

"What did we discuss about permissions?"
→ topic: "permissions"

"What did we discuss about the Developer role?"
→ topic: "Developer role"

"What did we discuss about the HR Policy?"
→ topic: "HR Policy"

"What was my previous question?"
→ topic: null

"What did we discuss earlier?"
→ topic: null

============================================================
CLASSIFICATION EXAMPLES
============================================================

Question:
"What permissions does Developer have?"

{{
    "intent": "permission_query",
    "username": null,
    "role_name": "Developer",
    "document_name": null,
    "action": null
}}

Question:
"What can a Developer role do?"

{{
    "intent": "permission_query",
    "username": null,
    "role_name": "Developer",
    "document_name": null,
    "action": null
}}

Question:
"What are my permissions?"

{{
    "intent": "my_permissions",
    "username": null,
    "role_name": null,
    "document_name": null,
    "action": null
}}

Question:
"Show me John's permissions."

{{
    "intent": "user_intelligence",
    "username": "John",
    "role_name": null,
    "document_name": null,
    "action": null
}}

Question:
"Is John a Developer?"

{{
    "intent": "role_membership",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": null
}}

Question:
"Does John currently have Developer access?"

{{
    "intent": "role_membership",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": null
}}

Question:
"Is the Developer role assigned to John?"

{{
    "intent": "role_membership",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": null
}}

Question:
"Give John the Developer role."

{{
    "intent": "role_management",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "grant"
}}

Question:
"Assign Developer to John."

{{
    "intent": "role_management",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "grant"
}}

Question:
"Can we give John the Developer role?"

{{
    "intent": "role_management",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "grant"
}}

Question:
"Can I assign Developer to John?"

{{
    "intent": "role_management",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "grant"
}}

Question:
"Could you add John to the Developer role?"

{{
    "intent": "role_management",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "grant"
}}

Question:
"Remove Developer from John."

{{
    "intent": "role_management",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "remove"
}}

Question:
"Revoke Developer from John."

{{
    "intent": "role_management",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "remove"
}}

Question:
"Is John allowed to get the Developer role?"

{{
    "intent": "role_assignment_check",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "check"
}}

Question:
"Is John authorized to receive the Developer role?"

{{
    "intent": "role_assignment_check",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "check"
}}

Question:
"Are we allowed to assign Developer to John?"

{{
    "intent": "role_assignment_check",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "check"
}}

Question:
"According to policy, can John be assigned Developer?"

{{
    "intent": "role_assignment_check",
    "username": "John",
    "role_name": "Developer",
    "document_name": null,
    "action": "check"
}}

Question:
"Can John access HR Policy?"

{{
    "intent": "document_access_check",
    "username": "John",
    "role_name": null,
    "document_name": "HR Policy",
    "action": "check"
}}

Question:
"Can I access HR Policy?"

{{
    "intent": "document_access_check",
    "username": null,
    "role_name": null,
    "document_name": "HR Policy",
    "action": "check"
}}

Question:
"Give John access to HR Policy."

{{
    "intent": "document_access_action",
    "username": "John",
    "role_name": null,
    "document_name": "HR Policy",
    "action": "grant"
}}

Question:
"Remove John's access to HR Policy."

{{
    "intent": "document_access_action",
    "username": "John",
    "role_name": null,
    "document_name": "HR Policy",
    "action": "revoke"
}}

Question:
"Who has access to HR Policy?"

{{
    "intent": "access_management",
    "username": null,
    "role_name": null,
    "document_name": "HR Policy",
    "action": null
}}

Question:
"Deactivate John."

{{
    "intent": "user_status_action",
    "username": "John",
    "role_name": null,
    "document_name": null,
    "action": "deactivate"
}}

Question:
"Is John active?"

{{
    "intent": "user_status_query",
    "username": "John",
    "role_name": null,
    "document_name": null,
    "action": "check"
}}

Question:
"Who logged in today?"

{{
    "intent": "login_activity",
    "username": null,
    "role_name": null,
    "document_name": null,
    "action": null
}}

Question:
"Hello, how are you?"

{{
    "intent": "general_conversation",
    "username": null,
    "role_name": null,
    "document_name": null,
    "action": null
}}

============================================================
USER QUESTION
============================================================

{question}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "intent": "general_conversation",
            "username": None,
            "role_name": None,
            "document_name": None,
            "action": None,
            "resource_type": None,
            "topic": None,
        }

    intent = result.get("intent")

    if intent not in INTENTS:
        intent = "general_conversation"

    username = result.get("username")
    role_name = result.get("role_name")
    document_name = result.get("document_name")
    action = result.get("action")
    resource_type = result.get("resource_type")
    topic = result.get("topic")


    # =========================================================
    # DETERMINISTIC ACTION NORMALIZATION
    # =========================================================

    if intent == "role_management":

        if action in {"give", "assign", "add", "grant"}:
            action = "grant"

        elif action in {"remove", "revoke", "take away"}:
            action = "remove"

        else:
            action = None


    elif intent == "role_assignment_check":

        action = "check"


    elif intent == "document_access_action":

        if action in {"give", "assign", "add", "grant"}:
            action = "grant"

        elif action in {"remove", "revoke", "take away"}:
            action = "revoke"

        else:
            action = None


    elif intent == "user_status_action":

        if action in {"activate", "enable"}:
            action = "activate"

        elif action in {"deactivate", "disable"}:
            action = "deactivate"

        else:
            action = None


    elif intent in {
        "document_access_check",
        "user_status_query",
    }:

        action = "check"


    # =========================================================
    # DETERMINISTIC AUDIT RESOURCE TYPE
    # =========================================================

    question_lower = question.lower()

    if intent in {
        "today_audit_activity",
        "recent_audit_activity",
    }:

        if any(word in question_lower for word in [
            "role",
            "roles",
            "role changes",
            "role history"
        ]):
            resource_type = "role"

        elif any(word in question_lower for word in [
            "user",
            "users",
            "user changes",
            "user history"
        ]):
            resource_type = "user"

        elif any(word in question_lower for word in [
            "document",
            "documents",
            "document access"
        ]):
            resource_type = "document"

        elif any(word in question_lower for word in [
            "permission",
            "permissions"
        ]):
            resource_type = "permission"

        elif any(word in question_lower for word in [
            "authentication",
            "auth",
            "login",
            "logins"
        ]):
            resource_type = "auth"

        elif any(word in question_lower for word in [
            "code",
            "codes",
            "code changes"
        ]):
            resource_type = "code"


    # =========================================================
    # DETERMINISTIC AUDIT USERNAME EXTRACTION
    # =========================================================

    if intent in {
        "today_audit_activity",
        "recent_audit_activity",
        "login_activity",
    } and not username:

        known_non_user_words = {
            "show",
            "me",
            "give",
            "get",
            "display",
            "what",
            "who",
            "was",
            "were",
            "happened",
            "on",
            "for",
            "the",
            "today",
            "yesterday",
            "recent",
            "audit",
            "audits",
            "history",
            "activity",
            "activities",
            "login",
            "logins",
            "logged",
            "in",
            "role",
            "roles",
            "user",
            "users",
            "document",
            "documents",
            "permission",
            "permissions",
            "auth",
            "authentication",
            "code",
            "changes",
            "todays",
            "today's",
            "john's",
            "alice's",
            "yesterday's",
            "recently",
        }

        words = (
            question_lower
            .replace("?", "")
            .split()
        )

        for word in words:

            if word in known_non_user_words:
                continue

            # Ignore common time expressions
            if word in {
                "todays",
                "today's",
                "yesterdays",
                "yesterday's",
                "recently",
            }:
                continue

            # Ignore possessive expressions
            if word.endswith("'s"):
                continue

            if word.isalnum():
                username = word
                break

    # =========================================================
    # FINAL STRUCTURED RESULT
    # =========================================================

    return {
            "intent": intent,
            "username": username,
            "role_name": role_name,
            "document_name": document_name,
            "action": action,
            "resource_type": resource_type,
            "topic": topic,
    }