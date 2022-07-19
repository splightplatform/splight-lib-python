import json
from django.test import TestCase
from splight_database.django.djatabase.models.blockchain import BlockchainContract


class TestBlockchainContract(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create(self):
        contract = BlockchainContract.objects.create(
            name="NFT",
            description="NFT Description",
            account_id="0x1234567894567894567812345678945678945678",
            abi_json=json.dumps({})
        )
        self.assertIsInstance(contract, BlockchainContract)
 