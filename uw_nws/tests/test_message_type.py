from unittest import TestCase
from uw_nws import NWS
from uw_nws.models import MessageType
from uw_nws.utilities import fdao_nws_override
from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)
from uw_nws.exceptions import InvalidUUID, InvalidSurrogateID


@fdao_nws_override
class NWSTestMessageType(TestCase):
    def _setup_message_type(self):
        message_type = MessageType()
        message_type.message_type_id = "d097a66a-23bb-4b2b-bb44-01fe1d11aab8"
        message_type.message_type_uri = ("/notification/v1/message-type/d097"
                                         "a66a-23bb-4b2b-bb44-01fe1d11aab0")
        message_type.surrogate_id = "uw_student_courseavailable"
        message_type.content_type = "application/json"
        message_type.desination_type = "channel"
        return message_type

    def test_default_message_type(self):
        message_type = MessageType()
        self.assertEquals(message_type.message_type_id, None)

    def test_message_type_by_id(self):
        nws = NWS()
        message_type = nws.get_message_type_by_id(
            "d097a66a-23bb-4b2b-bb44-01fe1d11aab0")
        self.assertEquals(
                         message_type.message_type_id,
                         "d097a66a-23bb-4b2b-bb44-01fe1d11aab0")

        self.assertRaises(
            DataFailureException,
            nws.get_message_type_by_id, "00000000-23bb-4b2b-bb44-01fe1d11aab0")

    def test_delete_message_type(self):
        nws = NWS(actas_user="javerage")
        self.assertRaises(
            DataFailureException, nws.delete_message_type,
            "d097a66a-23bb-4b2b-bb44-01fe1d11aab8")

    def test_delete_invalid_message_type(self):
        nws = NWS()
        self.assertRaises(
            InvalidUUID, nws.delete_message_type,
            "123")

    def test_update_message_type(self):
        nws = NWS(actas_user="javerage")
        message_type = nws.get_message_type_by_id(
            "d097a66a-23bb-4b2b-bb44-01fe1d11aab8")

        self.assertRaises(
            DataFailureException, nws.update_message_type, message_type)

        message_type.message_type_id = ""
        self.assertRaises(
            InvalidUUID, nws.update_message_type, message_type)

    def test_surrogate_id_validation(self):
        nws = NWS()
        nws._validate_message_type_surrogate("uw_student_courseavailable")
        nws._validate_message_type_surrogate("uw_direct_notification")

        self.assertRaises(
            InvalidSurrogateID, nws._validate_message_type_surrogate,
            'uc_fake_surrogate')
        self.assertRaises(
            InvalidSurrogateID, nws._validate_message_type_surrogate, 'uw')
        self.assertRaises(
            InvalidSurrogateID, nws._validate_message_type_surrogate,
            'd097a66a-23bb-4b2b-bb44-01fe1d11aab8')
        self.assertRaises(
            InvalidSurrogateID, nws._validate_message_type_surrogate, 'uw_')

    def test_json_data(self):
        message_type = self._setup_message_type()
        data = message_type.json_data()

        self.assertEquals(
            data["MessageType"]["MessageTypeID"],
            "d097a66a-23bb-4b2b-bb44-01fe1d11aab8")
        self.assertEquals(
            data["MessageType"]["MessageTypeURI"],
            "/notification/v1/message-type/" +
            "d097a66a-23bb-4b2b-bb44-01fe1d11aab0")
        self.assertEquals(
            data["MessageType"]["SurrogateID"],
            "uw_student_courseavailable")
