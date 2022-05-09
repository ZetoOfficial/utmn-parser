"""
этот говнокод надо бы убрать....
"""
from csv import writer, reader

from app.utmn_parser import UtmnParser
from settings import settings as s


def main():
    utmn = UtmnParser(s.app.usernameOrEmail, s.app.password)
    # study_plan = "Математическое обеспечение и администрирование информационных систем"
    study_plan = "Информационные системы и технологии"
    all_students = utmn.get_all_students_by_study_plan(study_plan=study_plan)
    detail_students = []
    for i, student in enumerate(all_students, start=1):
        username = student.get("username")
        student = utmn.get_student(username)
        main_info = student.get("response", {}).get("main", {})
        studbooks = student.get("response", {}).get("studbooks", {})
        studbooks = list(filter(lambda sb: sb["specialtyCode"] == "09.03.02", studbooks))
        studbooks = studbooks[0] if len(studbooks) else {}
        is_active = studbooks.get("active")
        defaultStudbook = student.get("response", {}).get("defaultStudbook", "")
        rating = student.get("response", {}).get("rating", {}).get("progress", {}).get(defaultStudbook)
        detail_students.append(
            (main_info.get("displayName"), studbooks.get("enteredUpon"), rating, username, is_active)
        )
        print(f"{i}/{len(all_students)} - {main_info.get('displayName')}")
    with open("students_isit_out.csv", "w", newline="") as output_file:
        csv_writer = writer(output_file)
        csv_writer.writerows(detail_students)


def get_students():
    with open("students_isit_out.csv", "r", newline="") as output_file:
        csv_reader = reader(output_file)
        detail_students = []
        for row in csv_reader:
            print(len(row), row)
            row[2] = row[2] or 0
            row[4] = "" if row[4] == "True" else "Отчислен"
            detail_students.append(row)
    with open("students_isit_output.csv", "w", newline="") as output_file:
        csv_writer = writer(output_file)
        csv_writer.writerows(sorted(detail_students, key=lambda r: (r[1], -float(r[2]))))
    return detail_students


def get_otchislen(studs):
    return len(list(filter(lambda stud: stud[4] == "Отчислен", studs)))


if __name__ == "__main__":
    # main()

    detail_students = get_students()
    print(get_otchislen(detail_students))
