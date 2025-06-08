from pydantic import BaseModel


class SchemaPost(BaseModel):
    title: str
    text: str
    author: int


class SchemaPostUpdate(BaseModel):
    id: int
    title: str
    text: str


class Filter(BaseModel):
    desc: str = None
    limit: int = None
    author: int = None