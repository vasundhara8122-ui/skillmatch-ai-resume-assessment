from pydantic import BaseModel


class CompanyLogin(BaseModel):
    email: str
    password: str


class StudentLogin(BaseModel):
    email: str
    password: str


class AnswerSubmit(BaseModel):
    question_id: int
    candidate_answer: str


class AssessmentSubmit(BaseModel):
    answers: list[AnswerSubmit]


class JobRoleCreate(BaseModel):
    name: str
    skills: list[dict]
