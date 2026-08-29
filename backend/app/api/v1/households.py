import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    AlreadyInHouseholdError,
    HouseholdInviteNotFoundError,
    InvalidHouseholdInviteError,
    InvitedUserNotFoundError,
    NotInHouseholdError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.household import HouseholdCreate, HouseholdRead, InviteCreate, InviteRead
from app.services import household_service

router = APIRouter(prefix="/households", tags=["households"])

_NOT_IN_HOUSEHOLD = HTTPException(
    status.HTTP_404_NOT_FOUND, "Não pertences a nenhum agregado familiar."
)


@router.post("", response_model=HouseholdRead, status_code=status.HTTP_201_CREATED)
def create_household(
    payload: HouseholdCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HouseholdRead:
    try:
        household = household_service.create_household(
            db, user_id=current_user.id, name=payload.name
        )
    except AlreadyInHouseholdError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Já pertences a um agregado familiar."
        ) from exc

    db.commit()
    return household


@router.get("/me", response_model=HouseholdRead)
def get_my_household(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> HouseholdRead:
    try:
        return household_service.get_my_household(db, user_id=current_user.id)
    except NotInHouseholdError as exc:
        raise _NOT_IN_HOUSEHOLD from exc


@router.post("/me/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_household(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    try:
        household_service.leave_household(db, user_id=current_user.id)
    except NotInHouseholdError as exc:
        raise _NOT_IN_HOUSEHOLD from exc

    db.commit()


@router.post(
    "/me/invites", response_model=InviteRead, status_code=status.HTTP_201_CREATED
)
def invite_member(
    payload: InviteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InviteRead:
    try:
        invite = household_service.invite_member(
            db, user_id=current_user.id, email=payload.email
        )
    except NotInHouseholdError as exc:
        raise _NOT_IN_HOUSEHOLD from exc
    except InvitedUserNotFoundError as exc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Não existe nenhum utilizador com esse email."
        ) from exc
    except InvalidHouseholdInviteError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, exc.message) from exc

    db.commit()
    return invite


@router.get("/me/invites", response_model=list[InviteRead])
def list_sent_invites(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[InviteRead]:
    try:
        return household_service.list_sent_invites(db, user_id=current_user.id)
    except NotInHouseholdError as exc:
        raise _NOT_IN_HOUSEHOLD from exc


@router.delete("/me/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_invite(
    invite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        household_service.cancel_invite(db, user_id=current_user.id, invite_id=invite_id)
    except NotInHouseholdError as exc:
        raise _NOT_IN_HOUSEHOLD from exc
    except HouseholdInviteNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Convite não encontrado.") from exc
    except InvalidHouseholdInviteError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, exc.message) from exc

    db.commit()


@router.get("/invites", response_model=list[InviteRead])
def list_received_invites(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[InviteRead]:
    return household_service.list_received_invites(db, user_id=current_user.id)


@router.post("/invites/{invite_id}/accept", response_model=HouseholdRead)
def accept_invite(
    invite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HouseholdRead:
    try:
        household = household_service.accept_invite(
            db, user_id=current_user.id, invite_id=invite_id
        )
    except HouseholdInviteNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Convite não encontrado.") from exc
    except AlreadyInHouseholdError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Já pertences a um agregado familiar."
        ) from exc
    except InvalidHouseholdInviteError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, exc.message) from exc

    db.commit()
    return household


@router.post("/invites/{invite_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
def decline_invite(
    invite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        household_service.decline_invite(db, user_id=current_user.id, invite_id=invite_id)
    except HouseholdInviteNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Convite não encontrado.") from exc
    except InvalidHouseholdInviteError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, exc.message) from exc

    db.commit()
