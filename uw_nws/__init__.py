"""
This is the interface for interacting with the Notifications Web Service.
"""

from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)
from uw_nws.exceptions import (
    InvalidUUID, InvalidEndpointProtocol, InvalidSurrogateID)
from uw_nws.dao import NWS_DAO
from uw_nws.models import Person, Channel, Endpoint, Subscription, MessageType
from urllib.parse import quote, urlencode
from datetime import datetime, time
import json
import re

MANAGED_ATTRIBUTES = (
    'DispatchedEmailCount', 'DispatchedTextMessageCount',
    'SentTextMessageCount', 'SubscriptionCount')
API = "/notification/v1"


class NWS(object):
    """
    The NWS object has methods for getting, updating, deleting information
    about channels, subscriptions, endpoints, and templates.
    """
    def __init__(self, actas_user=None):
        self.actas_user = actas_user
        self._re_uuid = re.compile(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        self._re_regid = re.compile(r'^[A-F0-9]{32}$', re.I)
        self._re_subscriber_id = re.compile(
            r'^([a-z]adm_)?[a-z][a-z0-9]{0,7}(@washington.edu)?$', re.I)
        self._re_protocol = re.compile(r'^(Email|SMS)$', re.I)
        self._re_message_type_surrogate = re.compile(
            r'^uw_[a-z0-9|_]{1,37}$', re.I)
        self._read_headers = {"Accept": "application/json"}

    def _write_headers(self):
        write_headers = {"Content-Type": "application/json"}
        if self.actas_user is not None:
            write_headers["X_UW_ACT_AS"] = self.actas_user
        return write_headers

    def get_endpoint_by_endpoint_id(self, endpoint_id):
        """
        Get an endpoint by endpoint id
        """
        self._validate_uuid(endpoint_id)

        url = "{}/endpoint/{}".format(API, endpoint_id)

        response = NWS_DAO().getURL(url, self._read_headers)
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return Endpoint.from_json(data.get("Endpoint"))

    def get_endpoint_by_subscriber_id_and_protocol(
            self, subscriber_id, protocol):
        """
        Get an endpoint by subscriber_id and protocol
        """
        self._validate_subscriber_id(subscriber_id)
        self._validate_endpoint_protocol(protocol)

        url = "{}/endpoint?subscriber_id={}&protocol={}".format(
            API, subscriber_id, protocol)

        response = NWS_DAO().getURL(url, self._read_headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        try:
            return Endpoint.from_json(data.get("Endpoints")[0])
        except IndexError:
            raise DataFailureException(url, 404, "No SMS endpoint found")

    def get_endpoint_by_address(self, endpoint_addr):
        """
        Get an endpoint by address
        """
        url = "{}/endpoint?endpoint_address={}".format(API, endpoint_addr)

        response = NWS_DAO().getURL(url, self._read_headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        try:
            return Endpoint.from_json(data.get("Endpoints")[0])
        except IndexError:
            raise DataFailureException(url, 404, "No SMS endpoint found")

    def get_endpoints_by_subscriber_id(self, subscriber_id):
        """
        Search for all endpoints by a given subscriber
        """
        self._validate_subscriber_id(subscriber_id)

        url = "{}/endpoint?subscriber_id={}".format(API, subscriber_id)

        response = NWS_DAO().getURL(url, self._read_headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)

        endpoints = []
        for datum in data.get("Endpoints", []):
            endpoints.append(Endpoint.from_json(datum))
        return endpoints

    def resend_sms_endpoint_verification(self, endpoint_id):
        """
        Calls NWS function to resend verification message to endpoint's
        phone number
        """
        self._validate_uuid(endpoint_id)

        url = "{}/endpoint/{}/verification".format(API, endpoint_id)

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

        url = "{}/endpoint/{}".format(API, endpoint_id)
        response = NWS_DAO().deleteURL(url, self._write_headers())

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def update_endpoint(self, endpoint):
        """
        Update an existing endpoint
        :param endpoint: is the updated endpoint the client wants to update
        """
        self._validate_uuid(endpoint.endpoint_id)
        self._validate_subscriber_id(endpoint.subscriber_id)

        url = "{}/endpoint/{}".format(API, endpoint.endpoint_id)
        response = NWS_DAO().putURL(
            url, self._write_headers(), self._json_body(endpoint.json_data()))

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def create_endpoint(self, endpoint):
        """
        Create a new endpoint
        :param endpoint: is the new endpoint that the client wants to create
        """
        self._validate_subscriber_id(endpoint.subscriber_id)

        url = "{}/endpoint".format(API)
        response = NWS_DAO().postURL(
            url, self._write_headers(), self._json_body(endpoint.json_data()))

        if response.status != 201:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def create_new_endpoint(self, endpoint):
        return self.create_endpoint(endpoint)

    def delete_subscription(self, subscription_id):
        """
        Deleting an existing subscription
        :param subscription_id: is the subscription the client wants to delete
        """
        self._validate_uuid(subscription_id)

        url = "{}/subscription/{}".format(API, subscription_id)
        response = NWS_DAO().deleteURL(url, self._write_headers())

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def create_subscription(self, subscription):
        """
        Create a new subscription
        :param subscription: the new subscription the client wants to create
        """
        if subscription.subscription_id is not None:
            self._validate_uuid(subscription.subscription_id)

        if subscription.endpoint is not None:
            if subscription.endpoint.subscriber_id is not None:
                self._validate_subscriber_id(
                    subscription.endpoint.subscriber_id)

            if subscription.endpoint.endpoint_id is not None:
                self._validate_uuid(subscription.endpoint.endpoint_id)

        if subscription.channel is not None:
            self._validate_uuid(subscription.channel.channel_id)

        url = "{}/subscription".format(API)
        response = NWS_DAO().postURL(url, self._write_headers(),
                                     self._json_body(subscription.json_data()))

        if response.status != 201:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def create_new_subscription(self, subscription):
        return self.create_subscription(subscription)

    def get_subscriptions_by_channel_id(self, channel_id):
        """
        Search for all subscriptions on a given channel
        """
        return self.search_subscriptions(channel_id=channel_id)

    def get_subscriptions_by_subscriber_id(
            self, subscriber_id, max_results=10):
        """
        Search for all subscriptions by a given subscriber
        """
        return self.search_subscriptions(
            subscriber_id=subscriber_id, max_results=max_results)

    def get_subscriptions_by_channel_id_and_subscriber_id(
            self, channel_id, subscriber_id):
        """
        Search for all subscriptions by a given channel and subscriber
        """
        return self.search_subscriptions(
            channel_id=channel_id, subscriber_id=subscriber_id)

    def get_subscriptions_by_channel_id_and_person_id(
            self, channel_id, person_id):
        """
        Search for all subscriptions by a given channel and person
        """
        return self.search_subscriptions(
            channel_id=channel_id, person_id=person_id)

    def get_subscription_by_channel_id_and_endpoint_id(
            self, channel_id, endpoint_id):
        """
        Search for subscription by a given channel and endpoint
        """
        subscriptions = self.search_subscriptions(
            channel_id=channel_id, endpoint_id=endpoint_id)

        try:
            return subscriptions[0]
        except IndexError:
            raise DataFailureException(url, 404, "No subscription found")

    def search_subscriptions(self, **kwargs):
        """
        Search for all subscriptions by parameters
        """
        params = [(key, kwargs[key]) for key in sorted(kwargs.keys())]
        url = "{}/subscription?{}".format(API, urlencode(params, doseq=True))

        response = NWS_DAO().getURL(url, self._read_headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        subscriptions = []
        for datum in data.get("Subscriptions", []):
            subscriptions.append(Subscription.from_json(datum))
        return subscriptions

    def get_channel_by_channel_id(self, channel_id):
        """
        Get a channel by channel id
        """
        self._validate_uuid(channel_id)

        url = "{}/channel/{}".format(API, channel_id)

        response = NWS_DAO().getURL(url, self._read_headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return Channel.from_json(data.get("Channel"))

    def get_channels_by_sln(self, channel_type, sln):
        """
        Search for all channels by sln
        """
        return self.search_channels(type=channel_type, tag_sln=sln)

    def get_channels_by_sln_year_quarter(
            self, channel_type, sln, year, quarter):
        """
        Search for all channels by sln, year and quarter
        """
        return self.search_channels(
            type=channel_type, tag_sln=sln, tag_year=year, tag_quarter=quarter)

    def get_active_channels_by_year_quarter(
            self, channel_type, year, quarter, expires=None):
        """
        Search for all active channels by year and quarter
        """
        if expires is None:
            # Set expires_after to midnight of current day
            expires = datetime.combine(datetime.utcnow().date(), time.min)

        return self.search_channels(
            type=channel_type, tag_year=year, tag_quarter=quarter,
            expires_after=expires.isoformat())

    def search_channels(self, **kwargs):
        """
        Search for all channels by parameters
        """
        params = [(key, kwargs[key]) for key in sorted(kwargs.keys())]
        url = "{}/channel?{}".format(API, urlencode(params, doseq=True))

        response = NWS_DAO().getURL(url, self._read_headers)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        channels = []
        for datum in data.get("Channels", []):
            channels.append(Channel.from_json(datum))
        return channels

    def get_person_by_surrogate_id(self, surrogate_id):
        self._validate_subscriber_id(surrogate_id)
        return self._get_person_by_id(surrogate_id)

    def get_person_by_uwregid(self, uwregid):
        self._validate_regid(uwregid)
        return self._get_person_by_id(uwregid)

    def _get_person_by_id(self, identifier):
        url = "{}/person/{}".format(API, identifier)

        response = NWS_DAO().getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return Person.from_json(data.get("Person"))

    def create_person(self, person):
        """
        Create a new person
        :param person: is the new person that the client wants to crete
        """
        self._validate_subscriber_id(person.surrogate_id)

        url = "{}/person".format(API)
        response = NWS_DAO().postURL(
            url, self._write_headers(), self._json_body(person.json_data()))

        if response.status != 201:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def create_new_person(self, person):
        return self.create_person(person)

    def update_person(self, person):
        """
        Update an existing person
        :param person: is the updated person that the client wants to update
        """
        self._validate_regid(person.person_id)
        self._validate_subscriber_id(person.surrogate_id)

        for attr in MANAGED_ATTRIBUTES:
            person.attributes.pop(attr, None)

        url = "{}/person/{}".format(API, person.person_id)
        response = NWS_DAO().putURL(
            url, self._write_headers(), self._json_body(person.json_data()))

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def create_new_dispatch(self, dispatch):
        """
        Create a new dispatch
        :param dispatch:
        is the new dispatch that the client wants to create
        """
        self._validate_uuid(dispatch.dispatch_id)

        # Create new dispatch
        url = "{}/dispatch".format(API)
        post_response = NWS_DAO().postURL(
            url, self._write_headers(), self._json_body(dispatch.json_data()))

        if post_response.status != 200:
            raise DataFailureException(
                url, post_response.status, post_response.data)
        return post_response.status

    def delete_dispatch(self, dispatch_id):
        """
        Deleting an existing dispatch
        :param dispatch_id: is the dispatch that the client wants to delete
        """
        self._validate_uuid(dispatch_id)

        url = "{}/dispatch/{}".format(API, dispatch_id)
        response = NWS_DAO().deleteURL(url, self._write_headers())

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def get_message_type_by_id(self, message_type_id):
        """
        Get a message type by message type ID
        :param message_type_id: is the message type that
                                the client wants to retrieve
        """
        self._validate_uuid(message_type_id)

        url = "{}/message-type/{}".format(API, message_type_id)
        response = NWS_DAO().getURL(url, self._write_headers())
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        data = json.loads(response.data)
        return MessageType.from_json(data.get("MessageType"))

    def update_message_type(self, message_type):
        """
        Update an existing message type
        :param message_type: is the updated message type that the
                             client wants to update
        """
        self._validate_uuid(message_type.message_type_id)

        url = "{}/message-type/{}".format(API, message_type.message_type_id)
        response = NWS_DAO().putURL(
            url, self._write_headers(), self._json_body(
                message_type.json_data()))

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def delete_message_type(self, message_type_id):
        """
        Delete an existing message type
        :param message_type_id: is the id of the message type the
                                client wants to delete
        """
        self._validate_uuid(message_type_id)

        url = "{}/message-type/{}".format(API, message_type_id)
        response = NWS_DAO().deleteURL(url, self._write_headers())

        if response.status != 204:
            raise DataFailureException(url, response.status, response.data)
        return response.status

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

    def _validate_message_type_surrogate(self, surrogate_id):
        if (surrogate_id is None or
                not self._re_message_type_surrogate.match(str(surrogate_id))):
            raise InvalidSurrogateID(surrogate_id)

    def _json_body(self, json_data):
        return json.dumps(json_data)
