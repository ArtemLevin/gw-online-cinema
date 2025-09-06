from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db import get_session, Base, engine
from .models import User
from .schemas import RegisterRequest, LoginRequest, TokenPair, Me
from .security import hash_password, verify_password, create_token, decode_token

app = FastAPI(title="Auth Service", docs_url="/api/auth/openapi", openapi_url="/api/auth/openapi.json")

security = HTTPBearer()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "OK"}

@app.post("/api/auth/register", response_model=Me, status_code=201)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(User).where(User.email == payload.email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return Me(id=user.id, email=user.email)

@app.post("/api/auth/login", response_model=TokenPair)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(User).where(User.email == payload.email))
    user = res.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenPair(
        access=create_token(str(user.id), minutes=30),
        refresh=create_token(str(user.id), minutes=43200)
    )

@app.get("/api/auth/me", response_model=Me)
async def me(token: HTTPAuthorizationCredentials = Depends(security), session: AsyncSession = Depends(get_session)):
    try:
        payload = decode_token(token.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload["sub"])
    res = await session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return Me(id=user.id, email=user.email)
