from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.config import settings
from app.modules.auth.dependencies import (
    AuthServiceDependency,
    CurrentUserDependency,
)
from app.modules.auth.schemas import AuthSession, LoginRequest
from app.modules.auth.rate_limit import (
    LoginRateLimitDependency,
    RegistrationRateLimitDependency,
)
from app.modules.auth.service import (
    DuplicateIdentityError,
    InvalidCredentialsError,
)
from app.modules.auth.tokens import (
    InvalidTokenError,
    TokenConfigurationError,
    create_access_token,
    decode_access_token,
)
from app.modules.users.schemas import UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegister,
    service: AuthServiceDependency,
    _rate_limit: RegistrationRateLimitDependency,
) -> UserRead:
    try:
        return UserRead.model_validate(service.register(payload))
    except DuplicateIdentityError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", response_model=AuthSession)
def login(
    payload: LoginRequest,
    response: Response,
    service: AuthServiceDependency,
    _rate_limit: LoginRateLimitDependency,
) -> AuthSession:
    try:
        user = service.authenticate(payload.email, payload.password)
        token, expires_at = create_access_token(
            user.id,
            settings.auth_secret_key,
            settings.auth_token_expiration_minutes,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except TokenConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured",
        ) from exc

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="strict",
        max_age=settings.auth_token_expiration_minutes * 60,
        path="/",
    )
    return AuthSession(
        access_token=token,
        expires_at=expires_at,
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUserDependency) -> UserRead:
    return UserRead.model_validate(current_user)


def _request_tokens(request: Request) -> set[str]:
    tokens: set[str] = set()
    cookie = request.cookies.get(settings.auth_cookie_name)
    if cookie:
        tokens.add(cookie)

    authorization = request.headers.get("Authorization")
    if authorization is not None:
        scheme, separator, credentials = authorization.partition(" ")
        if separator == " " and scheme.lower() == "bearer" and credentials.strip():
            tokens.add(credentials.strip())
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> Response:
    for token in _request_tokens(request):
        try:
            identity = decode_access_token(token, settings.auth_secret_key)
            request.app.state.revoked_auth_tokens.revoke(identity)
        except (InvalidTokenError, TokenConfigurationError):
            # Logout is idempotent and never reveals whether a presented token was valid.
            pass

    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="strict",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
