from unittest import TestCase
from uw_nws import NWS
from uw_nws.utilities import fdao_nws_override


@fdao_nws_override
class NWSTestActAs(TestCase):
    def test_act_as(self):
        nws = NWS()
        self.assertFalse(hasattr(nws._write_headers(), "X_UW_ACT_AS"))

        nws.actas_user = "javerage@washington.edu"
        self.assertEquals(
            nws._write_headers()["X_UW_ACT_AS"], "javerage@washington.edu")

        nws = NWS(actas_user="bill@washington.edu")
        self.assertEquals(
            nws._write_headers()["X_UW_ACT_AS"], "bill@washington.edu")

        nws.actas_user = "javerage@washington.edu"
        self.assertEquals(
            nws._write_headers()["X_UW_ACT_AS"], "javerage@washington.edu")
