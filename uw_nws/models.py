from restclients_core import models


class Person(models.Model):
    person_id = models.CharField(max_length=40)
    person_uri = models.CharField(max_length=200)
    surrogate_id = models.CharField(max_length=80)
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)
    attributes = {}
    endpoints = []

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
                "Endpoints": [e.json_data() for e in self.endpoints]
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
    tags = {}

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
    user = models.CharField(max_length=20)
    owner = models.CharField(max_length=20)
    status = models.CharField(max_length=40)
    active = models.NullBooleanField()
    default = models.NullBooleanField()
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)

    def json_data(self):
        return {
            "Endpoint": {
                "EndpointID": self.endpoint_id,
                "EndpointURI": self.endpoint_uri,
                "EndpointAddress": self.endpoint_address,
                "Carrier": self.carrier,
                "Protocol": self.protocol,
                "SubscriberID": self.user,
                "OwnerID": self.owner,
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
    subscription_id = models.CharField(max_length=40)
    subscription_uri = models.CharField(max_length=200)
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)
    channel = None
    endpoint = None

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
                "Channel": self.channel.json_data() if (
                    self.channel is not None) else None,
                "Endpoint": self.endpoint.json_data() if (
                    self.endpoint is not None) else None
            }
        }
