from pydantic import BaseModel


class SchemaUser(BaseModel):
    name: str
    token: str = "NoToken"
    login: str
    password: str


class SchemaVerification(BaseModel):
    login: str
    password: str