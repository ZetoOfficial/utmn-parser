import csv
import json
from datetime import date

from pydantic import BaseModel
from tqdm import tqdm

from app.utmn_parser import UtmnParser
from settings import getLogger, settings

logger = getLogger(__name__)


class InvalidUsername(Exception):
    pass


class StudentNotFound(Exception):
    pass


# Models
class Student(BaseModel):
    education_level: str
    specialty_code: str
    entered: int
    fio: str
    rating: float
    entered_upon: str


# Checks
def validate_student(student: dict, cached_students: dict):
    username = student['username']
    if username is None:
        raise InvalidUsername

    student_info = cached_students[username]
    if student_info is None:
        raise StudentNotFound


def get_students_information(students: list, cached_students: dict):
    for student in students:
        try:
            validate_student(student, cached_students)
        except InvalidUsername:
            logger.error(f'{student} have invalid username')
            continue
        except StudentNotFound:
            logger.error(f'{student} not found')
            continue

        username: str = student['username']
        fio: str = student['displayName']
        student_info = cached_students[username]

        rating: float = 0.00
        entered_upon: str = 'No info'
        entered: int = student_info['main'].get('entered')
        specialty_code: str = student_info['main'].get('specialtyCode')
        education_level: str = student_info['main'].get('educationLevel')

        for studbook in student_info['studbooks']:
            if not studbook.get('active'):
                continue
            rating = student_info.get('rating').get('progress')
            if isinstance(rating, dict):
                rating = rating.get(student_info['defaultStudbook'], 0.00)
            entered_upon = studbook.get('enteredUpon')

        yield Student(
            education_level=education_level,
            specialty_code=specialty_code,
            entered=entered,
            fio=fio,
            rating=round(float(rating), 2),
            entered_upon=entered_upon,
        )


# Cache student
def cache_students(up: UtmnParser, students: list) -> dict:
    with open('cached_students.json', 'r', encoding='utf8') as f:
        cached_students = json.load(f)

    students_bar = tqdm(desc='Collecting student data', total=len(students))
    for student in students:
        username = student.get('username')
        if not cached_students.get(username):
            student_info = up.get_student(username).get('response')
            cached_students.update({username: student_info})
            with open('cached_students.json', 'w', encoding='utf8') as f:
                json.dump(cached_students, f, ensure_ascii=False)
        students_bar.update(1)
    students_bar.close()

    return cached_students


def main(study_plan: str, qualification: str, entered: int, short_name: str):
    up = UtmnParser(settings.app.usernameOrEmail, settings.app.password)

    students = up.get_all_students_by_study_plan(
        study_plan=study_plan,
        qualification=qualification,
        entered=entered,
    )

    cached_students = cache_students(up, students)

    students = sorted(
        get_students_information(students, cached_students),
        key=lambda student: (
            student.rating,
            student.education_level,
            student.specialty_code,
            student.entered,
        ),
        reverse=True,
    )
    fieldnames = list(Student.__fields__.keys())
    with open(f'students_{short_name}_{entered}_{date.today()}.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for student in students:
            writer.writerow(student.dict())


if __name__ == '__main__':
    study_plan = 'Математическое обеспечение и администрирование информационных систем'
    # study_plan = 'Прикладная информатика: разработка информационных систем бизнеса'
    # study_plan = 'Информационные системы и технологии: интернет-технологии и разработка web-приложений'
    short_name = 'моаис'  # тут чисто для сохранения в файл
    qualification = 'Бакалавр'
    entered = 2024  # тут менять год
    main(study_plan, qualification, entered, short_name)
