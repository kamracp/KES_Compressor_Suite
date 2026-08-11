from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Persistence operations for tenant-scoped SaaS users."""

    def create(
        self,
        db: Session,
        *,
        organization_id: int,
        email: str,
        full_name: str,
        password_hash: str,
        active: bool,
        verified: bool,
    ) -> User:
        user = User(
            organization_id=organization_id,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            active=active,
            verified=verified,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def get_by_id(
        self,
        db: Session,
        user_id: int,
    ) -> User | None:
        return db.get(
            User,
            user_id,
        )

    def get_by_email(
        self,
        db: Session,
        *,
        organization_id: int,
        email: str,
    ) -> User | None:
        statement = select(User).where(
            User.organization_id == organization_id,
            User.email == email,
        )

        return db.execute(statement).scalar_one_or_none()

    def list_by_organization(
        self,
        db: Session,
        *,
        organization_id: int,
        active_only: bool = False,
    ) -> tuple[User, ...]:
        statement = select(User).where(
            User.organization_id == organization_id,
        )

        if active_only:
            statement = statement.where(
                User.active.is_(True),
            )

        statement = statement.order_by(
            User.full_name,
            User.id,
        )

        return tuple(db.execute(statement).scalars().all())

    def update(
        self,
        db: Session,
        user: User,
        *,
        updates: dict,
    ) -> User:
        for field_name, value in updates.items():
            setattr(
                user,
                field_name,
                value,
            )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user


user_repository = UserRepository()
