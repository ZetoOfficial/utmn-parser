import json
from urllib.parse import urlencode

import requests

from settings import getLogger

logger = getLogger(__name__)


class InvalidTokenException(Exception):
    pass


class UtmnParser:
    _api_url: str = "https://nova.utmn.ru/api/v1"
    _headers: dict = {}

    def __init__(self, username: str, password: str) -> None:
        self._headers.update({"Authorization": self._get_token(username, password)})

    def _get_token(self, username: str, password: str) -> str:
        """Получение токена по username и password

        Args:
            username (str): Имя пользователя или e-mail
            password (str): Пароль

        Raises:
            InvalidTokenException: Данные для авторизации не валидны

        Returns:
            str: Полученный токен
        """
        return """eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYxMTZjZmUxYzc4ODQ2MDE2Y2VkNmI1NSIsInVzZXJuYW1lIjoic3R1ZDAwMDAyNjE0OTkiLCJwcm9maWxlSW1hZ2VVUkwiOm51bGwsInByb2ZpbGVMYXlvdXRVUkwiOm51bGwsImVtYWlsIjoic3R1ZDAwMDAyNjE0OTlAc3R1ZHkudXRtbi5ydSIsImRpc3BsYXlOYW1lIjoi0KLQuNGC0L7QsiDQn9Cw0LLQtdC7INCh0LXRgNCz0LXQtdCy0LjRhyIsImV4cGlyZXMiOiIxNS4wNy4yMDIyIDc6NTY6MTIiLCJkZXBhcnRtZW50Ijp7Im5hbWUiOiLQmNC90YHRgtC40YLRg9GCINC80LDRgtC10LzQsNGC0LjQutC4INC4INC60L7QvNC_0YzRjtGC0LXRgNC90YvRhSDQvdCw0YPQuiIsInRpdGxlIjpudWxsfSwiaWF0IjoxNjU3ODEwNTcyfQ.dyl9q-5dm1rjFu00WP_EIrhG0NVNZu7q4TL3k819vG0"""
        # payload = json.dumps()
        resp = requests.post(
            f"{self._api_url}auth/signin", data={"usernameOrEmail": username, "password": password}
        )
        resp = resp.json().get("response")
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
        resp = requests.get(f"{self._api_url}/users?{urlencode(params)}", headers=self._headers)
        resp = resp.json()
        total = resp.get("response").get("total")
        all_students = [*resp.get("response").get("users")]
        params["limit"] = 20
        for offset in range(1, total + 1, 20):
            params["offset"] = offset
            resp = requests.get(f"{self._api_url}/users?{urlencode(params)}", headers=self._headers).json()
            logger.debug(resp)
            all_students += resp.get("response").get("users")
        return all_students

    def get_student(self, username: str) -> dict:
        """Получение подробной информации о студенте

        Args:
            username (str): username студента на vmeste

        Returns:
            dict: результат запроса
        """
        return requests.get(f"{self._api_url}/users/username/{username}", headers=self._headers).json()
