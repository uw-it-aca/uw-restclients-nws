from restclients_core import models


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

    def default_endpoint(self):
        for endpoint in self.endpoints:
            if endpoint.default:
                return endpoint

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
