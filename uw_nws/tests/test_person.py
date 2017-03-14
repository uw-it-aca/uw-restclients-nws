from unittest import TestCase
from uw_nws import NWS
from uw_nws.models import Person
from uw_nws.utilities import fdao_nws_override
from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)


@fdao_nws_override
class NWSTestPerson(TestCase):
    def _assert_person_matches(self, person):
        self.assertEquals('javerage@washington.edu', person.surrogate_id)
        self.assertEquals('9136CCB8F66711D5BE060004AC494FFE', person.person_id)
        self.assertTrue(len(person.endpoints))
        self.assertTrue(person.default_endpoint() is not None)

    def test_person_by_surrogate_id(self):
        nws = NWS()
        person = nws.get_person_by_surrogate_id("javerage@washington.edu")
        self._assert_person_matches(person)

        self.assertRaises(DataFailureException,
                          nws.get_person_by_surrogate_id,
                          "bill@washington.edu")
        self.assertRaises(InvalidNetID, nws.get_person_by_surrogate_id, None)
        self.assertRaises(InvalidNetID, nws.get_person_by_surrogate_id, "")
        self.assertRaises(InvalidNetID, nws.get_person_by_surrogate_id, 42)

    def test_person_by_uwregid(self):
        nws = NWS()
        person = nws.get_person_by_uwregid("9136CCB8F66711D5BE060004AC494FFE")
        self._assert_person_matches(person)

        self.assertRaises(DataFailureException,
                          nws.get_person_by_uwregid,
                          "ABC6CCB8F66711D5BE060004AC494FFE")
        self.assertRaises(InvalidRegID, nws.get_person_by_uwregid, None)
        self.assertRaises(InvalidRegID, nws.get_person_by_uwregid,  "")
        self.assertRaises(InvalidRegID, nws.get_person_by_uwregid, 42)

    def test_create_person(self):
        nws = NWS()
        person = nws.get_person_by_surrogate_id("javerage@washington.edu")
        person.person_id = None
        person.endpoints = None

        self.assertRaises(DataFailureException, nws.create_new_person, person)
        # response_status = nws.create_new_person(person)
        # self.assertEquals(201, response_status)
