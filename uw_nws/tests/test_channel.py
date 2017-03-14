from unittest import TestCase
from uw_nws import NWS
from uw_nws.models import Channel
from uw_nws.utilities import fdao_nws_override
from uw_sws.util import fdao_sws_override
from restclients_core.exceptions import DataFailureException


@fdao_nws_override
@fdao_sws_override
class NWSTestChannel(TestCase):
    def test_create_channel(self):
        channel = Channel()
        channel.surrogate_id = "2012,autumn,uwit,100,a"
        channel.type =  "uw_student_courseavailable"
        channel.name = "TEST CREATE CHANNEL"
        channel.description = "TEST CREATE CHANNEL \n"

        nws = NWS()
        response_status = nws.create_new_channel(channel)
        self.assertEquals(response_status, 201)

    def test_update_channel(self):
        channel = Channel()
        channel.surrogate_id = "2012,autumn,uwit,100,a"
        channel.type =  "uw_student_courseavailable"
        channel.name = "TEST CREATE CHANNEL"
        channel.description = "TEST CREATE CHANNEL \n"

        nws = NWS()
        response_status = nws.update_channel(channel)
        self.assertEquals(204, response_status)

    def test_channel_by_channel_id(self):
        nws = NWS()
        channel = nws.get_channel_by_channel_id("b779df7b-d6f6-4afb-8165-8dbe6232119f")
        self._assert_channel(channel)

    def test_channel_sln(self):
        nws = NWS()
        channels = nws.get_channels_by_sln("uw_student_courseavailable", "12345")
        self.assertEquals(len(channels), 1)

    def test_channel_sln_and_term(self):
        nws = NWS()
        channels = nws.get_channels_by_sln_year_quarter("uw_student_courseavailable", "12345", 2012, "autumn")
        self.assertEquals(len(channels), 1)

    def test_terms_with_active_channels(self):
        nws = NWS()

        terms = nws.get_terms_with_active_channels("uw_student_courseavailable")
        self.assertEquals(len(terms), 2)

        self.assertEquals(terms[0].year, 2013)
        self.assertEquals(terms[0].quarter, 'spring')
        self.assertEquals(terms[1].year, 2013)
        self.assertEquals(terms[1].quarter, 'summer')

    def test_channel_surrogate_id(self):
        nws = NWS()
        channel = nws.get_channel_by_surrogate_id("uw_student_courseavailable", "2012,autumn,cse,100,w")
        self._assert_channel(channel)

    def _assert_channel(self, channel):
        self.assertEquals(channel.channel_id, "b779df7b-d6f6-4afb-8165-8dbe6232119f")
        self.assertEquals(channel.surrogate_id, "2012,autumn,cse,100,w")
        self.assertEquals(channel.type, "uw_student_courseavailable")
        self.assertEquals(channel.name, "FLUENCY IN INFORMATION TECHNOLOGY")
        self.assertEquals(channel.description, "Introduces skills, concepts, and capabilities necessary to effectively use information technology. Includes logical reasoning, managing complexity, operation of computers and networks, and contemporary applications such as effective web searching and database manipulation, ethical aspects, and social impacts of information technology. Offered: jointly with INFO 100.\n")
