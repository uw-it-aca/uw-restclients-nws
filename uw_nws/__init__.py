"""
This is the interface for interacting with the Notifications Web Service.
"""

from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)
from uw_nws.exceptions import InvalidUUID, InvalidEndpointProtocol
from uw_nws.dao import NWS_DAO
from uw_nws.models import (
    Person, Channel, Endpoint, Subscription, CourseAvailableEvent)
from uw_sws.term import get_current_term, get_term_after
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
        self._headers = {"Accept": "application/json"}

    def get_endpoints(self, first_result=1, max_results=10):
        """
        Search for all endpoints
        """
        url = "/notification/v1/endpoint?first_result=%s&max_results=%s" % (
            first_result, max_results)

        response = NWS_DAO().getURL(url, self._headers)

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

        response = NWS_DAO().getURL(url, self._headers)
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

        response = NWS_DAO().getURL(url, self._headers)

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

        response = NWS_DAO().getURL(url, self._headers)

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

        response = NWS_DAO().getURL(url, self._headers)

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

    def delete_subscription(self, subscription_id):
        """
        Deleting an existing subscription
        :param subscription_id: is the subscription the client wants to delete
        """
        self._validate_uuid(subscription_id)

        url = "/notification/v1/subscription/%s" % (subscription_id)
        headers = {}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        response = NWS_DAO().deleteURL(url, headers)

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def create_new_channel(self, channel):
        """
        Create a new channel
        :param channel: is the new channel that the client wants to create
        """
        url = "/notification/v1/channel"
        headers = {"Content-Type": "application/json"}
        response = NWS_DAO().postURL(
            url, headers, channel.json_data())

        if response.status != 201:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def update_channel(self, channel):
        """
        Update an existing channel
        :param channel: is the updated channel that the client wants to update
        """
        url = "/notification/v1/channel/%s" % (channel.channel_id)
        headers = {"Content-Type": "application/json"}
        response = NWS_DAO().putURL(url, headers, channel.json_data())

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def delete_channel(self, channel_id):
        """
        Deleting an existing channel
        :param channel_id: is the channel that the client wants to delete
        """
        self._validate_uuid(channel_id)

        url = "/notification/v1/channel/%s" % (channel_id)
        response = NWS_DAO().deleteURL(url, None)

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def get_channel_by_channel_id(self, channel_id):
        """
        Get a channel by channel id
        """
        self._validate_uuid(channel_id)

        url = "/notification/v1/channel/%s" % (channel_id)

        response = NWS_DAO().getURL(url, self._headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return self._channel_from_json(data.get("Channel"))

    def get_channel_by_surrogate_id(self, channel_type, surrogate_id):
        """
        Get a channel by surrogate id
        """
        key = "%s|%s" % (channel_type, surrogate_id)
        url = "/notification/v1/channel/%s" % quote(key)

        response = NWS_DAO().getURL(url, self._headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return self._channel_from_json(data.get("Channel"))

    def get_channels_by_sln(self, channel_type, sln):
        """
        Search for all channels by sln
        """
        url = "/notification/v1/channel?type=%s&tag_sln=%s" % (
            channel_type, sln)

        response = NWS_DAO().getURL(url, self._headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        channels = []
        for datum in data.get("Channels", []):
            channels.append(self._channel_from_json(datum))
        return channels

    def get_channels_by_sln_year_quarter(
            self, channel_type, sln, year, quarter):
        """
        Search for all channels by sln, year and quarter
        """
        url = ("/notification/v1/channel?type=%s&"
               "tag_sln=%s&tag_year=%s&tag_quarter=%s") % (
                channel_type, sln, year, quarter)

        response = NWS_DAO().getURL(url, self._headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        channels = []
        for datum in data.get("Channels", []):
            channels.append(self._channel_from_json(datum))
        return channels

    def term_has_active_channel(self, channel_type, term):
        """
        Checks to see if there exists a channel for the given sws.Term object's
        year and quarter.
        """
        # Sets now to midnight of current day to allow for caching
        now = datetime.combine(datetime.utcnow().date(), time.min).isoformat()

        url = ("/notification/v1/channel?tag_year=%s&"
               "tag_quarter=%s&max_results=1&expires_after=%s") % (
                term.year, term.quarter, now)

        response = NWS_DAO().getURL(url, self._headers)

        if response.status != 200:
            return False

        data = json.loads(response.data)
        if data.get("TotalCount", 0) > 0:
            return True

        return False

    def get_terms_with_active_channels(self, channel_type):
        """
        Returns a list of all sws.Terms that have active channels.
        """
        # Check the current term, and the next 3, to see if they have
        # a channel for any course in that term.
        # when the sws term resource provides us with a timeschedule publish
        # date, use that instead of this.
        term = get_current_term()
        terms = []
        if self.term_has_active_channel(channel_type, term):
            terms.append(term)

        for i in range(3):
            term = get_term_after(term)
            if self.term_has_active_channel(channel_type, term):
                terms.append(term)

        return terms

    def get_channels(self, first_result=1, max_results=10):
        """
        Search for all channels
        """
        url = "/notification/v1/channel?first_result=%s&max_results=%s" % (
            first_result, max_results)

        response = NWS_DAO().getURL(url, self._headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        channels = []
        for datum in data.get("Channels", []):
            channels.append(self._channel_from_json(datum))
        return channels

    def get_person_by_surrogate_id(self, surrogate_id):
        self._validate_subscriber_id(surrogate_id)
        return self._get_person_by_id(surrogate_id)

    def get_person_by_uwregid(self, uwregid):
        self._validate_regid(uwregid)
        return self._get_person_by_id(uwregid)

    def _get_person_by_id(self, identifier):
        url = "/notification/v1/person/%s" % identifier

        response = NWS_DAO().getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return self._person_from_json(data.get("Person"))

    def create_new_person(self, person):
        """
        Create a new person
        :param person: is the new person that the client wants to crete
        """
        self._validate_subscriber_id(person.surrogate_id)

        url = "/notification/v1/person"
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        response = NWS_DAO().postURL(url, headers, person.json_data())

        if response.status != 201:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def update_person(self, person):
        """
        Update an existing person
        :param person: is the updated person that the client wants to update
        """
        self._validate_regid(person.person_id)
        self._validate_subscriber_id(person.surrogate_id)

        for attr in MANAGED_ATTRIBUTES:
            person.attributes.pop(attr, None)

        url = "/notification/v1/person/%s" % person.person_id
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        response = NWS_DAO().putURL(url, headers, person.json_data())

        if response.status != 204:
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
        endpoint.default = json_data.get("Default")
        if "Created" in json_data:
            endpoint.created = dateutil.parser.parse(json_data["Created"])
        if "LastModified" in json_data:
            endpoint.last_modified = dateutil.parser.parse(
                json_data["LastModified"])
        endpoint.modified_by = json_data.get("ModifiedBy")
        return endpoint

    def _person_from_json(self, json_data):
        person = Person()
        person.person_id = json_data["PersonID"]
        person.person_uri = json_data["PersonURI"]
        person.surrogate_id = json_data["SurrogateID"]
        if "Created" in json_data:
            person.created = dateutil.parser.parse(json_data["Created"])
        if "LastModified" in json_data:
            person.last_modified = dateutil.parser.parse(
                json_data["LastModified"])
        person.modified_by = json_data.get("ModifiedBy")

        for key, val in json_data.get("Attributes", {}).iteritems():
            person.attributes[key] = val

        for endpoint_data in json_data.get("Endpoints", []):
            person.endpoints.append(self._endpoint_from_json(endpoint_data))

        return person

    def _channel_from_json(self, json_data):
        channel = Channel()
        channel.channel_id = json_data["ChannelID"]
        channel.channel_uri = json_data["ChannelURI"]
        channel.surrogate_id = json_data["SurrogateID"]
        channel.type = json_data["Type"]
        channel.name = json_data["Name"]
        channel.description = json_data["Description"]
        if "Expires" in json_data:
            channel.expires = dateutil.parser.parse(json_data["Expires"])
        if "Created" in json_data:
            channel.created = dateutil.parser.parse(json_data["Created"])
        if "LastModified" in json_data:
            channel.last_modified = dateutil.parser.parse(
                json_data["LastModified"])
        channel.modified_by = json_data.get("ModifiedBy")

        for key, val in json_data.get("Tags", {}).iteritems():
            channel.tags[key] = val

        return channel

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
