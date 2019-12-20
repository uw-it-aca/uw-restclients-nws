from restclients_core import models
import dateutil.parser


class Person(models.Model):
    person_id = models.CharField(max_length=40)
    person_uri = models.CharField(max_length=200)
    surrogate_id = models.CharField(max_length=80)
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self.attributes = {}
        self.endpoints = []

    @staticmethod
    def from_json(json_data):
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
        person.attributes = json_data.get("Attributes", {})

        for endpoint_data in json_data.get("Endpoints", []):
            person.endpoints.append(Endpoint.from_json(endpoint_data))
        return person

    def accepted_tos(self):
        return self.attributes.get("AcceptedTermsOfUse", False)

    def default_endpoint(self):
        for endpoint in self.endpoints:
            if endpoint.default:
                return endpoint

    def has_valid_endpoints(self):
        endpoints = {"sms": False, "email": False}
        for endpoint in self.endpoints:
            endpoints[endpoint.protocol.lower()] = True
        return endpoints

    def get_verified_endpoints(self):
        verified_endpoints = {}
        for endpoint in self.endpoints:
            if endpoint.is_verified():
                verified_endpoints[endpoint.protocol.lower()] = endpoint
        return verified_endpoints

    def json_data(self):
        return {
            "Person": {
                "PersonID": self.person_id,
                "PersonURI": self.person_uri,
                "SurrogateID": self.surrogate_id,
                "Created": self.created.isoformat() if (
                    self.created is not None) else None,
                "LastModified": self.last_modified.isoformat() if (
                    self.last_modified is not None) else None,
                "ModifiedBy": self.modified_by,
                "Attributes": self.attributes,
                "Endpoints": [e.json_data()["Endpoint"] for e in (
                    self.endpoints)]
            }
        }


class Channel(models.Model):
    channel_id = models.CharField(max_length=40, default=None)
    channel_uri = models.CharField(max_length=200)
    surrogate_id = models.CharField(max_length=80)
    type = models.CharField(max_length=40)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=200)
    expires = models.DateTimeField()
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)
        self.tags = {}

    @staticmethod
    def from_json(json_data):
        channel = Channel()
        channel.channel_id = json_data["ChannelID"]
        channel.channel_uri = json_data["ChannelURI"]
        channel.surrogate_id = json_data["SurrogateID"]
        channel.type = json_data["Type"]
        channel.name = json_data["Name"]
        channel.description = json_data.get("Description")
        if "Expires" in json_data:
            channel.expires = dateutil.parser.parse(json_data["Expires"])
        if "Created" in json_data:
            channel.created = dateutil.parser.parse(json_data["Created"])
        if "LastModified" in json_data:
            channel.last_modified = dateutil.parser.parse(
                json_data["LastModified"])
        channel.modified_by = json_data.get("ModifiedBy")
        channel.tags = json_data.get("Tags", {})
        return channel

    def json_data(self):
        return {
            "Channel": {
                "ChannelID": self.channel_id,
                "ChannelURI": self.channel_uri,
                "SurrogateID": self.surrogate_id,
                "Type": self.type,
                "Name": self.name,
                "Description": self.description,
                "Expires": self.expires.isoformat() if (
                    self.expires is not None) else None,
                "Created": self.created.isoformat() if (
                    self.created is not None) else None,
                "LastModified": self.last_modified.isoformat() if (
                    self.last_modified is not None) else None,
                "ModifiedBy": self.modified_by,
                "Tags": self.tags
            }
        }


class Endpoint(models.Model):
    endpoint_id = models.CharField(max_length=40, default=None)
    endpoint_uri = models.CharField(max_length=200)
    endpoint_address = models.CharField(max_length=200)
    carrier = models.CharField(max_length=40)
    protocol = models.SlugField(max_length=40)
    subscriber_id = models.CharField(max_length=20)
    owner = models.CharField(max_length=20)
    status = models.CharField(max_length=40)
    active = models.NullBooleanField()
    default = models.NullBooleanField()
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)

    def is_verified(self):
        return (self.status is not None and self.status.lower() == 'verified')

    @staticmethod
    def from_json(json_data):
        endpoint = Endpoint()
        endpoint.endpoint_id = json_data["EndpointID"]
        endpoint.endpoint_uri = json_data["EndpointURI"]
        endpoint.endpoint_address = json_data["EndpointAddress"]
        endpoint.carrier = json_data.get("Carrier")
        endpoint.protocol = json_data["Protocol"]
        endpoint.subscriber_id = json_data["SubscriberID"]
        endpoint.owner = json_data["OwnerID"]
        endpoint.status = json_data["Status"]
        endpoint.active = json_data["Active"]
        endpoint.default = json_data.get("Default")
        if "Created" in json_data:
            endpoint.created = dateutil.parser.parse(json_data["Created"])
        if "LastModified" in json_data:
            endpoint.last_modified = dateutil.parser.parse(
                json_data["LastModified"])
        endpoint.modified_by = json_data.get("ModifiedBy")
        return endpoint

    def get_user_net_id(self):
        return self.subscriber_id

    def get_owner_net_id(self):
        return self.owner

    def json_data(self):
        return {
            "Endpoint": {
                "EndpointID": self.endpoint_id,
                "EndpointURI": self.endpoint_uri,
                "EndpointAddress": self.endpoint_address,
                "Carrier": self.carrier,
                "Protocol": self.protocol,
                "SubscriberID": self.subscriber_id,
                "OwnerID": self.owner,
                "Status": self.status,
                "Active": self.active,
                "Default": self.default,
                "Created": self.created.isoformat() if (
                    self.created is not None) else None,
                "LastModified": self.last_modified.isoformat() if (
                    self.last_modified is not None) else None,
                "ModifiedBy": self.modified_by
            }
        }


class Subscription(models.Model):
    subscription_id = models.CharField(max_length=40, default=None)
    subscription_uri = models.CharField(max_length=200)
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)
        self.channel = None
        self.endpoint = None

    @staticmethod
    def from_json(json_data):
        subscription = Subscription()
        subscription.subscription_id = json_data["SubscriptionID"]
        subscription.subscription_uri = json_data["SubscriptionURI"]
        if json_data.get("Created", None) is not None:
            subscription.created = dateutil.parser.parse(json_data["Created"])
        if json_data.get("LastModified", None) is not None:
            subscription.last_modified = dateutil.parser.parse(
                json_data["LastModified"])
        subscription.modified_by = json_data.get("ModifiedBy")

        if json_data.get("Endpoint", None) is not None:
            subscription.endpoint = Endpoint.from_json(json_data["Endpoint"])

        if json_data.get("Channel", None) is not None:
            subscription.channel = Channel.from_json(json_data["Channel"])
        return subscription

    def json_data(self):
        return {
            "Subscription": {
                "SubscriptionID": self.subscription_id,
                "SubscriptionURI": self.subscription_uri,
                "Created": self.created.isoformat() if (
                    self.created is not None) else None,
                "LastModified": self.last_modified.isoformat() if (
                    self.last_modified is not None) else None,
                "ModifiedBy": self.modified_by,
                "Channel": self.channel.json_data()["Channel"] if (
                    self.channel is not None) else None,
                "Endpoint": self.endpoint.json_data()["Endpoint"] if (
                    self.endpoint is not None) else None
            }
        }


class Dispatch(models.Model):
    dispatch_id = models.CharField(max_length=40, default=None)
    dispatch_uri = models.CharField(max_length=200)
    message_type = models.CharField(max_length=40)
    content = models.CharField(max_length=80)
    directive = models.CharField(max_length=20)
    number_of_recipients = models.IntegerField()
    locked = models.BooleanField()
    lock_id = models.CharField(max_length=40)
    locked_on = models.DateTimeField()
    locked_by = models.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        self.message = {}

    def json_data(self):
        return {
            "Dispatch": {
                "DispatchID": self.dispatch_id,
                "DispatchURI": self.dispatch_uri,
                "Message": self.message,
                "Content": self.content,
                "Directive": self.directive,
                "NumberOfRecipients": self.number_of_recipients,
                "Locked": self.locked,
                "LockID": self.lock_id,
                "LockedOn": self.locked_on,
                "LockedBy": self.locked_by
            }
        }


class MessageType(models.Model):
    message_type_id = models.CharField(max_length=40, default=None)
    message_type_uri = models.CharField(max_length=200)
    surrogate_id = models.CharField(max_length=40)
    content_type = models.CharField(max_length=40)
    destination_id = models.CharField(max_length=80)
    destination_type = models.CharField(max_length=40)
    from_dispatcher = models.CharField(max_length=40, default=None)
    to_endpoint = models.CharField(max_length=200)
    subject = models.CharField(max_length=80)
    body = models.CharField(max_length=200)
    short = models.CharField(max_length=80)
    created = models.DateTimeField()
    last_modified = models.DateTimeField()

    @staticmethod
    def from_json(json_data):
        message_type = MessageType()
        message_type.message_type_id = json_data["MessageTypeID"]
        message_type.message_type_uri = json_data["MessageTypeURI"]
        message_type.surrogate_id = json_data["SurrogateID"]
        message_type.content_type = json_data["ContentType"]
        message_type.destination_id = json_data["DestinationID"]
        message_type.destination_type = json_data["DestinationType"]
        message_type.from_dispatcher = json_data["From"]
        message_type.to_endpoint = json_data["To"]
        message_type.subject = json_data["Subject"]
        message_type.body = json_data["Body"]
        message_type.short = json_data["Short"]
        if "Created" in json_data:
            message_type.created = dateutil.parser.parse(json_data["Created"])
        if "LastModified" in json_data:
            message_type.last_modified = dateutil.parser.parse(
                 json_data["LastModified"])
        return message_type

    def json_data(self):
        return {
            "MessageType": {
                "MessageTypeID": self.message_type_id,
                "MessageTypeURI": self.message_type_uri,
                "SurrogateID": self.surrogate_id,
                "ContentType": self.content_type,
                "DestinationID": self.destination_id,
                "DestinationType": self.destination_type,
                "From": self.from_dispatcher,
                "To": self.to_endpoint,
                "Subject": self.subject,
                "Body": self.body,
                "Short": self.short,
                "Created": self.created.isoformat() if (
                    self.created is not None) else None,
                "LastModified": self.last_modified.isoformat() if (
                    self.last_modified is not None) else None
            }
        }
