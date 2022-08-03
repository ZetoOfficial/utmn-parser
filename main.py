import csv

from app.utmn_parser import UtmnParser
from settings import settings

if __name__ == "__main__":
    up = UtmnParser(settings.app.usernameOrEmail, settings.app.password)

    students = up.get_all_students_by_study_plan(
        "Математическое обеспечение и администрирование информационных систем"
    )
    students_out = []
    for student in sorted(students, key=lambda student: student.get("displayName")):
        username = student.get("username")
        fio = student.get("displayName")
        if username is None:
            continue
        student_info = up.get_student(username).get("response")
        if student_info is None:
            continue
        rating = ""
        entered_upon = ""
        for studbook in student_info.get("studbooks"):
            if not studbook.get("active"):
                continue
            studbook_id = studbook.get("studbookId")
            rating = student_info.get("rating").get("progress").get(studbook_id)
            entered_upon = studbook.get("enteredUpon")
        students_out.append([fio, rating, entered_upon])

    # with open("moais.csv", "r") as f:
    #     reader = csv.reader(f)
    #     for row in reader:
    #         fio = row[0]
    #         rating = float(row[1]) if row[1] and row[1] != "no info" else 0.0
    #         entered_upon = row[2]
    #         students_out.append([fio, round(rating, 2), entered_upon])
    #     # writer.writerows(sorted(students_out, key=lambda s: (s[2], s[1])))

    with open("moais_format.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(sorted(students_out, key=lambda s: (s[2], s[1]), reverse=True))
