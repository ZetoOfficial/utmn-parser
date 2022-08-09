import csv
import json

from tqdm import tqdm

from app.utmn_parser import UtmnParser
from settings import settings


def main():
    up = UtmnParser(settings.app.usernameOrEmail, settings.app.password)

    students = up.get_all_students_by_study_plan(
        study_plan="Математическое обеспечение и администрирование информационных систем",
        entered=2018,
    )
    students_out = []

    students_bar = tqdm(desc="Сбор данных о студентах", total=len(students))

    with open("cached_students.json", 'r', encoding='utf8') as f:
        cached_students = json.load(f)

    for student in students:
        username = student.get("username")
        fio = student.get("displayName")
        if not cached_students.get(username):
            student_info = up.get_student(username).get("response")
            cached_students.update({username: student_info})
            with open("cached_students.json", 'w', encoding='utf8') as f:
                json.dump(cached_students, f, ensure_ascii=False)
        students_bar.update(1)
    students_bar.close()

    for student in students:
        username = student.get("username")
        fio = student.get("displayName")
        if username is None:
            continue
        student_info = cached_students.get(username)
        if student_info is None:
            continue
        defaultStudbook = student_info.get("defaultStudbook")
        rating = 0.0
        entered_upon = "Нет информации"
        entered = student_info["main"].get("entered")
        specialtyCode = student_info["main"].get("specialtyCode")
        educationLevel = student_info["main"].get("educationLevel")
        for studbook in student_info.get("studbooks"):
            if not studbook.get("active"):
                continue
            rating = student_info.get("rating").get("progress")
            if isinstance(rating, dict):
                rating = rating.get(defaultStudbook, 0.0)
            entered_upon = studbook.get("enteredUpon")
        students_out.append([educationLevel, specialtyCode, entered, fio, round(float(rating), 2), entered_upon])

    with open("moais_format.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(sorted(students_out, key=lambda s: (s[4], s[0], s[1], s[2]), reverse=True))


if __name__ == "__main__":
    main()
