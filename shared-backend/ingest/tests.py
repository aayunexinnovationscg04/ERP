from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from fleet.models import Device, Telemetry
from ingest.models import Command


@override_settings(INGEST_TOKEN="t0k")
class ForwardedIngestTests(TestCase):
    """Packets forwarded by the receiver dashboard (X-Receiver-Seq) are stored once."""

    def post(self, seq, body='{"device_id":"dev-1","speed":30}'):
        return APIClient().post("/api/telemetry", body, content_type="application/json",
                                HTTP_X_AUTH="t0k", HTTP_X_DEVICE_ID="dev-1",
                                HTTP_X_FORWARDED_FOR="10.1.2.3", HTTP_X_RECEIVER_SEQ=str(seq))

    def test_forwarded_packet_is_stored_with_seq_and_device_ip(self):
        r = self.post(7)
        self.assertEqual(r.status_code, 200)
        t = Telemetry.objects.get()
        self.assertEqual(t.raw["_seq"], 7)
        self.assertEqual(t.raw["_client_ip"], "10.1.2.3")
        self.assertEqual(t.speed_kmph, 30)

    def test_duplicate_seq_is_not_stored_twice_but_commands_still_flow(self):
        self.post(7)
        Command.objects.create(device=Device.objects.get(device_id="dev-1"), payload="open")
        r = self.post(7)
        self.assertTrue(r.data.get("duplicate"))
        self.assertEqual([c["payload"] for c in r.data["commands"]], ["open"])
        self.assertEqual(Telemetry.objects.count(), 1)

    def test_wrong_token_rejected(self):
        r = APIClient().post("/api/telemetry", "{}", content_type="application/json", HTTP_X_AUTH="nope")
        self.assertEqual(r.status_code, 401)
