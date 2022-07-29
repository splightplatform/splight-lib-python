import json
from django.test import TestCase
from splight_database.django.djatabase.models.blockchain import BlockchainContract, BlockchainContractSubscription


class TestBlockchainContract(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create(self):
        contract = BlockchainContract.objects.create(
            name="NFT",
            description="NFT Description",
            address="0x1234567894567894567812345678945678945678",
            abi_json=json.dumps({})
        )
        self.assertIsInstance(contract, BlockchainContract)
 
    def test_create_subscription(self):
        contract = BlockchainContractSubscription.objects.create(
            asset_id = "0x1234567894567894567812345678945678945678",
            attribute_id = "0x1234567894567894567812345678945678945678",
            contract_id = "0x1234567894567894567812345678945678945678",
        )
        self.assertIsInstance(contract, BlockchainContractSubscription)
 