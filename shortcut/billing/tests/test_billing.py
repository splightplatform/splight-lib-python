from django.test import TestCase
from mock import patch
from datetime import datetime
from parameterized import parameterized
from splight_models import *
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient
from splight_lib.hub import HubClient
from ..billing import BillingGenerator
from decimal import Decimal, ROUND_HALF_UP
import splight_models as models

class TestBilling(TestCase):
    def setUp(self):
        self.namespace = "default"
        self.database_client = DatabaseClient(self.namespace)
        return super().setUp()

    @parameterized.expand([
        (
            (
                [
                    [HubComponent(
                        name="FakeComponentAlgorithm",
                        version="0_1",
                        impact=5
                    )],
                    [],
                    [],
                ]
            ),(
                [
                    BillingSettings(
                        pricing = Pricing(
                            COMPUTING_PRICE_PER_HOUR=0.04,
                            STORAGE_PRICE_PER_GB=2,
                            IMPACT_MULTIPLIER={
                                "1": 10.0,
                                "2": 25.0,
                                "3": 63.0,
                                "4": 156.0,
                                "5": 391.0
                            }
                        ),
                        discounts=[
                            Discount(
                                organization_id="default",
                                type=DiscountType.FIXED,
                                value=10
                            )
                        ],
                        computing_time_measurement_per_hour=True
                    )
                ]  
            ),(
                [
                    {
                        "_id": "deployment_id",
                        "events": [
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "create",
                                "timestamp": datetime(2022, 1, 1),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            },
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "destroy",
                                "timestamp": datetime(2022, 1, 2),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            }
                        ]
                    },
                    {
                        "_id": "deployment_id2",
                        "events": [
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "create",
                                "timestamp": datetime(2022, 1, 1),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id2",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            },
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "destroy",
                                "timestamp": datetime(2022, 1, 2),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id2",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            }
                        ]
                    },
                ]
            ),(
                    {"f6c55a58-aa6d-4518-9961-70d30d0cd74c": 2}
            ),
        ),
    ])
    def test_generate_simple(self, hub_component, billing_settings, billing_events, storage_usage_gb):
        with patch.object(HubClient, "get", side_effect=hub_component):
            with patch.object(DatabaseClient, "get", return_value=billing_settings):
                with patch.object(DatalakeClient, "raw_aggregate", return_value=billing_events):
                    with patch.object(DatalakeClient, "get_components_sizes_gb", return_value=storage_usage_gb):
                        begin_of_january, end_of_january = datetime(2022, 1, 1), datetime(2022, 1, 31)
                        billing_generator = BillingGenerator(self.namespace, date=end_of_january)
                        billing_month, billings = billing_generator.generate()
                        self.assertEqual(billing_month.month, datetime(2022, 1, 1, tzinfo=pytz.UTC))
                        
                        #the correct billing settings among all
                        expected_bs_index = 0
                        self.assertEqual(billing_generator.billing_settings, billing_settings[expected_bs_index])
                        billing_settings = billing_settings[expected_bs_index]

                        fake_algorithm_running_hs = (min(end_of_january, billing_events[0]["events"][1]["timestamp"])-max(begin_of_january, billing_events[0]["events"][0]["timestamp"])).total_seconds()/3600
                        fake_algorithm_running_hs = fake_algorithm_running_hs + (min(end_of_january, billing_events[1]["events"][1]["timestamp"])-max(begin_of_january, billing_events[1]["events"][0]["timestamp"])).total_seconds()/3600

                        storage_price = billing_settings.pricing.STORAGE_PRICE_PER_GB * storage_usage_gb["f6c55a58-aa6d-4518-9961-70d30d0cd74c"]
                        computing_price = billing_settings.pricing.COMPUTING_PRICE_PER_HOUR * fake_algorithm_running_hs
                        impact_multiplier = billing_settings.pricing.IMPACT_MULTIPLIER[str(hub_component[0][0].impact)]
                        expected_total_price_without_discount = (computing_price + storage_price) * impact_multiplier

                        discount_value = 0
                        for discount in billing_settings.discounts:
                            if discount.organization_id == self.namespace:
                                if discount.type == DiscountType.FIXED:
                                    discount_value += discount.value
                                elif discount.type == DiscountType.PERCENTAGE:
                                    discount_value += discount.value * expected_total_price_without_discount / 100

                        expected_total_price = max(0, expected_total_price_without_discount - discount_value)
                        expected_total_price = float(Decimal(expected_total_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


                        self.assertEqual(billing_month.total_price_without_discount, expected_total_price_without_discount)
                        self.assertEqual(billing_month.total_price, expected_total_price)
                        self.assertEqual(len(billings), 1)

                        sum = 0
                        sum_detailed = 0
                        for billing, _ in billings:
                            sum += billing.total_price
                            for detail in billing.detailed_pricing.values():
                                sum_detailed += detail
                        sum = max(0, sum - discount_value)
                        sum_detailed = max(0, sum_detailed - discount_value)
                        sum = float(Decimal(sum).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        sum_detailed = float(Decimal(sum_detailed).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        self.assertEqual(sum, expected_total_price)
                        self.assertEqual(sum_detailed, expected_total_price)
                        
                        # Deployment billing checks
                        billing_computing_price = computing_price * impact_multiplier
                        billing_storage_price = storage_price * impact_multiplier
                        deployment_billing, billing_items = billings[0]
                        self.assertEqual(deployment_billing.description, "Component deployments")
                        self.assertEqual(deployment_billing.detailed_pricing["computing_price"], billing_computing_price)
                        self.assertEqual(deployment_billing.detailed_pricing["storage_price"], billing_storage_price)

                        for billing_item in billing_items:
                            self.assertEqual(billing_item.computing_price, billing_computing_price)
                            self.assertEqual(billing_item.storage_price, billing_storage_price)


    @parameterized.expand([
        (
            (
                [
                    [HubComponent(
                        name="FakeComponentAlgorithm",
                        version="0_1",
                        impact=5
                    )],
                    [HubComponent(
                        name="FakeComponentConnector",
                        version="0_1",
                        # no impact, should be treated as default
                    )],
                    [],
                ]
            ),(
                [
                    BillingSettings(
                        timestamp=datetime(2021, 12, 31),
                        pricing = Pricing(
                            COMPUTING_PRICE_PER_HOUR=0.04,
                            STORAGE_PRICE_PER_GB=2,
                            IMPACT_MULTIPLIER={
                                "1": 10.0,
                                "2": 25.0,
                                "3": 63.0,
                                "4": 156.0,
                                "5": 391.0
                            }
                        ),
                        discounts=[
                            Discount(
                                organization_id="default",
                                type=DiscountType.PERCENTAGE,
                                value=25
                            )
                        ],
                        computing_time_measurement_per_hour=True
                    ),
                    BillingSettings(
                        timestamp=datetime(2022, 1, 2),
                        pricing = Pricing(
                            COMPUTING_PRICE_PER_HOUR=2,
                            STORAGE_PRICE_PER_GB=4,
                            IMPACT_MULTIPLIER={
                                "1": 100.0,
                                "2": 250.0,
                                "3": 630.0,
                                "4": 1560.0,
                                "5": 3910.0
                            }
                        ),
                        discounts=[
                            Discount(
                                organization_id="default",
                                type=DiscountType.PERCENTAGE,
                                value=45
                            )
                        ],
                        computing_time_measurement_per_hour=True
                    ),
                    BillingSettings(
                        timestamp=datetime(2022, 1, 5),
                        pricing = Pricing(
                            COMPUTING_PRICE_PER_HOUR=40,
                            STORAGE_PRICE_PER_GB=200,
                            IMPACT_MULTIPLIER={
                                "1": 6874.0,
                                "2": 14898.0,
                                "3": 32114.0,
                                "4": 456156.0,
                                "5": 7896391.0
                            }
                        ),
                        discounts=[
                            Discount(
                                organization_id="default",
                                type=DiscountType.PERCENTAGE,
                                value=85
                            )
                        ],
                        computing_time_measurement_per_hour=True
                    ),
                ]  
            ),(
                [
                    {
                        "_id": "deployment_id",
                        "events": [
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "create",
                                "timestamp": datetime(2022, 1, 15),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            },
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "destroy",
                                "timestamp": datetime(2022, 1, 20),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            }
                        ]
                    },
                    {
                        "_id": "deployment_id2",
                        "events": [
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "create",
                                "timestamp": datetime(2021, 12, 1),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id2",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            },
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "destroy",
                                "timestamp": datetime(2022, 1, 15),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id2",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            }
                        ]
                    },
                    {
                        "_id": "deployment_id3",
                        "events": [
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "create",
                                "timestamp": datetime(2022, 1, 5),
                                "data": {
                                    "version": "FakeComponentConnector-0_1",
                                    "type": "Connector",
                                    "id": "deployment_id3",
                                    "external_id": "9ba830b5-b1b3-440c-94e7-bca80e5c09cc"
                                }
                            },
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "destroy",
                                "timestamp": datetime(2022, 1, 6),
                                "data": {
                                    "version": "FakeComponentConnector-0_1",
                                    "type": "Connector",
                                    "id": "deployment_id3",
                                    "external_id": "9ba830b5-b1b3-440c-94e7-bca80e5c09cc"
                                }
                            }
                        ]
                    }
                ]
            ),(
                    {"f6c55a58-aa6d-4518-9961-70d30d0cd74c": 1, "9ba830b5-b1b3-440c-94e7-bca80e5c09cc": 2}
            ),
        )  
    ])
    def test_generate_multiple(self, hub_component, billing_settings, billing_events, storage_usage_gb):
        with patch.object(HubClient, "get", side_effect=hub_component):
                with patch.object(DatalakeClient, "raw_aggregate", return_value=billing_events):
                    with patch.object(DatalakeClient, "get_components_sizes_gb", return_value=storage_usage_gb):
                        for bs in billing_settings:
                            self.database_client.save(bs)
                        begin_of_january, end_of_january = datetime(2022, 1, 1), datetime(2022, 1, 31)
                        billing_generator = BillingGenerator(self.namespace, date=end_of_january)
                        billing_month, billings = billing_generator.generate()
                        self.assertEqual(billing_month.month, datetime(2022, 1, 1, tzinfo=pytz.UTC))

                        #check if get_billing_settings is working ok
                        expected_bs_index = 2
                        self.assertEqual(billing_generator.billing_settings, billing_settings[expected_bs_index])
                        billing_settings = billing_settings[expected_bs_index]
                        
                        fake_algorithm_running_hs = (min(end_of_january, billing_events[0]["events"][1]["timestamp"])-max(begin_of_january, billing_events[0]["events"][0]["timestamp"])).total_seconds()/3600
                        fake_algorithm_running_hs = fake_algorithm_running_hs + (min(end_of_january, billing_events[1]["events"][1]["timestamp"])-max(begin_of_january, billing_events[1]["events"][0]["timestamp"])).total_seconds()/3600
                        fake_connector_running_hs = (min(end_of_january, billing_events[2]["events"][1]["timestamp"])-max(begin_of_january, billing_events[2]["events"][0]["timestamp"])).total_seconds()/3600

                        fake_algorithm_storage_price = billing_settings.pricing.STORAGE_PRICE_PER_GB * storage_usage_gb["f6c55a58-aa6d-4518-9961-70d30d0cd74c"] 
                        fake_algorithm_computing_price = billing_settings.pricing.COMPUTING_PRICE_PER_HOUR * fake_algorithm_running_hs
                        fake_algorithm_impact_multiplier = billing_settings.pricing.IMPACT_MULTIPLIER[str(hub_component[0][0].impact)]
                        fake_algorithm_total_price = (fake_algorithm_storage_price + fake_algorithm_computing_price) * fake_algorithm_impact_multiplier

                        # fake connector does not have impact, should be the default
                        fake_connector_storage_price = billing_settings.pricing.STORAGE_PRICE_PER_GB * storage_usage_gb["9ba830b5-b1b3-440c-94e7-bca80e5c09cc"] 
                        fake_connector_computing_price = billing_settings.pricing.COMPUTING_PRICE_PER_HOUR * fake_connector_running_hs
                        fake_connector_impact_multiplier = billing_settings.pricing.IMPACT_MULTIPLIER[str(billing_generator.DEFAULT_COMPONENT_IMPACT)]
                        fake_connector_total_price = (fake_connector_storage_price + fake_connector_computing_price) * fake_connector_impact_multiplier

                        expected_total_price_without_discount = float(Decimal(fake_algorithm_total_price + fake_connector_total_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        discount_value = 0
                        for discount in billing_settings.discounts:
                            if discount.organization_id == self.namespace:
                                if discount.type == DiscountType.FIXED:
                                    discount_value += discount.value
                                elif discount.type == DiscountType.PERCENTAGE:
                                    discount_value += discount.value * expected_total_price_without_discount / 100

                        expected_total_price = max(0, expected_total_price_without_discount - discount_value)
                        expected_total_price = float(Decimal(expected_total_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

                        self.assertEqual(billing_month.total_price_without_discount, expected_total_price_without_discount)
                        self.assertEqual(billing_month.total_price, expected_total_price)
                        self.assertEqual(len(billings), 1)

                        sum = 0
                        sum_detailed = 0
                        for billing, _ in billings:
                            sum += billing.total_price
                            for detail in billing.detailed_pricing.values():
                                sum_detailed += detail
                        sum = max(0, sum - discount_value)
                        sum_detailed = max(0, sum_detailed - discount_value)
                        sum = float(Decimal(sum).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        sum_detailed = float(Decimal(sum_detailed).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        self.assertEqual(sum, expected_total_price)
                        self.assertEqual(sum_detailed, expected_total_price)
                        
                        # Deployment billing checks
                        deployment_billing, billing_items = billings[0]
                        self.assertEqual(deployment_billing.description, "Component deployments")
                        self.assertEqual(deployment_billing.total_price, expected_total_price_without_discount)
                        self.assertEqual(len(billing_items), 2)

    @parameterized.expand([
        (
            (
                [
                    [HubComponent(
                        name="FakeComponentAlgorithm",
                        version="0_1",
                        impact=5
                    )],
                    [],
                    [],
                ]
            ),(
                [
                    BillingSettings(
                        timestamp=datetime(2021, 12, 31),
                        pricing = Pricing(
                            COMPUTING_PRICE_PER_HOUR=0.04,
                            STORAGE_PRICE_PER_GB=2,
                            IMPACT_MULTIPLIER={
                                "1": 10.0,
                                "2": 25.0,
                                "3": 63.0,
                                "4": 156.0,
                                "5": 391.0
                            }
                        ),
                        discounts=[
                            Discount(
                                organization_id="default",
                                type=DiscountType.PERCENTAGE,
                                value=25
                            )
                        ],
                        computing_time_measurement_per_hour=True
                    ),
                    BillingSettings(
                        timestamp=datetime(2022, 1, 2),
                        pricing = Pricing(
                            COMPUTING_PRICE_PER_HOUR=1,
                            STORAGE_PRICE_PER_GB=1,
                            IMPACT_MULTIPLIER={
                                "1": 1.0,
                                "2": 1.0,
                                "3": 1.0,
                                "4": 1.0,
                                "5": 1.0
                            }
                        ),
                        discounts=[
                            Discount(
                                organization_id="default",
                                type=DiscountType.PERCENTAGE,
                                value=45
                            )
                        ],
                        computing_time_measurement_per_hour=True
                    ),
                ]  
            ),(
                [
                    {
                        "_id": "deployment_id",
                        "events": [
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "create",
                                "timestamp": datetime(2021, 12, 1),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            }
                        ]
                    }
                ]
            ),(
                    {"f6c55a58-aa6d-4518-9961-70d30d0cd74c": 1}
            ),
        )  
    ])
    def test_generate_component_runned_all_month(self, hub_component, billing_settings, billing_events, storage_usage_gb):
        with patch.object(HubClient, "get", side_effect=hub_component):
                with patch.object(DatalakeClient, "raw_aggregate", return_value=billing_events):
                    with patch.object(DatalakeClient, "get_components_sizes_gb", return_value=storage_usage_gb):
                        for bs in billing_settings:
                            self.database_client.save(bs)
                        begin_of_january, end_of_january = datetime(2022, 1, 1), datetime(2022, 1, 31)
                        billing_generator = BillingGenerator(self.namespace, date=end_of_january)
                        billing_month, billings = billing_generator.generate()
                        self.assertEqual(billing_month.month, datetime(2022, 1, 1, tzinfo=pytz.UTC))

                        #check if get_billing_settings is working ok
                        expected_bs_index = 1
                        self.assertEqual(billing_generator.billing_settings, billing_settings[expected_bs_index])
                        billing_settings = billing_settings[expected_bs_index]
                        
                        fake_algorithm_running_hs = (end_of_january-max(begin_of_january, billing_events[0]["events"][0]["timestamp"])).total_seconds()/3600

                        fake_algorithm_storage_price = billing_settings.pricing.STORAGE_PRICE_PER_GB * storage_usage_gb["f6c55a58-aa6d-4518-9961-70d30d0cd74c"] 
                        fake_algorithm_computing_price = billing_settings.pricing.COMPUTING_PRICE_PER_HOUR * fake_algorithm_running_hs
                        fake_algorithm_impact_multiplier = billing_settings.pricing.IMPACT_MULTIPLIER[str(hub_component[0][0].impact)]
                        fake_algorithm_total_price = (fake_algorithm_storage_price + fake_algorithm_computing_price) * fake_algorithm_impact_multiplier

                        expected_total_price_without_discount = float(Decimal(fake_algorithm_total_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        discount_value = 0
                        for discount in billing_settings.discounts:
                            if discount.organization_id == self.namespace:
                                if discount.type == DiscountType.FIXED:
                                    discount_value += discount.value
                                elif discount.type == DiscountType.PERCENTAGE:
                                    discount_value += discount.value * expected_total_price_without_discount / 100

                        expected_total_price = max(0, expected_total_price_without_discount - discount_value)
                        expected_total_price = float(Decimal(expected_total_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

                        self.assertEqual(billing_month.total_price_without_discount, expected_total_price_without_discount)
                        self.assertEqual(billing_month.total_price, expected_total_price)
                        self.assertEqual(len(billings), 1)

                        sum = 0
                        sum_detailed = 0
                        for billing, _ in billings:
                            sum += billing.total_price
                            for detail in billing.detailed_pricing.values():
                                sum_detailed += detail
                        sum = max(0, sum - discount_value)
                        sum_detailed = max(0, sum_detailed - discount_value)
                        sum = float(Decimal(sum).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        sum_detailed = float(Decimal(sum_detailed).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                        self.assertEqual(sum, expected_total_price)
                        self.assertEqual(sum_detailed, expected_total_price)
                        
                        # Deployment billing checks
                        deployment_billing, billing_items = billings[0]
                        self.assertEqual(deployment_billing.description, "Component deployments")
                        self.assertEqual(deployment_billing.total_price, expected_total_price_without_discount)
                        self.assertEqual(len(billing_items), 1)


    @parameterized.expand([
        (
            (
                [
                    [HubComponent(
                        name="FakeComponentAlgorithm",
                        version="0_1",
                        impact=1
                        )],
                    [],
                    [],
                    [HubComponent(
                        name="FakeComponentAlgorithm",
                        version="0_1",
                        impact=1
                        )],
                    [],
                    []
                ]
            ),(
                [
                    BillingSettings(
                        pricing = Pricing(
                            COMPUTING_PRICE_PER_HOUR=0.04,
                            STORAGE_PRICE_PER_GB=2,
                            IMPACT_MULTIPLIER={
                                "1": 10.0,
                                "2": 25.0,
                                "3": 63.0,
                                "4": 156.0,
                                "5": 391.0
                            }
                        ),
                        discounts=[],
                        computing_time_measurement_per_hour=True
                    )
                ]  
            ),(
                [
                    {
                        "_id": "deployment_id",
                        "events": [
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "create",
                                "timestamp": datetime(2022, 1, 1),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            },
                            {
                                "type": BillingEventType.COMPONENT_DEPLOYMENT,
                                "event": "destroy",
                                "timestamp": datetime(2022, 1, 2),
                                "data": {
                                    "version": "FakeComponentAlgorithm-0_1",
                                    "type": "Algorithm",
                                    "id": "deployment_id",
                                    "external_id": "f6c55a58-aa6d-4518-9961-70d30d0cd74c"
                                }
                            }
                        ]
                    },
                ]
            ),(
                    {"f6c55a58-aa6d-4518-9961-70d30d0cd74c": 1}
            ),
        ),
    ])
    def test_close_month(self, hub_component, billing_settings, billing_events, storage_usage_gb):
        with patch.object(HubClient, "get", side_effect=hub_component):
            with patch.object(DatabaseClient, "get", side_effect=[billing_settings, []]):
                with patch.object(DatalakeClient, "raw_aggregate", return_value=billing_events):
                    with patch.object(DatalakeClient, "get_components_sizes_gb", return_value=storage_usage_gb):
                        billing_generator = BillingGenerator(self.namespace, date=datetime(2022, 1, 1))
                        billing_month, billings = billing_generator.generate()
                        billing_generator.close_month()
        saved_billing_month = self.database_client.get(resource_type=MonthBilling, first=True)
        billing_month.id = saved_billing_month.id
        self.assertEqual(billing_month, saved_billing_month)
        for billing, billing_items in billings:
            saved_billing = self.database_client.get(resource_type=Billing, first=True)
            billing.id = saved_billing.id
            billing.month_billing_id = saved_billing_month.id
            self.assertEqual(billing, saved_billing)
            for billing_item in billing_items:
                saved_billing_item = self.database_client.get(resource_type=getattr(models,billing.items_type), first=True)
                billing_item.id = saved_billing_item.id
                billing_item.billing_id = saved_billing.id
                self.assertEqual(billing_item, saved_billing_item)