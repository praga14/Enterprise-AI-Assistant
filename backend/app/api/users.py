from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    PasswordUpdate,
    SelfPasswordUpdate,
)
from app.services.user_service import (
    create_user,
    deactivate_user,
    get_user_by_id,
    get_users,
    reactivate_user,
    update_user,
    update_user_password,
    change_own_password,
)
from app.services.access_service import get_user_permissions
from app.services.user_role_service import (
    get_user_roles,
    remove_role_from_user,
)
from app.core.dependencies import (
    get_current_user,
    require_permission,
)
from app.models.user import User

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.post("/", response_model=UserResponse)
def create_user_endpoint(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("user.manage")
    ),
):
    return create_user(
    db=db,
    user_data=data,
    actor_user_id=current_user.id,
    )


@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("user.read")
    ),
):
    return get_users(db)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user(
        db=db,
        user=current_user,
        user_data=user_data,
        actor_user_id=current_user.id,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("user.read")
    ),
):
    user = get_user_by_id(db, user_id)

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user

@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("user.manage")
    ),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return update_user(
    db=db,
    user=user,
    user_data=user_data,
    actor_user_id=current_user.id,
    )


@router.patch("/me/password")
def update_my_password_endpoint(
    password_data: SelfPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        change_own_password(
            db=db,
            user=current_user,
            password_data=password_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "message": "Password updated successfully",
        "user_id": current_user.id,
    }



@router.patch("/{user_id}/password")
def update_user_password_endpoint(
    user_id: int,
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("user.manage")
    ),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    update_user_password(
        db=db,
        user=user,
        password_data=password_data,
        actor_user_id=current_user.id,
    )

    return {
        "message": "Password updated successfully",
        "user_id": user.id,
    }



@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("user.manage")
    ),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return deactivate_user(
    db=db,
    user=user,
    actor_user_id=current_user.id,
    )


@router.patch(
    "/{user_id}/reactivate",
    response_model=UserResponse,
)
def reactivate_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("user.manage")
    ),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return reactivate_user(
    db=db,
    user=user,
    actor_user_id=current_user.id,
    )

@router.get("/{user_id}/permissions")
def get_user_permissions_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("permission.read")
    ),
):
    try:
        permissions = get_user_permissions(db, user_id)
        return permissions
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.get("/{user_id}/roles")
def get_user_roles_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("role.read")
    ),
):
    try:
        roles = get_user_roles(db, user_id)
        return roles
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.delete("/{user_id}/roles/{role_id}")
def remove_role_from_user_endpoint(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("access.grant")
    ),
):
    try:
        remove_role_from_user(
            db=db,
            user_id=user_id,
            role_id=role_id,
            actor_user_id=current_user.id,
        )

        return {
            "message": "Role removed from user successfully",
            "user_id": user_id,
            "role_id": role_id,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )