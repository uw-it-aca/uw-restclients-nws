"""
Contains UW NWS DAO implementations.
"""
from restclients_core.dao import DAO
from os.path import abspath, dirname
import os


class NWS_DAO(DAO):
    def service_name(self):
        return 'nws'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _custom_headers(self, method, url, headers, body):
        headers = {}
        bearer_key = self.get_service_setting("OAUTH_BEARER", "")
        if bearer_key:
            headers["Authorization"] = "Bearer {}".format(bearer_key)
        return headers
