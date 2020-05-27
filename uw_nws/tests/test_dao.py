from unittest import TestCase
from uw_nws.dao import NWS_DAO
from uw_nws.utilities import fdao_nws_override
from commonconf import override_settings


@fdao_nws_override
class NWSTestDAO(TestCase):
    def test_no_auth_header(self):
        nws = NWS_DAO()
        headers = nws._custom_headers("GET", "/", {}, "")
        self.assertFalse("Authorization" in headers)

    @override_settings(RESTCLIENTS_NWS_OAUTH_BEARER="test1")
    def test_auth_header(self):
        nws = NWS_DAO()
        headers = nws._custom_headers("GET", "/", {}, "")
        self.assertTrue("Authorization" in headers)
        self.assertEqual(headers["Authorization"], "Bearer test1")
