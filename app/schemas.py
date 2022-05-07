from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    profileImageURL: Optional[str]
    profileImageAD: Optional[str]
    profileLayoutURL: Optional[str]


class Rating(BaseModel):
    activity: int
    portfolio: int
    progress: dict


class MainInfo(BaseModel):
    username: str
    institute: Optional[str]
    department: str
    qualification: str
    formType: str
    entered: int
    specialtyCode: str
    curriculumName: str
    educationLevel: str
    recordBook: str
    birthday: datetime
    displayName: str
    email: str
    modeus: bool
    roles: list[str]


class Studbooks(BaseModel):
    id: str
    studbookId: str
    studbookNumber: str
    department: str
    qualification: str
    entered: int
    academicDegree: str
    specialtyCode: str
    formType: str
    enteredUpon: str
    curriculumName: str
    formOfEducation: str


class Student(BaseModel):
    id: str
    user: User
    main: MainInfo
    rating: Rating
    isActiveUser: bool
    studbooks: Studbooks

    class Config:
        orm_mode = True
