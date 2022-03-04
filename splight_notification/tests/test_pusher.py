from unittest import TestCase
from unittest.mock import patch
from pusher import Pusher
from splight_notification.pusher import PusherClient
from splight_lib.database import Channel

class TestPusherClient(TestCase):
    channel = 'sample_channel'
    topic = 'sample_topic'
    socket = 'thisisjustasampleforasocket'
    data = {'key': 'value'}

    @patch.object(Pusher, '__init__', return_value=None)
    def test_init_with_args(self, _):
        client = PusherClient()
        self.assertIsInstance(client._client, Pusher)

    @patch.object(Pusher, '__init__', return_value=None)
    @patch('splight_notification.pusher.Pusher.authenticate')
    def test_client_authenticate(self, mocked_call, _):
        client = PusherClient()
        client.authenticate(self.socket, self.channel)
        mocked_call.assert_called_with(client.get_channel_name(self.channel, Channel.PRIVATE), self.socket)

    @patch.object(Pusher, '__init__', return_value=None)
    @patch('splight_notification.pusher.Pusher.trigger')
    def test_client_send(self, mocked_call, _):
        client = PusherClient()
        client.send(self.topic, self.data, self.channel)
        mocked_call.assert_called_with(client.get_channel_name(self.channel, Channel.PRIVATE), self.topic, self.data)

