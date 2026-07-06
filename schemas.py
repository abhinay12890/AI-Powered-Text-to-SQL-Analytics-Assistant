from pydantic import BaseModel
from typing import List

class SQLQuery(BaseModel):
    name:str
    sql:str

class SQLPlan(BaseModel):
    plan_type:str
    queries:List[SQLQuery]


class ValidationResult(BaseModel):
    valid:bool
    reason:str