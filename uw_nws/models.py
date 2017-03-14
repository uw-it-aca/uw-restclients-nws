from restclients_core import models


class Person(models.Model):
    person_id = models.CharField(max_length=40)
    person_uri = models.CharField(max_length=200)
    surrogate_id = models.CharField(max_length=80)
    #attributes = ViewModelField('Attributes', 6, view_model_type=DictionaryViewModel, produceable=False)
    #default_endpoint = ViewModelField('DefaultEndpoint', 8, view_model_type=Endpoint, produceable=False)
    #endpoints = ViewModelField('Endpoints', 9, view_model_type=EndpointList, produceable=False)
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)


class Channel(models.Model):
    channel_id = models.CharField(max_length=40)
    channel_uri = models.CharField(max_length=200)
    surrogate_id = models.CharField(max_length=80)
    type = models.CharField(max_length=40)
    name = models.CharField(max_length=80)
    #tags = ViewModelField('Tags', 6, view_model_type=DictionaryViewModel, produceable=False)
    description = models.CharField(max_length=200)
    expires = models.DateTimeField()
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)


class Endpoint(models.Model):
    endpoint_id = models.CharField(max_length=40)
    endpoint_uri = models.CharField(max_length=200)
    endpoint_address = models.CharField(max_length=200)
    carrier = models.CharField(max_length=40)
    protocol = models.SlugField(max_length=40)
    user = models.CharField(max_length=20)
    owner = models.CharField(max_length=20)
    status = models.CharField(max_length=40)
    active = models.NullBooleanField()
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
                "Created": self.created.isoformat(),
                "LastModified": self.last_modified.isoformat(),
                "ModifiedBy": self.modified_by
            }
        }


class Subscription(models.Model):
    subscription_id = models.CharField(max_length=40)
    subscription_uri = models.CharField(max_length=200)
    subscription_type = models.CharField(max_length=40)
    #channel = ViewModelField('Channel', 4, view_model_type=Channel)
    #endpoint = ViewModelField('Endpoint', 5, view_model_type=Endpoint)
    created = models.DateTimeField()
    last_modified = models.DateTimeField()
    modified_by = models.CharField(max_length=40)


class CourseAvailableEvent(models.Model):
    event_id = models.CharField(max_length=40)
    event_create_date = models.CharField(max_length=40)
    message_timestamp = models.CharField(max_length=40)
    space_available = models.PositiveIntegerField()
    quarter = models.CharField(max_length=6)
    year = models.PositiveSmallIntegerField()
    curriculum_abbr = models.CharField(max_length=6)
    course_number = models.CharField(max_length=3)
    section_id = models.CharField(max_length=2)
    sln = models.PositiveSmallIntegerField()
    notification_msg_0 = models.CharField(max_length=40)

    # THIS IS BROKEN
    def get_logging_description(self):
        return "%s,%s,%s,%s/%s - %s" % (
            self.year, self.quarter, self.curriculum_abbr, self.course_number,
            self.section_id)

    def get_surrogate_id(self):
        return "%s,%s,%s,%s,%s" % (
            self.year, self.quarter, self.curriculum_abbr.lower(),
            self.course_number, self.section_id.lower())

    def json_data(self):
        return{
            "Event": {
                "EventID": self.event_id,
                "EventCreateDate": self.event_create_date,
                "Section": {
                    "Course": {
                        "CourseNumber": self.course_number,
                        "CurriculumAbbreviation": self.curriculum_abbr.upper(),
                        "Quarter": self.quarter,
                        "Year": self.year
                    },
                    "SLN": self.sln,
                    "SectionID": self.section_id.upper()
                },
                "SpaceAvailable": self.space_available,
                "NotificationMsg0": self.notification_msg_0
            }
}
