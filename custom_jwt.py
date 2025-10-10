import asyncio
import uuid
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi_jwt_auth3.jwtauth import (
    FastAPIJWTAuth,
    JWTPresetClaims,
    KeypairGenerator,
    generate_jwt_token,
)
from jwcrypto import jwk
from piccolo.apps.user.tables import BaseUser
from pydantic import BaseModel, ConfigDict, EmailStr


# Define the token claims to be projected to when decoding JWT tokens
class TokenClaims(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: int
    username: str
    email: EmailStr
    iss: str
    aud: str
    exp: int
    sub: str
    iat: int
    jti: str
    # You can pass whatever you want here, e.g. roles: str or roles: list[str]
    # for authorization etc. and add that to the claims in the login route
    # role: str
    # roles: list[str]


# Payload for our logins
class LoginIn(BaseModel):
    username: str
    password: str


# FastAPI app instantiation
app = FastAPI(title="FastAPI JWT Auth Example")

# For the purpose of this example, we will generate a new RSA keypair
private_key, public_key = KeypairGenerator.generate_rsa_keypair()

# Create a JWK key from the public key
jwk_key = jwk.JWK.from_pem(public_key.encode("utf-8"))
public_key_id = jwk_key.get("kid")

jwt_auth = FastAPIJWTAuth(
    algorithm="RS256",
    base_url="http://localhost:8000",
    secret_key=private_key,
    public_key=public_key,
    public_key_id=public_key_id,
    issuer="https://localhost:8000",
    audience="https://localhost:8000",
    expiry=60 * 15,
    refresh_token_expiry=60 * 60 * 24 * 7,
    leeway=0,
    project_to=TokenClaims,
)

jwt_auth.init_app(app)


# Protected route
@app.get("/protected")
async def current_user(claims: TokenClaims = Depends(jwt_auth)) -> TokenClaims:
    return claims


# Login route
@app.post("/login")
async def login(payload: LoginIn) -> dict[str, Any]:
    # Use Piccolo login method to compare the username and hashed password
    # with the payload data and obtain the registered user id
    user = await BaseUser.login(
        username=payload.username, password=payload.password
    )
    # get user
    result: Any = await BaseUser.objects().where(BaseUser.id == user).first()

    # preset claims
    preset_claims = JWTPresetClaims.factory(
        issuer=jwt_auth.issuer,
        audience=jwt_auth.audience,
        expiry=jwt_auth.expiry,
        subject=str(uuid.uuid4()),
    )

    # additional claims
    claims = {
        "user_id": result.id,
        "username": result.username,
        "email": result.email,
    }

    # generate token
    token = generate_jwt_token(
        header=jwt_auth.header,
        secret_key=jwt_auth.secret_key,
        preset_claims=preset_claims,
        claims=claims,
    )

    # This is optional but good practice to generate refresh token
    refresh_token = jwt_auth.generate_refresh_token(access_token=token)

    return {"access_token": token, "refresh_token": refresh_token}


# Public route
@app.get("/")
async def public() -> JSONResponse:
    return JSONResponse({"data": "Public Page"})


async def main():
    # Tables creating
    await BaseUser.create_table(if_not_exists=True)

    # Creating example user
    if not await BaseUser.exists().where(BaseUser.email == "admin@test.com"):
        user = BaseUser(
            username="piccolo",
            password="piccolo123",
            email="admin@test.com",
            admin=True,
            active=True,
            superuser=True,
        )
        await user.save()


if __name__ == "__main__":
    asyncio.run(main())

    uvicorn.run(app, host="127.0.0.1", port=8000)
