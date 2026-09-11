from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""


class SubjectResponse(BaseModel):
    id: str
    name: str
    description: str

    model_config = {"from_attributes": True}


class GradeCreate(BaseModel):
    subject_id: str
    name: str = Field(min_length=1, max_length=100)


class GradeResponse(BaseModel):
    id: str
    subject_id: str
    name: str

    model_config = {"from_attributes": True}


class ChapterCreate(BaseModel):
    grade_id: str
    name: str = Field(min_length=1, max_length=255)
    order: int = 0


class ChapterResponse(BaseModel):
    id: str
    grade_id: str
    name: str
    order: int

    model_config = {"from_attributes": True}


class LessonCreate(BaseModel):
    chapter_id: str
    name: str = Field(min_length=1, max_length=255)
    content: str = ""
    order: int = 0


class LessonResponse(BaseModel):
    id: str
    chapter_id: str
    name: str
    content: str
    order: int

    model_config = {"from_attributes": True}


class KnowledgePointCreate(BaseModel):
    lesson_id: str
    name: str = Field(min_length=1, max_length=255)


class KnowledgePointResponse(BaseModel):
    id: str
    lesson_id: str
    name: str

    model_config = {"from_attributes": True}
