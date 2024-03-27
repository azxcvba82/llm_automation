from typing import Optional
from langchain.pydantic_v1 import BaseModel, Field

class ShellTool(BaseModel):
    command: str = Field(description="should be a command in string type")

class PythonTool(BaseModel):
    command: str = Field(description="should be a script in string type")

class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")