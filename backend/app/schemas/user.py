from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str



    class Config:
        from_attributes = True