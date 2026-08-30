import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AlreadyInHouseholdError,
    HouseholdInviteNotFoundError,
    InvalidHouseholdInviteError,
    InvitedUserNotFoundError,
    NotInHouseholdError,
)
from app.models.household import Household, HouseholdInvite, HouseholdMember, InviteStatus
from app.repositories import household_repository, user_repository
from app.schemas.household import HouseholdMemberRead, HouseholdRead, InviteRead


def _build_household_read(db: Session, household: Household) -> HouseholdRead:
    members = []
    for member in household_repository.list_members(db, household.id):
        user = user_repository.get_by_id(db, member.user_id)
        assert user is not None  # membership só existe enquanto o user existir (FK CASCADE)
        members.append(
            HouseholdMemberRead(
                user_id=member.user_id,
                name=user.name,
                email=user.email,
                joined_at=member.joined_at,
                is_creator=member.user_id == household.created_by,
            )
        )
    return HouseholdRead(
        id=household.id,
        name=household.name,
        created_by=household.created_by,
        created_at=household.created_at,
        members=members,
    )


def _build_invite_read(db: Session, invite: HouseholdInvite) -> InviteRead:
    household = household_repository.get_household(db, invite.household_id)
    invited = user_repository.get_by_id(db, invite.invited_user_id)
    inviter = user_repository.get_by_id(db, invite.invited_by)
    assert invited is not None
    return InviteRead(
        id=invite.id,
        household_id=invite.household_id,
        household_name=household.name if household is not None else "(agregado removido)",
        invited_user_email=invited.email,
        invited_user_name=invited.name,
        invited_by_name=inviter.name if inviter is not None else "(utilizador removido)",
        status=invite.status,
        created_at=invite.created_at,
        responded_at=invite.responded_at,
    )


def _require_membership(db: Session, user_id: uuid.UUID) -> HouseholdMember:
    membership = household_repository.get_membership_for_user(db, user_id)
    if membership is None:
        raise NotInHouseholdError
    return membership


# --- agregado ------------------------------------------------------------


def get_my_household(db: Session, *, user_id: uuid.UUID) -> HouseholdRead:
    membership = _require_membership(db, user_id)
    household = household_repository.get_household(db, membership.household_id)
    assert household is not None
    return _build_household_read(db, household)


def create_household(db: Session, *, user_id: uuid.UUID, name: str) -> HouseholdRead:
    if household_repository.get_membership_for_user(db, user_id) is not None:
        raise AlreadyInHouseholdError
    household = household_repository.create_household(db, name=name, created_by=user_id)
    household_repository.create_member(db, household_id=household.id, user_id=user_id)
    db.flush()
    return _build_household_read(db, household)


def leave_household(db: Session, *, user_id: uuid.UUID) -> None:
    membership = _require_membership(db, user_id)
    household_id = membership.household_id
    household_repository.delete_member(db, membership)
    db.flush()

    # Sem membros, apaga o agregado (convites pendentes vão em cascata).
    if household_repository.count_members(db, household_id) == 0:
        household = household_repository.get_household(db, household_id)
        if household is not None:
            household_repository.delete_household(db, household)
            db.flush()


# --- convites ----------------------------------------------------------


def invite_member(db: Session, *, user_id: uuid.UUID, email: str) -> InviteRead:
    membership = _require_membership(db, user_id)

    invited = user_repository.get_by_email(db, email)
    if invited is None:
        raise InvitedUserNotFoundError
    if invited.id == user_id:
        raise InvalidHouseholdInviteError("Não te podes convidar a ti próprio.")

    invited_membership = household_repository.get_membership_for_user(db, invited.id)
    if invited_membership is not None:
        if invited_membership.household_id == membership.household_id:
            raise InvalidHouseholdInviteError("Esta pessoa já é membro do agregado.")
        raise InvalidHouseholdInviteError("Esta pessoa já pertence a outro agregado familiar.")

    already_pending = household_repository.get_pending_invite(
        db, household_id=membership.household_id, invited_user_id=invited.id
    )
    if already_pending is not None:
        raise InvalidHouseholdInviteError("Já existe um convite pendente para esta pessoa.")

    invite = household_repository.create_invite(
        db,
        household_id=membership.household_id,
        invited_user_id=invited.id,
        invited_by=user_id,
    )
    db.flush()
    return _build_invite_read(db, invite)


def list_sent_invites(db: Session, *, user_id: uuid.UUID) -> list[InviteRead]:
    membership = _require_membership(db, user_id)
    return [
        _build_invite_read(db, invite)
        for invite in household_repository.list_pending_invites_for_household(
            db, membership.household_id
        )
    ]


def cancel_invite(db: Session, *, user_id: uuid.UUID, invite_id: uuid.UUID) -> None:
    membership = _require_membership(db, user_id)
    invite = household_repository.get_invite(db, invite_id)
    if invite is None or invite.household_id != membership.household_id:
        raise HouseholdInviteNotFoundError
    if invite.status != InviteStatus.PENDING:
        raise InvalidHouseholdInviteError("Este convite já foi respondido.")
    invite.status = InviteStatus.CANCELLED
    invite.responded_at = datetime.now(UTC)
    db.flush()


def list_received_invites(db: Session, *, user_id: uuid.UUID) -> list[InviteRead]:
    return [
        _build_invite_read(db, invite)
        for invite in household_repository.list_pending_invites_for_user(db, user_id)
    ]


def _own_pending_invite(
    db: Session, user_id: uuid.UUID, invite_id: uuid.UUID
) -> HouseholdInvite:
    invite = household_repository.get_invite(db, invite_id)
    if invite is None or invite.invited_user_id != user_id:
        raise HouseholdInviteNotFoundError
    if invite.status != InviteStatus.PENDING:
        raise InvalidHouseholdInviteError("Este convite já foi respondido.")
    return invite


def accept_invite(db: Session, *, user_id: uuid.UUID, invite_id: uuid.UUID) -> HouseholdRead:
    invite = _own_pending_invite(db, user_id, invite_id)
    if household_repository.get_membership_for_user(db, user_id) is not None:
        raise AlreadyInHouseholdError
    household = household_repository.get_household(db, invite.household_id)
    if household is None:
        raise HouseholdInviteNotFoundError

    invite.status = InviteStatus.ACCEPTED
    invite.responded_at = datetime.now(UTC)
    household_repository.create_member(db, household_id=household.id, user_id=user_id)

    # Outros convites pendentes deixam de fazer sentido: só se pertence a um agregado.
    for other in household_repository.list_pending_invites_for_user(db, user_id):
        if other.id != invite.id:
            other.status = InviteStatus.CANCELLED
            other.responded_at = datetime.now(UTC)

    db.flush()
    return _build_household_read(db, household)


def decline_invite(db: Session, *, user_id: uuid.UUID, invite_id: uuid.UUID) -> None:
    invite = _own_pending_invite(db, user_id, invite_id)
    invite.status = InviteStatus.DECLINED
    invite.responded_at = datetime.now(UTC)
    db.flush()
