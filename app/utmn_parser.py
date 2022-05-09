from json import dumps
from requests import get as r_get
from urllib.parse import urlencode
from settings import settings as s


class InvalidTokenException(Exception):
    pass


class UtmnParser:
    _api_url: str = "https://nova.utmn.ru/api/v1/"
    _headers: dict = {}

    def __init__(self, username: str, password: str) -> None:
        self._headers.update({"Authorization": self.get_token(username, password)})

    def get_token(self, username: str, password: str) -> str:
        """Получение токена по username и password

        Args:
            username (str): Имя пользователя или e-mail
            password (str): Пароль

        Raises:
            InvalidTokenException: Данные для авторизации не валидны

        Returns:
            str: Полученный токен
        """
        payload = dumps({"usernameOrEmail": username, "password": password})
        resp = r_get(f"{self._api_url}/auth/signin", data=payload).json().get("response")
        if token := resp.get("token"):
            return token
        raise InvalidTokenException()

    def get_all_students_by_study_plan(
        self,
        study_plan: str,
        entered: int = 2021,
    ) -> list:
        """Получение всех студентов заданного направления

        Args:
            study_plan (str): Полное название направления
            entered (int, optional): Год поступления. По умолчанию 2021.

        Returns:
            dict: результат запроса
        """
        params = {
            "limit": 1,
            "searchRole": "student",
            "entered": entered,
            "studyPlan": study_plan,
            "offset": 0,
            "qualification": "Бакалавр",
        }
        resp = r_get(f"{self._api_url}/users?{urlencode(params)}", headers=self._headers).json()
        total = resp.get("response").get("total")
        all_students = [resp.get("response").get("users")]
        params["limit"] = 20
        for offset in range(1, total + 1, 20):
            params["offset"] = offset
            resp = r_get(f"{self._api_url}/users?{urlencode(params)}", headers=self._headers).json()
            all_students += resp.get("response").get("users")
        return all_students

    def get_student(self, username: str) -> dict:
        """Получение подробной информации о студенте

        Args:
            username (str): username студента на vmeste

        Returns:
            dict: результат запроса
        """
        return r_get(f"{self._api_url}/users/username/{username}", headers=self._headers).json()
