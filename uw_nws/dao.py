from restclients_core.dao import DAO
from restclients_core.exceptions import DataFailureException
from os.path import abspath, dirname
import json
import os


class NWS_AUTH_DAO(DAO):
    def service_name(self):
        return 'nws_auth'

    def _is_cacheable(self, method, url, headers, body=None):
        return True

    def get_auth_token(self, secret):
        url = '/oauth2/token'
        headers = {'Authorization': 'Basic {}'.format(secret),
                   'Content-type': 'application/x-www-form-urlencoded'}

        response = self.postURL(url, headers, 'grant_type=client_credentials')

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return data.get('access_token', '')


class NWS_DAO(DAO):
    def __init__(self):
        self.auth_dao = NWS_AUTH_DAO()
        return super(NWS_DAO, self).__init__()

    def service_name(self):
        return 'nws'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), 'resources'))]

    def _custom_headers(self, method, url, headers, body):
        headers = {}
        secret = self.get_service_setting('AUTH_SECRET', '')
        if secret:
            headers['Authorization'] = self.auth_dao.get_auth_token(secret)
        return headers
