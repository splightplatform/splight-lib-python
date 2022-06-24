from jsonpath_ng.ext import parse
from jsonpath_ng import JSONPathError
from typing import List, Any, Union, Optional
from shortcut.exceptions import ShortcutException
from splight_lib.communication import Variable, Message, Action, ExternalCommunicationClient
from splight_lib.datalake import DatalakeClient
from splight_lib.database import DatabaseClient
from splight_models import *
from splight_lib import logging

logger = logging.getLogger()


class NoDefaultValue:
    pass


def _get_asset_attribute_mapping(asset_id: str, attribute_id: str, database_client: DatabaseClient) -> Union[ClientMapping, ValueMapping]:
    '''
    This function resolves an attribute values to be eather a values o client mappings.
    '''
    reference_mapping: Optional[ReferenceMapping] = database_client.get(resource_type=ReferenceMapping, first=True, asset_id=asset_id, attribute_id=attribute_id)
    if reference_mapping:
        return _get_asset_attribute_mapping(reference_mapping.ref_asset_id, reference_mapping.ref_attribute_id, database_client)

    client_mapping: Optional[ClientMapping] = database_client.get(resource_type=ClientMapping, first=True, asset_id=asset_id, attribute_id=attribute_id)
    if client_mapping:
        return client_mapping

    value_mapping: ValueMapping = database_client.get(resource_type=ValueMapping, first=True, asset_id=asset_id, attribute_id=attribute_id)
    if value_mapping:
        return value_mapping

    raise AttributeError("No mapping found")


def _asset_read(asset_id: str, attribute_id: str, datalake_client: DatalakeClient, database_client: DatabaseClient) -> Any:
    '''
    This function returns the value of an attribute of an asset. (Helper function for asset_get)
    '''
    mapping: Union[ClientMapping, ValueMapping] = _get_asset_attribute_mapping(asset_id=asset_id, attribute_id=attribute_id, database_client=database_client)
    if type(mapping) == ClientMapping:
        variable: Variable = Variable(asset_id=mapping.asset_id,
                                        attribute_id=mapping.attribute_id,
                                        args=dict())

        variable = datalake_client.get(Variable, asset_id=variable.asset_id, attribute_id=variable.attribute_id)

        if not variable:
            raise AttributeError("No variable value found")

        return variable[0].args["value"]

    elif type(mapping) == ValueMapping:
        return mapping.value
    
    else:
        raise NotImplementedError


def _asset_write(asset_id: str, attribute_id: str, value: Any, database_client: DatabaseClient, communication_client: ExternalCommunicationClient) -> None:
    '''
    This function writes a value to an attribute of an asset. (Helper function for asset_set)
    '''
    mapping: Union[ClientMapping, ValueMapping] = _get_asset_attribute_mapping(asset_id=asset_id, attribute_id=attribute_id, database_client=database_client)

    if type(mapping) == ClientMapping:
        variable: Variable = Variable(asset_id=mapping.asset_id, attribute_id=mapping.attribute_id, args=dict(value=value), path=mapping.path)
        msg: Message = Message(action=Action.WRITE, variables=[variable])
        logger.debug(f"Executing write asset attribute. external communication = {communication_client}, message = {msg}")
        communication_client.send(msg.dict())
        logger.debug(f"Write message sent through {communication_client}: {msg}. {communication_client.topic}")

    elif type(mapping) == ValueMapping:
        mapping.value = str(value)
        database_client.save(mapping)

    else:
        raise NotImplementedError


def get_asset_attributes(asset_id: str, database_client: DatabaseClient) -> List[Attribute]:
    '''
    This function returns all the attributes of an asset.
    '''
    mappings = [m for mapping_type in [ClientMapping, ValueMapping, ReferenceMapping] for m in database_client.get(mapping_type, asset_id = asset_id)]
    attributes: List[Attribute] = database_client.get(Attribute, id__in=[m.attribute_id for m in mappings])
    distinct_attributes = set()
    return [a for a in attributes if a.id not in distinct_attributes and not distinct_attributes.add(a.id)]


def asset_get(asset_id: str, attribute_id: str, namespace: str, default=NoDefaultValue) -> Any:
    '''
    This function returns the value of an attribute of an asset.
    '''
    # WARNING: this method is using $last as aggregation method to obtain the resulting value of a rule
    dl_client = DatalakeClient(namespace)
    db_client = DatabaseClient(namespace)
    try:
        return _asset_read(asset_id=asset_id, attribute_id=attribute_id, datalake_client=dl_client, database_client=db_client)
    except AttributeError as e:
        if default != NoDefaultValue:
            return default
        raise e


def asset_set(asset_id: str, attribute_id: str, value: Any, namespace: str) -> None:
    '''
    This function writes a value to an attribute of an asset.
    '''
    db_client = DatabaseClient(namespace)
    q_client = ExternalCommunicationClient(namespace)
    _asset_write(asset_id=asset_id, attribute_id=attribute_id, value=value, database_client=db_client, communication_client=q_client)


def asset_load_history(
        asset_id: str,
        dataframe: pd.DataFrame,
        db_client: DatabaseClient,
        dl_client: DatalakeClient
    ) -> None:
    """
    Loads history from dataframe with timestamp column
    """
    mappings = db_client.get(ClientMapping, asset_id=asset_id)
    logger.info(mappings)

    try:
        dataframe.timestamp = pd.to_datetime(dataframe.timestamp)
    except Exception as e:
        raise ShortcutException(f"Invalid dataframe. Check timestamp column: {str(e)}")

    for _, row in dataframe.iterrows():
        for map in mappings:
            try:
                jsonpath = parse(map.path)
            except JSONPathError:
                logger.error(f"Not possible to parse {map.path}")
                continue
            variables = [
                Variable(
                    timestamp=row.timestamp,
                    asset_id=map.asset_id,
                    attribute_id=map.attribute_id,
                    path=map.path,
                    args={
                        "value": match.value,
                    }
                )
                for match in jsonpath.find([row.to_dict()])
            ]
            if not variables:
                continue
            dl_client.save(
                Variable,
                instances = variables
            )


