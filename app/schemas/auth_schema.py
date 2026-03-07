from pydantic import BaseModel

class LoginRequest(BaseModel):
    mobile_or_email: str


class VerifyOTPRequest(BaseModel):
    mobile_or_email: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"