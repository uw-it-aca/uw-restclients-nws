"""
This is the interface for interacting with the Notifications Web Service.
"""

from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)
from uw_nws.exceptions import InvalidUUID, InvalidEndpointProtocol
from uw_nws.dao import NWS_DAO
from uw_nws.models import (
    Person, Channel, Endpoint, Subscription, CourseAvailableEvent)
# from uw_sws.term import get_current_term, get_term_after
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from datetime import datetime, time
import dateutil.parser
import json
import re


MANAGED_ATTRIBUTES = (
    'DispatchedEmailCount', 'DispatchedTextMessageCount',
    'SentTextMessageCount', 'SubscriptionCount')


class NWS(object):
    """
    The NWS object has methods for getting, updating, deleting information
    about channels, subscriptions, endpoints, and templates.
    """
    def __init__(self, override_user=None):
        self.override_user = override_user
        self._re_uuid = re.compile(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        self._re_regid = re.compile(r'^[A-F0-9]{32}$', re.I)
        self._re_subscriber_id = re.compile(
            r'^([a-z]adm_)?[a-z][a-z0-9]{0,7}(@washington.edu)?$', re.I)
        self._re_protocol = re.compile(r'^(Email|SMS)$', re.I)

    def get_endpoints(self, first_result=1, max_results=10):
        """
        Search for all endpoints
        """
        url = "/notification/v1/endpoint?first_result=%s&max_results=%s" % (
            first_result, max_results)

        response = NWS_DAO().getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        endpoints = []
        for datum in data.get("Endpoints", []):
            endpoints.append(self._endpoint_from_json(datum))
        return endpoints

    def get_endpoint_by_endpoint_id(self, endpoint_id):
        """
        Get an endpoint by endpoint id
        """
        self._validate_uuid(endpoint_id)

        url = "/notification/v1/endpoint/%s" % (endpoint_id)

        response = NWS_DAO().getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return self._endpoint_from_json(data.get("Endpoint"))

    def get_endpoint_by_subscriber_id_and_protocol(
            self, subscriber_id, protocol):
        """
        Get an endpoint by subscriber_id and protocol
        """
        self._validate_subscriber_id(subscriber_id)
        self._validate_endpoint_protocol(protocol)

        url = "/notification/v1/endpoint?subscriber_id=%s&protocol=%s" % (
            subscriber_id, protocol)

        response = NWS_DAO().getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        try:
            return self._endpoint_from_json(data.get("Endpoints")[0])
        except IndexError:
            raise DataFailureException(url, 404, "No SMS endpoint found")

    def get_endpoint_by_address(self, endpoint_addr):
        """
        Get an endpoint by address
        """
        url = "/notification/v1/endpoint?endpoint_address=%s" % endpoint_addr

        response = NWS_DAO().getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        try:
            return self._endpoint_from_json(data.get("Endpoints")[0])
        except IndexError:
            raise DataFailureException(url, 404, "No SMS endpoint found")

    def get_endpoints_by_subscriber_id(self, subscriber_id):
        """
        Search for all endpoints by a given subscriber
        """
        self._validate_subscriber_id(subscriber_id)

        url = "/notification/v1/endpoint?subscriber_id=%s" % (subscriber_id)

        response = NWS_DAO().getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)

        endpoints = []
        for datum in data.get("Endpoints", []):
            endpoints.append(self._endpoint_from_json(datum))
        return endpoints

    def resend_sms_endpoint_verification(self, endpoint_id):
        """
        Calls NWS function to resend verification message to endpoint's
        phone number
        """
        self._validate_uuid(endpoint_id)

        url = "/notification/v1/endpoint/%s/verification" % (endpoint_id)

        response = NWS_DAO().postURL(url, None, None)

        if response.status != 202:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def delete_endpoint(self, endpoint_id):
        """
        Deleting an existing endpoint
        :param endpoint_id: is the endpoint that the client wants to delete
        """
        self._validate_uuid(endpoint_id)

        url = "/notification/v1/endpoint/%s" % (endpoint_id)
        headers = {}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        response = NWS_DAO().deleteURL(url, headers)

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def update_endpoint(self, endpoint):
        """
        Update an existing endpoint
        :param endpoint: is the updated endpoint the client wants to update
        """
        self._validate_uuid(endpoint.endpoint_id)
        self._validate_subscriber_id(endpoint.user)

        url = "/notification/v1/endpoint/%s" % (endpoint.endpoint_id)
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        response = NWS_DAO().putURL(url, headers, endpoint.json_data())

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def create_new_endpoint(self, endpoint):
        """
        Create a new endpoint
        :param endpoint: is the new endpoint that the client wants to create
        """
        self._validate_subscriber_id(endpoint.user)

        url = "/notification/v1/endpoint"
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        response = NWS_DAO().postURL(url, headers, endpoint.json_data())

        if response.status != 201:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def _endpoint_from_json(self, json_data):
        endpoint = Endpoint()
        endpoint.endpoint_id = json_data["EndpointID"]
        endpoint.endpoint_uri = json_data["EndpointURI"]
        endpoint.endpoint_address = json_data["EndpointAddress"]
        endpoint.carrier = json_data.get("Carrier")
        endpoint.protocol = json_data["Protocol"]
        endpoint.user = json_data["SubscriberID"]
        endpoint.owner = json_data["OwnerID"]
        endpoint.active = json_data["Active"]
        if "Created" in json_data:
            endpoint.created = dateutil.parser.parse(json_data["Created"])
        if "LastModified" in json_data:
            endpoint.last_modified = dateutil.parser.parse(
                json_data["LastModified"])
        endpoint.modified_by = json_data.get("ModifiedBy")
        return endpoint

    def _validate_uuid(self, uuid):
        if (uuid is None or not self._re_uuid.match(str(uuid))):
            raise InvalidUUID(uuid)

    def _validate_regid(self, regid):
        if (regid is None or not self._re_regid.match(str(regid))):
            raise InvalidRegID(regid)

    def _validate_subscriber_id(self, subscriber_id):
        if (subscriber_id is None or
                not self._re_subscriber_id.match(str(subscriber_id))):
            raise InvalidNetID(subscriber_id)

    def _validate_endpoint_protocol(self, protocol):
        if (protocol is None or not self._re_protocol.match(str(protocol))):
            raise InvalidEndpointProtocol(protocol)
