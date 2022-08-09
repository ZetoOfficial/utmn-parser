import json
from urllib.parse import urlencode

import requests
from tqdm import tqdm

from settings import getLogger

logger = getLogger(__name__)


class InvalidTokenException(Exception):
    pass


class UtmnParser:
    _api_url: str = "https://nova.utmn.ru/api/v1"
    _headers: dict = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }

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
        payload = json.dumps({"usernameOrEmail": username, "password": password})
        resp = requests.post(f"{self._api_url}/auth/signin", headers=self._headers, data=payload)
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
        students_bar = tqdm(desc="Сбор первичных данных о студентах", total=total)
        total = resp.get("response").get("total")
        all_students = [*resp.get("response").get("users")]
        params["limit"] = 20
        for offset in range(1, total + 1, 20):
            params["offset"] = offset
            resp = requests.get(f"{self._api_url}/users?{urlencode(params)}", headers=self._headers).json()
            logger.debug(resp)
            all_students += resp.get("response").get("users")
            students_bar.update(20)
        students_bar.close()
        return all_students

    def get_student(self, username: str) -> dict:
        """Получение подробной информации о студенте

        Args:
            username (str): username студента на vmeste

        Returns:
            dict: результат запроса
        """
        return requests.get(f"{self._api_url}/users/username/{username}", headers=self._headers).json()
