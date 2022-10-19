import json
from urllib.parse import urlencode

import requests
from tqdm import tqdm

from settings import getLogger

logger = getLogger(__name__)


class InvalidTokenException(Exception):
    pass


class UtmnParser:
    _api_url: str = 'https://nova.utmn.ru/api/v1'
    _headers: dict = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }

    def __init__(self, username: str, password: str) -> None:
        self._headers.update({'Authorization': self._get_token(username, password)})

    def _get_token(self, username: str, password: str) -> str:
        '''Getting token by username and password

        Args:
            username (str): Username or e-mail
            password (str): Password

        Raises:
            InvalidTokenException: Authorization data is not valid

        Returns:
            str: Received token
        '''
        payload = json.dumps({'usernameOrEmail': username, 'password': password})
        resp = requests.post(
            f'{self._api_url}/auth/signin', headers=self._headers, data=payload
        )
        resp = resp.json().get('response')
        if token := resp.get('token'):
            return token
        raise InvalidTokenException()

    def get_all_students_by_study_plan(
        self,
        study_plan: str,
        qualification: str,
        entered: int,
    ) -> list:
        '''Getting all students of a given direction

        Args:
            study_plan (str): Full name of the study plan
            qualification (str): Qualification level
            entered (int, optional): Entered Year. The default is 2021.

        Returns:
            dict: query result
        '''
        params = {
            'limit': 1,
            'searchRole': 'student',
            'entered': entered,
            'studyPlan': study_plan,
            'offset': 0,
            'qualification': qualification,
        }
        limit = 20
        resp = requests.get(
            f'{self._api_url}/users?{urlencode(params)}', headers=self._headers
        ).json()
        total = resp.get('response').get('total')

        all_students = [*resp.get('response').get('users')]
        params['limit'] = limit
        students_bar = tqdm(desc='Collecting primary data on students', total=total)

        for offset in range(1, total + 1, limit):
            params['offset'] = offset
            resp = requests.get(
                f'{self._api_url}/users?{urlencode(params)}', headers=self._headers
            ).json()
            logger.debug(resp)
            all_students += resp.get('response').get('users')
            students_bar.update(limit)
        students_bar.close()

        return all_students

    def get_student(self, username: str) -> dict:
        '''Getting detailed information about the student

        Args:
            username (str): student username on vmeste

        Returns:
            dict: query result
        '''
        return requests.get(
            f'{self._api_url}/users/username/{username}', headers=self._headers
        ).json()
