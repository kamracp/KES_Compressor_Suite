from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.organization import organization_repository
from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate


class UserNotFoundError(LookupError):
    """Raised when a user cannot be found."""


class UserEmailConflictError(ValueError):
    """Raised when an email already exists within an organization."""


class UserOrganizationNotFoundError(LookupError):
    """Raised when the requested organization cannot be found."""


class UserService:
    """Business service for tenant-scoped SaaS users."""

    def create(
        self,
        db: Session,
        user_in: UserCreate,
    ) -> User:
        organization = organization_repository.get_by_id(
            db,
            user_in.organization_id,
        )

        if organization is None:
            raise UserOrganizationNotFoundError("Organization not found.")

        normalized_email = str(user_in.email).strip().lower()

        existing = user_repository.get_by_email(
            db,
            organization_id=user_in.organization_id,
            email=normalized_email,
        )

        if existing is not None:
            raise UserEmailConflictError(
                f"Email '{normalized_email}' already exists within this organization."
            )

        return user_repository.create(
            db,
            organization_id=user_in.organization_id,
            email=normalized_email,
            full_name=user_in.full_name.strip(),
            password_hash=hash_password(user_in.password),
            active=user_in.active,
            verified=user_in.verified,
        )

    def get(
        self,
        db: Session,
        user_id: int,
    ) -> User:
        user = user_repository.get_by_id(
            db,
            user_id,
        )

        if user is None:
            raise UserNotFoundError("User not found.")

        return user

    def get_by_email(
        self,
        db: Session,
        *,
        organization_id: int,
        email: str,
    ) -> User:
        normalized_email = email.strip().lower()

        user = user_repository.get_by_email(
            db,
            organization_id=organization_id,
            email=normalized_email,
        )

        if user is None:
            raise UserNotFoundError("User not found.")

        return user

    def list_by_organization(
        self,
        db: Session,
        *,
        organization_id: int,
        active_only: bool = False,
    ) -> tuple[User, ...]:
        organization = organization_repository.get_by_id(
            db,
            organization_id,
        )

        if organization is None:
            raise UserOrganizationNotFoundError("Organization not found.")

        return user_repository.list_by_organization(
            db,
            organization_id=organization_id,
            active_only=active_only,
        )

    def update(
        self,
        db: Session,
        *,
        user_id: int,
        user_in: UserUpdate,
    ) -> User:
        user = self.get(
            db,
            user_id,
        )

        updates = user_in.model_dump(
            exclude_unset=True,
        )

        if "email" in updates and updates["email"] is not None:
            normalized_email = str(updates["email"]).strip().lower()

            existing = user_repository.get_by_email(
                db,
                organization_id=user.organization_id,
                email=normalized_email,
            )

            if existing is not None and existing.id != user.id:
                raise UserEmailConflictError(
                    f"Email '{normalized_email}' already exists within this organization."
                )

            updates["email"] = normalized_email

        if "full_name" in updates and updates["full_name"] is not None:
            updates["full_name"] = updates["full_name"].strip()

        return user_repository.update(
            db,
            user,
            updates=updates,
        )


user_service = UserService()
