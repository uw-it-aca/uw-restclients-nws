from unittest import TestCase
from uw_nws import NWS
from uw_nws.models import Subscription, Endpoint, Channel
from uw_nws.utilities import fdao_nws_override
from uw_nws.exceptions import InvalidUUID
from restclients_core.exceptions import DataFailureException, InvalidNetID


@fdao_nws_override
class NWSTestSubscription(TestCase):
    def _setup_subscription(self):
        subscription = Subscription()
        subscription.subscription_id = "c4597f93-0f62-4feb-ac88-af5f0329001f"
        subscription.modified_by = "javerage@washington.edu"
        subscription.endpoint = Endpoint()
        subscription.endpoint.endpoint_address = "javerage0@uw.edu"
        subscription.endpoint.protocol = "Email"
        subscription.endpoint.subscriber_id = "javerage@washington.edu"
        subscription.endpoint.owner = "javerage@washington.edu"
        subscription.channel = Channel()
        subscription.channel.channel_id = (
            "b779df7b-d6f6-4afb-8165-8dbe6232119f")
        return subscription

    def test_default_subscription(self):
        subscription = Subscription()
        self.assertEquals(subscription.subscription_id, None)

    def test_subscriptions_channel_id(self):
        nws = NWS()
        subscriptions = nws.get_subscriptions_by_channel_id(
            "b779df7b-d6f6-4afb-8165-8dbe6232119f")
        self.assertEquals(len(subscriptions), 5)

    def test_subscriptions_channel_id_and_endpoint_id(self):
        nws = NWS()
        subscription = nws.get_subscription_by_channel_id_and_endpoint_id(
            "b779df7b-d6f6-4afb-8165-8dbe6232119f",
            "780f2a49-2118-4969-9bef-bbd38c26970a")

        self.assertEquals(subscription.endpoint.endpoint_id,
                          "780f2a49-2118-4969-9bef-bbd38c26970a")

        self.assertRaises(
            DataFailureException,
            nws.get_subscription_by_channel_id_and_endpoint_id,
            "b779df7b-d6f6-4afb-8165-8dbe6232119f",
            "000f2a49-2118-4969-9bef-bbd38c26970a")

    def test_subscriptions_subscriber_id(self):
        nws = NWS()
        subscriptions = nws.get_subscriptions_by_subscriber_id(
            "javerage", max_results=10)
        self.assertEquals(len(subscriptions), 5)

        self.assertRaises(
            DataFailureException, nws.get_subscriptions_by_subscriber_id,
            "bill")

    def test_subscriptions_channel_id_subscriber_id(self):
        nws = NWS()
        subscriptions = nws.get_subscriptions_by_channel_id_and_subscriber_id(
            "b779df7b-d6f6-4afb-8165-8dbe6232119f", "javerage")
        self.assertEquals(len(subscriptions), 5)

    def test_subscriptions_channel_id_person_id(self):
        nws = NWS()
        subscriptions = nws.get_subscriptions_by_channel_id_and_person_id(
            "b779df7b-d6f6-4afb-8165-8dbe6232119f",
            "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEquals(len(subscriptions), 5)

    def test_create_subscription(self):
        subscription = self._setup_subscription()

        nws = NWS(actas_user="javerage")
        self.assertRaises(
            DataFailureException, nws.create_subscription, subscription)

        subscription.endpoint.endpoint_id = "abc"
        self.assertRaises(
            InvalidUUID, nws.create_subscription, subscription)

    def test_create_invalid_subscriber_id_subscription(self):
        subscription = self._setup_subscription()
        subscription.endpoint.subscriber_id = "-@#$ksjdsfkli13290243290490"

        nws = NWS()
        self.assertRaises(
            InvalidNetID, nws.create_subscription, subscription)

    def test_create_empty_channelid_subscription(self):
        subscription = self._setup_subscription()
        subscription.channel.channel_id = None

        nws = NWS()
        self.assertRaises(
            InvalidUUID, nws.create_subscription, subscription)

    def test_delete_subscription(self):
        nws = NWS(actas_user="javerage")
        self.assertRaises(
            DataFailureException, nws.delete_subscription,
            "652236c6-a85a-4845-8dc5-3e518bec044c")

    def test_delete_invalid_subscription(self):
        nws = NWS()
        self.assertRaises(
            InvalidUUID, nws.delete_subscription,
            "652236c6-a85a-4845-8dc5-3e518bec044")

    def test_subscriber_id_validation(self):
        nws = NWS()
        nws._validate_subscriber_id('javerage')
        nws._validate_subscriber_id('javerage@washington.edu')

        self.assertRaises(
            InvalidNetID, nws._validate_subscriber_id, '00ok')
        self.assertRaises(
            InvalidNetID, nws._validate_subscriber_id, 'ok123456789')
        self.assertRaises(
            InvalidNetID, nws._validate_subscriber_id, 'javerage@gmail.com')
        self.assertRaises(
            InvalidNetID, nws._validate_subscriber_id, 'javerage@')

    def test_json_data(self):
        subscription = self._setup_subscription()
        data = subscription.json_data()

        self.assertEquals(
            data["Subscription"]["SubscriptionID"],
            "c4597f93-0f62-4feb-ac88-af5f0329001f")
        self.assertEquals(
            data["Subscription"]["Endpoint"]["Protocol"], "Email")
        self.assertEquals(
            data["Subscription"]["Channel"]["ChannelID"],
            "b779df7b-d6f6-4afb-8165-8dbe6232119f")
        self.assertEquals(data["Subscription"]["ModifiedBy"],
                          "javerage@washington.edu")
