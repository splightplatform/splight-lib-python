import os
import subprocess
import pytz
import time
import jinja2
import splight_models as models
from datetime import datetime, timezone
from collections import defaultdict
from datetime import timedelta
from typing import Dict
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Tuple
from splight_models import (
    BillingEvent,
    BillingEventType,
    BillingSettings,
    DeploymentBillingItem,
    Billing,
    MonthBilling,
    DiscountType,
    BillingItem,
    HubAlgorithm,
    HubConnector,
    HubNetwork)
from splight_lib import logging
from splight_lib.settings import splight_settings


HubClient = splight_settings.HUB_CLIENT
DatalakeClient = splight_settings.DATALAKE_CLIENT
DatabaseClient = splight_settings.DATABASE_CLIENT

logger = logging.getLogger()


class PDFGenerationException(Exception):
    pass

class MonthBillingNotFoundException(Exception):
    pass

class BillingGenerator:
    DEFAULT_COMPONENT_IMPACT: int = os.getenv("DEFAULT_COMPONENT_IMPACT", 1)

    def __init__(self, organization_id: str, date: datetime = None):
        """
        Initializes the billing generator.
        args:
            organization_id: The organization id

            date: The billing date. If not specified, the current date is used.
                  Think of this date as the simulation date for the billing.

            closing_month: If true, the billing considers the date's whole month data.
                           Otherwise, the billing is generated until the BillingGenerator date,
                           starting from the first day of the date's month.

        Usage examples:
        BillingGenerator(organization_id="org_id").generate()

        => Returns a MonthBilling, List[Tuple[Billing, List[BillingItem]]]
           considering all the data from the first day of the current month (when executing)
           until the moment when it's executed. Used to calculate how much money is being
           spent in the current month.

        BillingGenerator(organization_id="org_id", date=datetime(2020, 1, 15)).generate()

        => Returns a MonthBilling, List[Tuple[Billing, List[BillingItem]]]
           that simulates the billing in the 15th day of January 2020. That means,
           the billing considering all data from 1st of January 2020 until 15th of January 2020.

        BillingGenerator(organization_id="org_id", date=datetime(2020, 1)).close_month()

        => Generates and saves in database the MonthBilling and regarding List[Tuple[Billing, List[BillingItem]]]
           that corresponds to the billing for January 2020. Executed once a month.
        """

        self.organization_id: str = organization_id
        self.closing_month: bool = False
        self.date: datetime = date.replace(tzinfo=pytz.UTC) if date else datetime.now(timezone.utc)

        self.datalake_client: DatalakeClient = DatalakeClient(self.organization_id)
        self.database_client: DatabaseClient = DatabaseClient(self.organization_id)
        self.hub_client: HubClient = HubClient(token=f"Splight {os.getenv('BOT_HUB_ACCESS_ID')} {os.getenv('BOT_HUB_SECRET_KEY')}", namespace=self.organization_id)

        self.billing_settings: BillingSettings = BillingGenerator.get_billing_settings(self.date)

        # The billing types are defined in the billing_types dictionary.
        # The key is the billing type name and the value is a function that returns a tuple
        # that is (billing, billing items) item for the given billing type.

        # Edit this for further billing types.
        self.billing_types: Dict = {
            BillingEventType.COMPONENT_DEPLOYMENT: self.billing_component_deployment,
        }

    def _month_first_last_day(self, any_day):
        next_month = any_day.replace(day=28, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=4)
        last_day_of_month = next_month - timedelta(days=next_month.day)
        last_day_of_month = last_day_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)
        first_day_of_month = any_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_day_of_month = first_day_of_month.replace(tzinfo=pytz.UTC)
        last_day_of_month = last_day_of_month.replace(tzinfo=pytz.UTC)
        return first_day_of_month, last_day_of_month

    @staticmethod
    def get_billing_settings(date = None) -> BillingSettings:
        default_database_client = DatabaseClient()
        date: datetime = date.replace(tzinfo=pytz.UTC) if date else datetime.now(timezone.utc)
        billing_settings: Optional[List[BillingSettings]] = default_database_client.get(resource_type=BillingSettings, timestamp__lte=date)
        settings: BillingSettings = BillingSettings()
        if billing_settings:
            settings = billing_settings[0]
            for settings_item in billing_settings:
                if settings_item.timestamp > settings.timestamp:
                    settings = settings_item
        return settings

    def billing_component_deployment(self) -> Tuple[Billing, List[BillingItem]]:
        """
        Generates the billing for the component deployments
        Returns the Billing and the list of BillingItems
        """

        def component_impact_multiplier(default_impact: int) -> List[Dict]:
            component_types = [HubAlgorithm, HubConnector, HubNetwork]
            hub_components = []
            for type in component_types:
                hub_components.extend(self.hub_client.get(resource_type=type))
            default_impact_multiplier = Decimal(str(self.billing_settings.pricing.IMPACT_MULTIPLIER[str(default_impact)]))
            components = defaultdict(lambda: default_impact_multiplier)
            for component in hub_components:
                if component.impact:
                    components[f"{component.name}-{component.version}"] = Decimal(str(self.billing_settings.pricing.IMPACT_MULTIPLIER[str(component.impact)]))
            return components

        first_day, last_day = self._month_first_last_day(self.date)
        if not self.closing_month:
            last_day = self.date

        start = time.time()
        logger.info(f"[BILLING] Starting billing events query for {self.organization_id} ")
        billing_events: List[Dict] = list(self.datalake_client.raw_aggregate(
            collection = BillingEvent.__name__,
            pipeline = [
            {
                '$match': {'timestamp': {'$lte': last_day}}
            }, {
                '$group': {
                    '_id': '$data.id', 
                    'events': {'$push': '$$ROOT'}
                }
            }, {
                '$match': {
                    '$or': [
                        {
                            '$and': [
                                {
                                    'events': {'$size': 1}
                                }, {
                                    'events.0.event': 'create'
                                }
                            ]
                        }, {
                            '$and': [
                                {
                                    'events': {'$size': 2}
                                }, {
                                    'events.0.event': 'create'
                                }, {
                                    'events.1.event': 'destroy'
                                }, {
                                    'events.1.timestamp': {'$gte': first_day}
                                }, {
                                    'events.1.timestamp': {'$lte': last_day}
                                }
                            ]
                        }
                    ]
                }
            }
            ]
        ))
        logger.info(f"[BILLING] Billing events query for {self.organization_id} finished in {time.time() - start} seconds. {len(billing_events)} billing events found.")
        component_billing_dict: defaultdict[str, Dict] = defaultdict(
            lambda: {
                "description": "Default description",
                "computing_price": Decimal(0),
                "storage_price": Decimal(0),
                "total_price": Decimal(0),
            }
        )

        computing_price_per_hour: Decimal = Decimal(str(self.billing_settings.pricing.COMPUTING_PRICE_PER_HOUR))
        storage_price_per_gb: Decimal = Decimal(str(self.billing_settings.pricing.STORAGE_PRICE_PER_GB))

        start = time.time()
        logger.info(f"[BILLING] Starting components sizes query for {self.organization_id}")
        component_storage_sizes: Dict[str, float] = self.datalake_client.get_components_sizes_gb(start=first_day, end=last_day)
        logger.info(f"[BILLING] Components sizes query for {self.organization_id} finished in {time.time() - start} seconds. {len(component_storage_sizes)} components found.")

        impact_multipliers = component_impact_multiplier(self.DEFAULT_COMPONENT_IMPACT)

        for billing_data in billing_events:
            events = billing_data["events"]
            deployment_id = billing_data["_id"]
            events = [BillingEvent(**event) for event in events]
            info_event = None
            if len(events) == 1:
                # The event hasn't stopped yet
                start: BillingEvent = events[0]
                # If event started in previous month, set the first day of month as start date
                start.timestamp = max(first_day, start.timestamp)
                end: BillingEvent = BillingEvent(
                    type=BillingEventType.COMPONENT_DEPLOYMENT,
                    event="destroy",
                    timestamp=last_day
                )
                info_event = start
            elif len(events) == 2:
                # The event has stopped in current billing period
                start: BillingEvent = events[0]
                end: BillingEvent = events[1]
                if start.timestamp > end.timestamp:
                    start, end = end, start
                # If event started in previous month, set the first day of month as start date
                start.timestamp = max(first_day, start.timestamp)
                info_event = start
            else:
                # Should never get in here because of the DL query
                logger.warning(f"[WARNING] Found deployment with more than 2 BillingEvents: {events}. Unexpected behavior. Billing dates may not be accurate.")
                data = {
                    "id": deployment_id,
                }
                for event in events:
                    data.update(event.data)

                start: BillingEvent(
                    type=BillingEventType.COMPONENT_DEPLOYMENT,
                    event="create",
                    timestamp=first_day,
                    data=data
                )
                end: BillingEvent(
                    type=BillingEventType.COMPONENT_DEPLOYMENT,
                    event="destroy",
                    timestamp=last_day
                )
                info_event = start

            impact_multiplier = impact_multipliers[info_event.data["version"]]
            storage_used_in_gb: Decimal = Decimal(component_storage_sizes.get(info_event.data["external_id"], 0))
            duration: timedelta = end.timestamp - start.timestamp
            duration_in_hours: Decimal = Decimal(str(duration.total_seconds() / 3600))
            
            # Billing components assuming whole month usage
            if not self.billing_settings.computing_time_measurement_per_hour:
                first_day_of_month, last_day_of_month = self._month_first_last_day(self.date)
                duration: timedelta = last_day_of_month - first_day_of_month
                duration_in_hours = Decimal(str(duration.total_seconds() / 3600))

            computing_price: Decimal = computing_price_per_hour * duration_in_hours * impact_multiplier
            storage_price: Decimal = storage_price_per_gb * storage_used_in_gb * impact_multiplier

            computing_price: Decimal = computing_price.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            storage_price: Decimal = storage_price.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            underscore_latex_render = "\\_"
            component_dict = component_billing_dict[info_event.data['external_id']]
            component_dict["description"] = f"{info_event.data['type']} component named {' version '.join(info_event.data['version'].replace('_', underscore_latex_render).split('-'))} with id {info_event.data['external_id']}"
            
            if self.billing_settings.computing_time_measurement_per_hour:
                component_dict["computing_price"] += computing_price
            else:
                component_dict["computing_price"] = max(component_dict["computing_price"], computing_price)
            
            component_dict["storage_price"] = max(component_dict["storage_price"], storage_price)
            component_dict["total_price"] = Decimal(component_dict["computing_price"] + component_dict["storage_price"])

            component_dict["computing_price"] = component_dict["computing_price"].quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            component_dict["storage_price"] = component_dict["storage_price"].quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            component_dict["total_price"] = component_dict["total_price"].quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

            
        billing_items_result: List[DeploymentBillingItem] = []
        for component_id, billing_item in component_billing_dict.items():
            billing_items_result.append(
                DeploymentBillingItem(
                    description=billing_item["description"],
                    type="deployment",
                    computing_price=billing_item["computing_price"],
                    storage_price=billing_item["storage_price"],
                    total_price= billing_item["total_price"],
                )
            )

        # Calculate detailed pricing
        detailed_pricing = defaultdict(lambda: Decimal(0))
        for item in billing_items_result:
            detailed_pricing["computing_price"] = detailed_pricing["computing_price"] + Decimal(item.computing_price)
            detailed_pricing["storage_price"] = detailed_pricing["storage_price"] + Decimal(item.storage_price)

        detailed_pricing["computing_price"] = float(detailed_pricing["computing_price"].quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        detailed_pricing["storage_price"] = float(detailed_pricing["storage_price"].quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        
        # Calculate billing total price
        total_price: Decimal = Decimal(0)
        for item in billing_items_result:
                total_price += Decimal(item.total_price)
        total_price = max(Decimal(0), total_price)
        total_price = total_price.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        billing: Billing = Billing(
            description="Component deployments",
            detailed_pricing=detailed_pricing,
            items_type=DeploymentBillingItem.__name__,
            total_price=float(total_price)
        )
        billing_items: List[BillingItem] = billing_items_result
        return billing, billing_items
    
    def generate(self) -> Tuple[MonthBilling, List[Tuple[Billing, List[BillingItem]]]]:
        """
        Generates the billing for the month
        Returns the MonthBilling and a list of tuples containing the Billing and the BillingItems
        """
        logger.info(f"[BILLING] Generating billing {self.organization_id} with date {self.date}")
        start_time = time.time()
        billings: List[Tuple[Billing, List[BillingItem]]] = []
        for _, billing_function in self.billing_types.items():
            billings.append(billing_function())

        billing_discount = None
        # Only the first discount in the global discounts list will be applied
        for discount in self.billing_settings.discounts:
            if discount.organization_id == self.organization_id:
                billing_discount = discount
                break

        discount_detail = None
        if billing_discount:
            if billing_discount.type == DiscountType.PERCENTAGE:
                discount_detail = f"{billing_discount.value}\%"

        billing_price: Decimal = Decimal(0)
        for billing, _ in billings:
            billing_price += Decimal(billing.total_price)

        discount = Decimal(0)
        if billing_discount:
            discount = Decimal(billing_discount.value) if billing_discount.type == DiscountType.FIXED else billing_price * Decimal(billing_discount.value) / Decimal(100)

        discount = max(Decimal(0), discount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        billing_price = max(Decimal(0), billing_price).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        total_price = max(Decimal(0), billing_price - discount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


        month_billing: MonthBilling = MonthBilling(
            month=self.date,
            total_price_without_discount=float(billing_price),
            discount_detail=discount_detail,
            discount_value=float(discount),
            total_price=float(total_price),
        )

        logger.info(f"[BILLING] Billing generated in {time.time() - start_time} seconds for {self.organization_id}. Total price: {month_billing.total_price}")
        return month_billing, billings

    def _delete_monthbilling(self, id: str) -> None:
        previous_month_billing = self.database_client.get(MonthBilling, id=id, first=True)
        if previous_month_billing:
            logger.debug(f"[BILLING] Deleting previous billing for month {previous_month_billing}")
            previous_billings: List[Billing] = self.database_client.get(Billing, month_billing_id=previous_month_billing.id)
            previous_billing_items: List[List[BillingItem]] = [self.database_client.get(getattr(models, billing.items_type), billing_id=billing.id) for billing in previous_billings]
            for billing_items in previous_billing_items:
                for billing_item in billing_items:
                    self.database_client.delete(type(billing_item), id=billing_item.id)
            for billing in previous_billings:
                self.database_client.delete(Billing, id=billing.id)
            self.database_client.delete(MonthBilling, id=previous_month_billing.id)

    def close_month(self) -> None:
        """
        Executes when closing the month.
        Generates and saves the month billing and regarding data to the database.
        """
        logger.debug(f"[BILLING] Closing month {self.date}")
        self.closing_month=True
        month_billing, billings = self.generate()

        # Check if previous billing exists for the month
        previous_month_billings = self.database_client.get(MonthBilling, month=month_billing.month)
        for prev_month in previous_month_billings:
            logger.debug(f"[BILLING] Previous billing exists for month {prev_month.month}")
            self._delete_monthbilling(prev_month.id)

        month_billing = self.database_client.save(month_billing)
        for billing, items in billings:
            billing.month_billing_id = month_billing.id
            saved_billing = self.database_client.save(billing)
            for item in items:
                item.billing_id = saved_billing.id
                self.database_client.save(item)
        self.closing_month=False

    def generate_pdf(self, month_billing_id: str) -> bytes:
        month_billing: MonthBilling = self.database_client.get(resource_type=MonthBilling, id=month_billing_id, first=True)
        if not month_billing:
            raise MonthBillingNotFoundException
        billings: List[Billing] = self.database_client.get(resource_type=Billing, month_billing_id=month_billing.id)
        billing_items: List[BillingItem] = []
        for billing in billings:
            billing_items.append(self.database_client.get(resource_type=getattr(models, billing.items_type), billing_id=billing.id))
        billings: List[Tuple[Billing, List[BillingItem]]] = list(zip(billings, billing_items))

        env = {'block_start_string': '\BLOCK{',
              'block_end_string': '}',
              'variable_start_string': '\VAR{',
              'variable_end_string': '}',
              'comment_start_string': '\#{',
              'comment_end_string': '}',
              'line_statement_prefix': '%%',
              'line_comment_prefix': '%#',
              'trim_blocks': True,
              'autoescape': False
        }
        template_dir = os.path.dirname(__file__)
        env['loader'] = jinja2.FileSystemLoader(template_dir)
        env = jinja2.Environment(**env)
        template = env.get_template("template.tex")
        if type(month_billing) != dict:
            month_billing = month_billing.dict()

        logger.debug(f"[BILLING] Generating PDF for MonthBilling {month_billing} with the following billings: {billings}")

        render = template.render(
            **month_billing,
            logo=os.path.join(os.path.dirname(__file__), "splight-logo.png"),
            deployment_billing=billings[0][0],
            deployment_billing_items=billings[0][1]
        )
        render_filename = "render"
        render_path = os.path.join(template_dir, f"{render_filename}.tex")
        with open(render_path, "w+") as f:
            f.write(render)

        try:
            result = subprocess.run(f"pdflatex -halt-on-error -file-line-error -interaction=nonstopmode {render_path}", shell=True)
            if result.returncode != 0:
                raise PDFGenerationException("Failed to generate PDF")
            pdf_path = f"{render_filename}.pdf"
            pdf = None
            with open(pdf_path, "rb") as f:
                pdf = f.read()
            return pdf
            
        finally:
            for file in [f"{render_filename}{x}" for x in [".tex", ".aux", ".log", ".out", ".pdf"]]:
                if os.path.exists(file):
                    os.remove(file)
            if os.path.exists(render_path):
                os.remove(render_path)