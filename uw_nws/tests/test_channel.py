from unittest import TestCase
from uw_nws import NWS
from uw_nws.models import Channel
from uw_nws.utilities import fdao_nws_override
from uw_nws.exceptions import InvalidUUID
from restclients_core.exceptions import DataFailureException
from datetime import datetime


@fdao_nws_override
class NWSTestChannel(TestCase):
    def test_channel_by_channel_id(self):
        nws = NWS()
        channel = nws.get_channel_by_channel_id(
            "b779df7b-d6f6-4afb-8165-8dbe6232119f")
        self._assert_channel(channel)

    def test_channel_by_channel_id_exceptions(self):
        nws = NWS()
        self.assertRaises(InvalidUUID, nws.get_channel_by_channel_id, "abc")
        self.assertRaises(
            DataFailureException, nws.get_channel_by_channel_id,
            "00000000-d6f6-4afb-8165-8dbe6232119f")

    def test_channel_sln(self):
        nws = NWS()
        channels = nws.get_channels_by_sln(
            "uw_student_courseavailable", "12345")
        self.assertEquals(len(channels), 1)

        self.assertRaises(
            DataFailureException, nws.get_channels_by_sln,
            "uw_student_courseavailable", "00000")

    def test_channel_sln_and_term(self):
        nws = NWS()
        channels = nws.get_channels_by_sln_year_quarter(
            "uw_student_courseavailable", "12345", 2012, "autumn")
        self.assertEquals(len(channels), 1)

        self.assertRaises(
            DataFailureException, nws.get_channels_by_sln_year_quarter,
            "uw_student_courseavailable", "12345", 2013, "summer")

    def test_active_channels_by_year_quarter(self):
        nws = NWS()
        dt = datetime(2013, 5, 31, 0, 0, 0)
        channels = nws.get_active_channels_by_year_quarter(
            "uw_student_courseavailable", 2013, 'spring', expires=dt)
        self.assertEquals(len(channels), 1)

        self.assertRaises(
            DataFailureException,  nws.get_active_channels_by_year_quarter,
            "uw_student_courseavailable", 2013, 'summer', expires=dt)

    def _assert_channel(self, channel):
        self.assertEquals(
            channel.channel_id, "b779df7b-d6f6-4afb-8165-8dbe6232119f")
        self.assertEquals(channel.surrogate_id, "2012,autumn,cse,100,w")
        self.assertEquals(channel.type, "uw_student_courseavailable")
        self.assertEquals(channel.name, "FLUENCY IN INFORMATION TECHNOLOGY")
        self.assertEquals(channel.description, (
            "Introduces skills, concepts, and capabilities necessary to "
            "effectively use information technology. Includes logical "
            "reasoning, managing complexity, operation of computers and "
            "networks, and contemporary applications such as effective web "
            "searching and database manipulation, ethical aspects, and "
            "social impacts of information technology. Offered: jointly "
            "with INFO 100.\n"))
