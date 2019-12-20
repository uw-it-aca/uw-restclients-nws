from unittest import TestCase
from uw_nws import NWS
from uw_nws.models import Endpoint
from uw_nws.utilities import fdao_nws_override
from uw_nws.exceptions import InvalidUUID, InvalidEndpointProtocol
from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)


@fdao_nws_override
class NWSTestEndpoint(TestCase):
    def _assert_endpoint_matches(self, endpoint):
        self.assertEquals(
            '780f2a49-2118-4969-9bef-bbd38c26970a', endpoint.endpoint_id)
        self.assertEquals(
            '/notification/v1/endpoint/780f2a49-2118-4969-9bef-bbd38c26970a',
            endpoint.endpoint_uri)
        self.assertEquals('222-222-3333', endpoint.endpoint_address)
        self.assertEquals('AT&T', endpoint.carrier)
        self.assertEquals('sms', endpoint.protocol)
        self.assertEquals('javerage', endpoint.subscriber_id)
        self.assertEquals('sdf', endpoint.owner)
        self.assertEquals('unconfirmed', endpoint.status)
        self.assertFalse(endpoint.is_verified())
        self.assertEquals(False, endpoint.active)

        # Backward compatibility methods
        self.assertEquals('javerage', endpoint.get_user_net_id())
        self.assertEquals('sdf', endpoint.get_owner_net_id())

        # JSON data
        data = endpoint.json_data()
        self.assertEquals(False, data['Endpoint']['Active'])
        self.assertEquals('unconfirmed', data['Endpoint']['Status'])

    def test_endpoint_by_endpoint_id(self):
        nws = NWS()
        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        self._assert_endpoint_matches(endpoint)

        self.assertRaises(InvalidUUID, nws.get_endpoint_by_endpoint_id, None)
        self.assertRaises(InvalidUUID, nws.get_endpoint_by_endpoint_id,  '')
        self.assertRaises(InvalidUUID, nws.get_endpoint_by_endpoint_id, 'ABC')
        self.assertRaises(
            DataFailureException, nws.get_endpoint_by_endpoint_id,
            '00000000-0000-0000-0000-000000000000')

    def test_endpoint_search_by_subscriber_id(self):
        nws = NWS()
        endpoints = nws.get_endpoints_by_subscriber_id("javerage")
        self.assertEquals(len(endpoints), 2)

        endpoint = endpoints[0]
        self._assert_endpoint_matches(endpoint)

        endpoint = endpoints[1]
        self.assertTrue(endpoint.is_verified())

        self.assertRaises(
            InvalidNetID, nws.get_endpoints_by_subscriber_id, None)
        self.assertRaises(InvalidNetID, nws.get_endpoints_by_subscriber_id, "")
        self.assertRaises(InvalidNetID, nws.get_endpoints_by_subscriber_id, 32)

    def test_endpoint_by_address(self):
        nws = NWS()
        endpoint = nws.get_endpoint_by_address("222-222-3333")
        self._assert_endpoint_matches(endpoint)

    def test_endpoint_by_address_exceptions(self):
        nws = NWS()
        # Valid address, no endpoints
        self.assertRaises(
            DataFailureException, nws.get_endpoint_by_address, "123-456-7890")
        # Valid address, no file found
        self.assertRaises(
            DataFailureException, nws.get_endpoint_by_address, "000-000-0000")

    def test_endpoint_by_subscriber_id_and_protocol(self):
        nws = NWS()
        endpoint = nws.get_endpoint_by_subscriber_id_and_protocol(
            "javerage", "sms")
        self._assert_endpoint_matches(endpoint)

    def test_endpoint_by_subscriber_id_and_protocol_exceptions(self):
        nws = NWS()
        # Valid netid and protocol, no endpoints
        self.assertRaises(
            DataFailureException,
            nws.get_endpoint_by_subscriber_id_and_protocol,
            "javerage", "email")
        # Valid netid and protocol, file not found
        self.assertRaises(
            DataFailureException,
            nws.get_endpoint_by_subscriber_id_and_protocol, "bill", "sms")
        self.assertRaises(
            InvalidNetID, nws.get_endpoint_by_subscriber_id_and_protocol,
            None, "sms")
        self.assertRaises(
            InvalidNetID, nws.get_endpoint_by_subscriber_id_and_protocol,
            "", "sms")
        self.assertRaises(
            InvalidNetID, nws.get_endpoint_by_subscriber_id_and_protocol,
            32, "sms")
        self.assertRaises(
            InvalidEndpointProtocol,
            nws.get_endpoint_by_subscriber_id_and_protocol, "javerage", None)
        self.assertRaises(
            InvalidEndpointProtocol,
            nws.get_endpoint_by_subscriber_id_and_protocol, "javerage", "")

    def test_resend_sms_endpoint_verification(self):
        nws = NWS()
        self.assertRaises(
            InvalidUUID, nws.resend_sms_endpoint_verification, "")
        self.assertRaises(
            DataFailureException, nws.resend_sms_endpoint_verification,
            "780f2a49-2118-4969-9bef-bbd38c26970a")

    def test_create_endpoint(self):
        nws = NWS(actas_user="javerage")
        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        endpoint.endpoint_id = None
        endpoint.endpoint_uri = None

        self.assertRaises(
            DataFailureException, nws.create_endpoint, endpoint)

        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        endpoint.subscriber_id = ""
        self.assertRaises(InvalidNetID, nws.create_endpoint, endpoint)

    def test_update_endpoint(self):
        nws = NWS(actas_user="javerage")
        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")

        self.assertRaises(
            DataFailureException, nws.update_endpoint, endpoint)

        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        endpoint.endpoint_id = ""
        self.assertRaises(
            InvalidUUID, nws.update_endpoint, endpoint)

        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        endpoint.subscriber_id = ""
        self.assertRaises(
            InvalidNetID, nws.update_endpoint, endpoint)

    def test_delete_endpoint(self):
        nws = NWS(actas_user="javerage")
        self.assertRaises(
            DataFailureException, nws.delete_endpoint,
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        self.assertRaises(
            InvalidUUID, nws.delete_endpoint, "")
