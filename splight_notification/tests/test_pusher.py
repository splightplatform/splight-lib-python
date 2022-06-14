from unittest import TestCase
from unittest.mock import patch
from pusher import Pusher
from splight_notification.pusher import PusherClient
from splight_models import Notification


class TestPusherClient(TestCase):
    topic = 'sample_topic'
    data = {'message': 'Sample message', 'title': "Sample title"}

    @patch.object(Pusher, '__init__', return_value=None)
    def test_init_with_args(self, _):
        client = PusherClient()
        self.assertIsInstance(client._client, Pusher)

    @patch.object(Pusher, '__init__', return_value=None)
    @patch('splight_notification.pusher.Pusher.trigger')
    def test_client_send(self, mocked_call, _):
        client = PusherClient()
        data = Notification(**self.data)
        client.send(data, self.topic)
        mocked_call.assert_called_with(client.channel, self.topic, data.json())
