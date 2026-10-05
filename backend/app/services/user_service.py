from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordUpdate, SelfPasswordUpdate
from app.core.security import hash_password, verify_password
from app.services.audit_log_service import create_audit_log


def create_user(
    db: Session,
    user_data: UserCreate,
    actor_user_id: int,
) -> User:
    user = User(
        employee_id=user_data.employee_id,
        username=user_data.username,
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        department=user_data.department,
    )

    db.add(user)

    # Generate the new user's ID before creating the audit record.
    db.flush()

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="CREATE_USER",
        resource_type="USER",
        resource_id=user.id,
        target_user_id=user.id,
        details=f"User '{user.username}' created",
    )

    db.commit()
    db.refresh(user)

    return user

def get_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def update_user(
    db: Session,
    user: User,
    user_data: UserUpdate,
    actor_user_id: int,
) -> User:
    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.department is not None:
        user.department = user_data.department

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="UPDATE_USER",
        resource_type="USER",
        resource_id=user.id,
        target_user_id=user.id,
        details=f"User '{user.username}' profile updated",
    )

    db.commit()
    db.refresh(user)

    return user


def deactivate_user(
    db: Session,
    user: User,
    actor_user_id: int,
) -> User:
    user.is_active = False

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="DEACTIVATE_USER",
        resource_type="USER",
        resource_id=user.id,
        target_user_id=user.id,
        details=f"User '{user.username}' deactivated",
    )

    db.commit()
    db.refresh(user)

    return user

def reactivate_user(
    db: Session,
    user: User,
    actor_user_id: int,
) -> User:
    user.is_active = True

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="REACTIVATE_USER",
        resource_type="USER",
        resource_id=user.id,
        target_user_id=user.id,
        details=f"User '{user.username}' reactivated",
    )

    db.commit()
    db.refresh(user)

    return user


def update_user_password(
    db: Session,
    user: User,
    password_data: PasswordUpdate,
    actor_user_id: int,
) -> User:

    if not verify_password(
        password_data.current_password,
        user.password_hash,
    ):
        raise ValueError("Current password is incorrect")

    user.password_hash = hash_password(
        password_data.new_password
    )

    create_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="UPDATE_PASSWORD",
        resource_type="USER",
        resource_id=user.id,
        target_user_id=user.id,
        details=f"Password updated for user '{user.username}'",
    )

    db.commit()
    db.refresh(user)

    return user


def change_own_password(
    db: Session,
    user: User,
    password_data: SelfPasswordUpdate,
) -> User:
    if not verify_password(
        password_data.current_password,
        user.password_hash,
    ):
        raise ValueError("Current password is incorrect")

    user.password_hash = hash_password(
        password_data.new_password
    )

    create_audit_log(
        db,
        actor_user_id=user.id,
        action="UPDATE_PASSWORD",
        resource_type="USER",
        resource_id=user.id,
        target_user_id=user.id,
        details=f"Password updated for user '{user.username}'",
    )

    db.commit()
    db.refresh(user)

    return user