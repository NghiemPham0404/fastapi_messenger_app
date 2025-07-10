from pydantic import BaseModel

class Token(BaseModel):
    """
    Token model for JWT
    """
    success : bool = True
    access_token: str
    token_type : str
    refresh_token : str


class LoginWithEmailForm(BaseModel):
    """
    Login Form with email and password
    """
    email: str
    password: str

class SignUpWithEmailForm(BaseModel):
    """
    Sign Form with name, email and password
    """
    name : str
    email: str
    password: str

class RefreshTokenBody(BaseModel):
    refresh_token : str


class GoogleLoginRequest(BaseModel):
    email : str
    username : str
    avatar : str
    provider : str = "Google"
    provider_id : str

class AuthProviderInDB(BaseModel):
    user_id : int
    provider : str
    provider_id : str

