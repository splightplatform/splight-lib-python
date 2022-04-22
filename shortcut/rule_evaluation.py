from splight_lib.communication import Variable
from splight_lib.datalake import DatalakeClient
from splight_lib.database import DatabaseClient
from splight_models import *
from splight_lib import logging


logger = logging.getLogger()


def rule_eval(rule_id: str, dl_client: DatalakeClient, db_client: DatabaseClient) -> bool:
    # !!WARNING: this method is using $last as aggregation method to obtain the resulting value of a rule
    rule = db_client.get(Rule, id=rule_id, first=True)
    if rule is None:
        return None
    
    values = {}
    for var in rule.variables:
        reads = dl_client.get(Variable, collection=var.collection, **var.filters)
        if not reads:
            continue
        values[var.id] = reads[0].args.get(var.key)
    return rule.statement_evaluation(rule.statement, rule.variables, values)
