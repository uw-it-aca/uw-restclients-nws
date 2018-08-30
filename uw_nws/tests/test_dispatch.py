from unittest import TestCase
from uw_nws import NWS
from uw_nws.models import Dispatch
from uw_nws.utilities import fdao_nws_override
from restclients_core.exceptions import (
    DataFailureException)
from uw_nws.exceptions import InvalidUUID


@fdao_nws_override
class NWSTestDispatch(TestCase):
    def _setup_dispatch(self):
        dispatch = Dispatch()
        dispatch.dispatch_id = "8b77b7b8-604e-4854-9c8d-872214fe8ae7"
        dispatch.message_type = "uw_student_courseavailable"
        dispatch.content = {}
        return dispatch

    def test_default_dispatch(self):
        dispatch = Dispatch()
        self.assertEquals(dispatch.dispatch_id, None)

    def test_create_dispatch(self):
        dispatch = self._setup_dispatch()

        nws = NWS(actas_user="javerage")
        self.assertRaises(
            DataFailureException, nws.create_new_dispatch, dispatch)

        dispatch.dispatch_id = ""
        self.assertRaises(InvalidUUID, nws.create_new_dispatch, dispatch)

    def test_create_invalid_dispatch(self):
        dispatch = self._setup_dispatch()
        dispatch.dispatch_id = "123"

        nws = NWS()
        self.assertRaises(
            InvalidUUID, nws.create_new_dispatch, dispatch)

    def test_delete_dispatch(self):
        nws = NWS(actas_user="javerage")
        self.assertRaises(
            DataFailureException, nws.delete_dispatch,
            "8b77b7b8-604e-4854-9c8d-872214fe8ae7")

    def test_delete_invalid_dispatch(self):
        nws = NWS(actas_user="javerage")
        self.assertRaises(
            InvalidUUID, nws.delete_dispatch,
            "123")

    def test_json_data(self):
        dispatch = self._setup_dispatch()
        data = dispatch.json_data()

        self.assertEquals(
            data["Dispatch"]["DispatchID"],
            "8b77b7b8-604e-4854-9c8d-872214fe8ae7")
