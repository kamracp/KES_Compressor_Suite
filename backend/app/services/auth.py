from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.core.token_security import create_access_token
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.auth import AccessTokenResponse, LoginRequest


class AuthenticationFailedError(ValueError):
    """Raised when login credentials are invalid."""


class InactiveUserError(PermissionError):
    """Raised when an inactive user attempts to authenticate."""


class AuthService:
    """Authentication service for SaaS users."""

    def authenticate(
        self,
        db: Session,
        request: LoginRequest,
    ) -> tuple[User, AccessTokenResponse]:
        normalized_email = str(request.email).strip().lower()

        user = user_repository.get_by_email(
            db,
            organization_id=request.organization_id,
            email=normalized_email,
        )

        if user is None:
            raise AuthenticationFailedError("Invalid organization, email, or password.")

        if not user.active:
            raise InactiveUserError("User account is inactive.")

        if not verify_password(
            password=request.password,
            hashed_password=user.password_hash,
        ):
            raise AuthenticationFailedError("Invalid organization, email, or password.")

        token, expires_at = create_access_token(
            user_id=user.id,
            organization_id=user.organization_id,
            email=user.email,
        )

        return user, AccessTokenResponse(
            access_token=token,
            expires_at=expires_at,
        )


auth_service = AuthService()
