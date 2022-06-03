from splight_lib.communication import Variable
from splight_lib.datalake import DatalakeClient
from splight_lib.database import DatabaseClient
from splight_models import *
from splight_lib import logging


logger = logging.getLogger()


def rule_eval(rule: AlgorithmRule, dl_client: DatalakeClient, db_client: DatabaseClient) -> bool:
    # !!WARNING: this method is using $last as aggregation method to obtain the resulting value of a rule
    if rule is None:
        return None
    
    values = {}
    for var in rule.variables:
        reads = dl_client.get(Variable, collection=var.collection, **var.filters)
        if not reads:
            continue
        read = reads[0].dict()
        for key in var.key.split("__"):
            read = read.get(key)
            if read is None:
                continue
        values[var.id] = read
    return rule.statement_evaluation(rule.statement, rule.variables, values)
