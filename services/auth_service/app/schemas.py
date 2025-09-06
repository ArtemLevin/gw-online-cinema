from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access: str
    refresh: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Me(BaseModel):
    id: int
    email: EmailStr
