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
        self.assertEquals('javerage', endpoint.user)
        self.assertEquals('sdf', endpoint.owner)
        self.assertEquals(False, endpoint.active)

    def test_create_endpoint(self):
        nws = NWS()
        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        endpoint.endpoint_id = None
        endpoint.endpoint_uri = None

        self.assertRaises(
            DataFailureException, nws.create_new_endpoint, endpoint)
        # response_status = nws.create_new_endpoint(endpoint)
        # self.assertEquals(201, response_status)

	endpoint.user = ""
        self.assertRaises(InvalidNetID, nws.create_new_endpoint, endpoint)

    def test_get_endpoints(self):
        nws = NWS()
        endpoints = nws.get_endpoints()
        self.assertEquals(len(endpoints), 2)

        endpoint = endpoints[0]
        self._assert_endpoint_matches(endpoint)

    def test_endpoint_by_endpoint_id(self):
        nws = NWS()
        endpoint = nws.get_endpoint_by_endpoint_id(
            "780f2a49-2118-4969-9bef-bbd38c26970a")
        self._assert_endpoint_matches(endpoint)

        self.assertRaises(InvalidUUID, nws.get_endpoint_by_endpoint_id, None)
        self.assertRaises(InvalidUUID, nws.get_endpoint_by_endpoint_id,  '')
        self.assertRaises(InvalidUUID, nws.get_endpoint_by_endpoint_id, 'ABC')

    def test_endpoint_search_by_subscriber_id(self):
        nws = NWS()
        endpoints = nws.get_endpoints_by_subscriber_id("javerage")
        self.assertEquals(len(endpoints), 2)

        endpoint = endpoints[0]
        self._assert_endpoint_matches(endpoint)

	self.assertRaises(
            InvalidNetID, nws.get_endpoints_by_subscriber_id, None)
        self.assertRaises(InvalidNetID, nws.get_endpoints_by_subscriber_id, "")
        self.assertRaises(InvalidNetID, nws.get_endpoints_by_subscriber_id, 32)

    def test_endpoint_search_by_endpoint_address(self):
        nws = NWS()
        endpoint = nws.get_endpoint_by_address("222-222-3333")
        self._assert_endpoint_matches(endpoint)

    def test_endpoint_by_subscriber_id_and_protocol(self):
        nws = NWS()
        endpoint = nws.get_endpoint_by_subscriber_id_and_protocol(
            "javerage", "sms")
        self._assert_endpoint_matches(endpoint)

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
