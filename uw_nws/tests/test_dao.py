from unittest import TestCase
from uw_nws.dao import NWS_DAO, NWS_AUTH_DAO
from uw_nws.utilities import fdao_nws_override
from commonconf import override_settings
import mock


@fdao_nws_override
class NWSTestDAO(TestCase):
    def test_no_auth_header(self):
        nws = NWS_DAO()
        headers = nws._custom_headers("GET", "/", {}, "")
        self.assertFalse("Authorization" in headers)

    @override_settings(RESTCLIENTS_NWS_AUTH_SECRET="test1")
    @mock.patch.object(NWS_AUTH_DAO, "get_auth_token")
    def test_auth_header(self, mock_get_auth_token):
        mock_get_auth_token.return_value = "abcdef"
        nws = NWS_DAO()
        headers = nws._custom_headers("GET", "/", {}, "")
        self.assertTrue("Authorization" in headers)
        self.assertEqual(headers["Authorization"], "Bearer abcdef")
