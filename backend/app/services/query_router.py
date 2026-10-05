def classify_query(question: str) -> str:
    normalized = question.lower().strip()

    permission_patterns = [
        "what permissions do i have",
        "what are my permissions",
        "my permissions",
        "which permissions do i have",
        "show my permissions",
        "list my permissions",
    ]

    for pattern in permission_patterns:
        if pattern in normalized:
            return "my_permissions"

    login_activity_patterns = [
        "who logged in today",
        "who login today",
        "who logged in yesterday",
        "who login yesterday",
        "show today's login activity",
        "show todays login activity",
        "show today's logins",
        "show todays logins",
        "login activity today",
        "login activity yesterday",
    ]

    for pattern in login_activity_patterns:
        if pattern in normalized:
            return "login_activity"

    
    audit_date_patterns = [
        "audit logs for ",
        "audit activity for ",
        "audit logs on ",
        "audit activity on ",
    ]

    for pattern in audit_date_patterns:
        if pattern in normalized:
            return "today_audit_activity"

    audit_activity_patterns = [
        "show recent audit activity",
        "show recent audit logs",
        "show the latest audit logs",
        "show latest audit logs",
        "show audit activity",
        "show audit logs",
        "recent audit activity",
        "recent audit logs",
        "latest audit activity",
        "latest audit logs",
    ]

    for pattern in audit_activity_patterns:
        if pattern in normalized:
            return "recent_audit_activity"


    today_audit_patterns = [
        "what happened in the audit logs today",
        "what happened in audit logs today",
        "what audit activity happened today",
        "show today's audit activity",
        "show todays audit activity",
        "show today's audit logs",
        "show todays audit logs",
        "show me today's audit logs",
        "show me todays audit logs",
        "audit activity today",
        "audit logs today",
        "today audit logs",
    ]

    for pattern in today_audit_patterns:
        if pattern in normalized:
            return "today_audit_activity"

    permission_query_patterns = [
        "what permissions does ",
        "which permissions does ",
        "what permissions do ",
        "which permissions do ",
        "permissions of ",
    ]

    for pattern in permission_query_patterns:
        if normalized.startswith(pattern):
            return "permission_query"

    role_membership_patterns = [
        "does ",
    ]

    for pattern in role_membership_patterns:
        if normalized.startswith(pattern) and " have the " in normalized:
            return "role_membership"

    role_management_patterns = [
        "give ",
        "assign ",
        "add ",
        "remove ",
        "revoke ",
    ]

    for pattern in role_management_patterns:
        if normalized.startswith(pattern) and " role" in normalized:
            return "role_management"

    role_query_patterns = [
        "what roles does ",
        "which roles does ",
        "what role does ",
        "which role does ",
        "who has the ",
        "who have the ",
        "users with the ",
        "does ",
    ]

    for pattern in role_query_patterns:
        if normalized.startswith(pattern):
            if "role" in normalized:
                return "role_query"


    document_access_action_patterns = [
        "grant ",
        "give ",
        "revoke ",
        "remove ",
    ]

    for pattern in document_access_action_patterns:
        if normalized.startswith(pattern):
            if " access to " in normalized:
                return "document_access_action"


    access_management_patterns = [
        "who can grant access to",
        "who can revoke access to",
        "who can grant or revoke access to",
        "who can grant/revoke access to",
        "who can grant access",
        "who can revoke access",
        "who can grant or revoke access",
        "who can grant/revoke access",
    ]

    for pattern in access_management_patterns:
        if pattern in normalized:
            return "access_management"


    named_user_access_patterns = [
        "does ",
        "can ",
    ]

    for pattern in named_user_access_patterns:
        if normalized.startswith(pattern):
            if (
                " have access to " in normalized
                or " access " in normalized
                or " read " in normalized
            ):
                return "document_access_check"

    document_access_check_patterns = [
        "do i have access to",
        "does i have access to",
        "do i have permission to access",
        "does i have permission to access",
        "can i access",
        "can i read",
        "am i allowed to access",
    ]

    for pattern in document_access_check_patterns:
        if pattern in normalized:
            return "document_access_check"

    document_access_patterns = [
        "who has access to",
        "who can access",
        "who has permission to access",
        "who can read",
    ]

    for pattern in document_access_patterns:
        if pattern in normalized:
            return "document_access"


    user_intelligence_patterns = [
        "show me ",
        "show ",
        "get ",
        "tell me ",
    ]

    for pattern in user_intelligence_patterns:
        if normalized.startswith(pattern):
            if (
                "details" in normalized
                and "roles" in normalized
                and "permissions" in normalized
            ):
                return "user_intelligence"

    user_status_action_patterns = [
        "activate ",
        "deactivate ",
    ]

    for pattern in user_status_action_patterns:
        if normalized.startswith(pattern):
            return "user_status_action"

    user_status_patterns = [
        "is ",
        "is the ",
    ]

    for pattern in user_status_patterns:
        if normalized.startswith(pattern) and " active" in normalized:
            return "user_status_query"


    user_query_patterns = [
        "show me the details of ",
        "show details of ",
        "show user details for ",
        "get details of ",
        "what are the details of ",
        "tell me about user ",
    ]

    for pattern in user_query_patterns:
        if normalized.startswith(pattern):
            return "user_query"

    return "document_rag"


def extract_user_query(question: str) -> str | None:
    normalized = question.strip()

    patterns = [
        "show me the details of ",
        "show details of ",
        "show user details for ",
        "get details of ",
        "what are the details of ",
        "tell me about user ",
    ]

    lower_question = normalized.lower()

    for pattern in patterns:
        if lower_question.startswith(pattern):
            username = normalized[len(pattern):].strip().rstrip("?. ")
            return username

    return None

def extract_user_status_query(question: str) -> str | None:
    normalized = question.strip()
    lower_question = normalized.lower()

    patterns = [
        "is ",
        "is the ",
    ]

    for pattern in patterns:
        if lower_question.startswith(pattern) and " active" in lower_question:
            username = normalized[len(pattern):].strip()

            active_index = username.lower().find(" active")
            if active_index != -1:
                username = username[:active_index].strip()

            return username.rstrip("?. ")

    return None


def extract_document_name(question: str) -> str:
    normalized = question.strip()

    prefixes = [
        "Who has access to ",
        "who has access to ",
        "Who can access ",
        "who can access ",
        "Who has permission to access ",
        "who has permission to access ",
        "Who can read ",
        "who can read ",
    ]

    for prefix in prefixes:
        if normalized.startswith(prefix):
            return normalized[len(prefix):].strip().rstrip("?. ")

    return normalized


def extract_document_name_for_access_check(question: str) -> str:
    normalized = question.strip()

    prefixes = [
        "Do I have access to ",
        "do i have access to ",
        "Does I have access to ",
        "does i have access to ",
        "Do I have permission to access ",
        "do i have permission to access ",
        "Can I access ",
        "can i access ",
        "Can I read ",
        "can i read ",
        "Am I allowed to access ",
        "am i allowed to access ",
    ]

    for prefix in prefixes:
        if normalized.startswith(prefix):
            return normalized[len(prefix):].strip().rstrip("?. ")

    return normalized


def extract_document_name_for_access_management(question: str) -> str | None:
    normalized = question.strip()

    prefixes = [
        "Who can grant access to ",
        "who can grant access to ",
        "Who can revoke access to ",
        "who can revoke access to ",
        "Who can grant or revoke access to ",
        "who can grant or revoke access to ",
        "Who can grant/revoke access to ",
        "who can grant/revoke access to ",
    ]

    for prefix in prefixes:
        if normalized.startswith(prefix):
            return normalized[len(prefix):].strip().rstrip("?. ")

    return None


def extract_user_and_document_for_access_check(question: str) -> tuple[str | None, str]:
    normalized = question.strip()
    lower_question = normalized.lower()

    patterns = [
        ("does ", " have access to "),
        ("can ", " access "),
        ("can ", " read "),
    ]

    for prefix, separator in patterns:
        if lower_question.startswith(prefix):
            separator_index = lower_question.find(separator)

            if separator_index != -1:
                username = normalized[len(prefix):separator_index].strip()
                document_name = normalized[
                    separator_index + len(separator):
                ].strip().rstrip("?. ")

                return username, document_name

    return None, extract_document_name_for_access_check(question)


def extract_user_status_action(question: str) -> tuple[str | None, str | None]:
    normalized = question.strip()
    lower_question = normalized.lower()

    patterns = [
        ("activate ", "activate"),
        ("deactivate ", "deactivate"),
    ]

    for prefix, action in patterns:
        if lower_question.startswith(prefix):
            username = normalized[len(prefix):].strip().rstrip("?. ")

            if username:
                return action, username

    return None, None


def extract_document_access_action(question: str) -> tuple[str | None, str | None, str | None]:
    normalized = question.strip()
    lower_question = normalized.lower()

    patterns = [
        ("grant ", "grant"),
        ("give ", "grant"),
        ("revoke ", "revoke"),
        ("remove ", "revoke"),
    ]

    for prefix, action in patterns:
        if lower_question.startswith(prefix):
            remaining = normalized[len(prefix):].strip()
            lower_remaining = remaining.lower()

            # Format: Grant Bob access to rag_test.txt
            separator = " access to "
            separator_index = lower_remaining.find(separator)

            if separator_index != -1:
                username = remaining[:separator_index].strip()
                document_name = remaining[
                    separator_index + len(separator):
                ].strip().rstrip("?. ")

                return action, username, document_name

            # Format: Grant access to rag_test.txt for Bob
            separator = " access to "
            for_suffix = " for "

            if lower_remaining.startswith("access to ") and for_suffix in lower_remaining:
                document_part = remaining[len("access to "):]
                lower_document_part = document_part.lower()

                for_index = lower_document_part.rfind(for_suffix)

                if for_index != -1:
                    document_name = document_part[:for_index].strip().rstrip("?. ")
                    username = document_part[
                        for_index + len(for_suffix):
                    ].strip().rstrip("?. ")

                    return action, username, document_name
            
            if lower_remaining.startswith("access to ") and " from " in lower_remaining:
                document_part = remaining[len("access to "):]
                lower_document_part = document_part.lower()

                from_index = lower_document_part.rfind(" from ")

                if from_index != -1:
                    document_name = document_part[:from_index].strip().rstrip("?. ")
                    username = document_part[
                        from_index + len(" from "):
                    ].strip().rstrip("?. ")

                    return action, username, document_name

    return None, None, None


def extract_role_query(question: str) -> tuple[str | None, str | None]:
    normalized = question.strip()
    lower_question = normalized.lower()

    # Example: What roles does John have?
    for prefix in ["what roles does ", "which roles does ", "what role does ", "which role does "]:
        if lower_question.startswith(prefix):
            remaining = normalized[len(prefix):].strip()

            for suffix in [" have?", " have", "?"]:
                if remaining.lower().endswith(suffix):
                    remaining = remaining[:-len(suffix)].strip()
                    break

            return remaining, None

    # Example: Who has the Developer role?
    for prefix in ["who has the ", "who have the ", "users with the "]:
        if lower_question.startswith(prefix):
            remaining = normalized[len(prefix):].strip()

            for suffix in [" role?", " role", "?"]:
                if remaining.lower().endswith(suffix):
                    remaining = remaining[:-len(suffix)].strip()
                    break

            return None, remaining

    return None, None


def extract_role_membership_query(question: str) -> tuple[str | None, str | None]:
    normalized = question.strip()
    lower_question = normalized.lower()

    prefix = "does "
    separator = " have the "

    if lower_question.startswith(prefix):
        separator_index = lower_question.find(separator)

        if separator_index != -1:
            username = normalized[len(prefix):separator_index].strip()

            role_name = normalized[
                separator_index + len(separator):
            ].strip().rstrip("?. ")

            if role_name.lower().endswith(" role"):
                role_name = role_name[:-5].strip()

            return username, role_name

    return None, None

def extract_role_management_query(
    question: str,
) -> tuple[str | None, str | None, str | None]:
    normalized = question.strip()
    lower_question = normalized.lower()

    patterns = [
        ("give ", "grant"),
        ("assign ", "grant"),
        ("add ", "grant"),
        ("remove ", "remove"),
        ("revoke ", "remove"),
    ]

    for prefix, action in patterns:
        if lower_question.startswith(prefix):
            remaining = normalized[len(prefix):].strip()

            if action == "grant":
                separator = " the "
                separator_index = remaining.lower().find(separator)

                if separator_index != -1:
                    username = remaining[:separator_index].strip()
                    role_name = remaining[
                        separator_index + len(separator):
                    ].strip().rstrip("?. ")

                    if role_name.lower().endswith(" role"):
                        role_name = role_name[:-5].strip()

                    return action, username, role_name

            else:
                separator = " from the "
                separator_index = remaining.lower().find(separator)

                if separator_index != -1:
                    username = remaining[:separator_index].strip()
                    role_name = remaining[
                        separator_index + len(separator):
                    ].strip().rstrip("?. ")

                    if role_name.lower().endswith(" role"):
                        role_name = role_name[:-5].strip()

                    return action, username, role_name

    return None, None, None

def extract_user_intelligence_query(question: str) -> str | None:
    normalized = question.strip()
    lower_question = normalized.lower()

    patterns = [
        "show me ",
        "show ",
        "get ",
        "tell me ",
    ]

    for pattern in patterns:
        if lower_question.startswith(pattern):
            if (
                "details" in lower_question
                and "roles" in lower_question
                and "permissions" in lower_question
            ):
                remaining = normalized[len(pattern):].strip()

                details_index = remaining.lower().find(" details")
                if details_index != -1:
                    username_part = remaining[:details_index].strip()
                    username_part = username_part.rstrip("'s").strip()
                    return username_part

    return None


def extract_permission_query(question: str) -> str | None:
    normalized = question.strip()
    lower_question = normalized.lower()

    patterns = [
        "what permissions does ",
        "which permissions does ",
        "what permissions do ",
        "which permissions do ",
        "permissions of ",
    ]

    for pattern in patterns:
        if lower_question.startswith(pattern):
            role_name = normalized[len(pattern):].strip()

            if role_name.lower().endswith(" have"):
                role_name = role_name[:-5].strip()

            role_name = role_name.rstrip("?. ")

            if role_name.lower().endswith("role"):
                role_name = role_name[:-4].strip()

            return role_name

    return None