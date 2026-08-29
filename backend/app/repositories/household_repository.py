import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.household import Household, HouseholdInvite, HouseholdMember, InviteStatus

# --- households -------------------------------------------------------------


def create_household(db: Session, *, name: str, created_by: uuid.UUID) -> Household:
    household = Household(name=name, created_by=created_by)
    db.add(household)
    db.flush()
    return household


def get_household(db: Session, household_id: uuid.UUID) -> Household | None:
    return db.get(Household, household_id)


def delete_household(db: Session, household: Household) -> None:
    db.delete(household)


# --- members ---------------------------------------------------------------


def get_membership_for_user(db: Session, user_id: uuid.UUID) -> HouseholdMember | None:
    return db.scalar(select(HouseholdMember).where(HouseholdMember.user_id == user_id))


def list_members(db: Session, household_id: uuid.UUID) -> list[HouseholdMember]:
    return list(
        db.scalars(
            select(HouseholdMember)
            .where(HouseholdMember.household_id == household_id)
            .order_by(HouseholdMember.joined_at)
        )
    )


def member_user_ids(db: Session, household_id: uuid.UUID) -> list[uuid.UUID]:
    return list(
        db.scalars(
            select(HouseholdMember.user_id).where(HouseholdMember.household_id == household_id)
        )
    )


def count_members(db: Session, household_id: uuid.UUID) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(HouseholdMember)
            .where(HouseholdMember.household_id == household_id)
        )
        or 0
    )


def create_member(
    db: Session, *, household_id: uuid.UUID, user_id: uuid.UUID
) -> HouseholdMember:
    member = HouseholdMember(household_id=household_id, user_id=user_id)
    db.add(member)
    db.flush()
    return member


def delete_member(db: Session, member: HouseholdMember) -> None:
    db.delete(member)


# --- invites -------------------------------------------------------------


def create_invite(
    db: Session, *, household_id: uuid.UUID, invited_user_id: uuid.UUID, invited_by: uuid.UUID
) -> HouseholdInvite:
    invite = HouseholdInvite(
        household_id=household_id,
        invited_user_id=invited_user_id,
        invited_by=invited_by,
        status=InviteStatus.PENDING,
    )
    db.add(invite)
    db.flush()
    return invite


def get_invite(db: Session, invite_id: uuid.UUID) -> HouseholdInvite | None:
    return db.get(HouseholdInvite, invite_id)


def get_pending_invite(
    db: Session, *, household_id: uuid.UUID, invited_user_id: uuid.UUID
) -> HouseholdInvite | None:
    return db.scalar(
        select(HouseholdInvite).where(
            HouseholdInvite.household_id == household_id,
            HouseholdInvite.invited_user_id == invited_user_id,
            HouseholdInvite.status == InviteStatus.PENDING,
        )
    )


def list_pending_invites_for_household(
    db: Session, household_id: uuid.UUID
) -> list[HouseholdInvite]:
    return list(
        db.scalars(
            select(HouseholdInvite)
            .where(
                HouseholdInvite.household_id == household_id,
                HouseholdInvite.status == InviteStatus.PENDING,
            )
            .order_by(HouseholdInvite.created_at.desc())
        )
    )


def list_pending_invites_for_user(
    db: Session, invited_user_id: uuid.UUID
) -> list[HouseholdInvite]:
    return list(
        db.scalars(
            select(HouseholdInvite)
            .where(
                HouseholdInvite.invited_user_id == invited_user_id,
                HouseholdInvite.status == InviteStatus.PENDING,
            )
            .order_by(HouseholdInvite.created_at.desc())
        )
    )
