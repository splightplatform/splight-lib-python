import yaml
# TODO MOVE THIS STUFF
from typing import Type, Dict, Tuple, Any, Optional
from pydantic import BaseSettings, Extra
from importlib import import_module
from pydantic.env_settings import SettingsSourceCallable
import os
import sys

TESTING = "test" in sys.argv or "pytest" in sys.argv
SPLIGHT_HOME = os.path.join(os.getenv('HOME'), '.splight')
USE_TZ = True
# EOTODO


"""
Settings for SPLIGHT framework are all namespaced in the SPLIGHT_FRAMEWORK setting.
For example your project's `settings.py` file might look like this:

SPLIGHT_FRAMEWORK = {
    'DATABASE_CLIENT': 'splight_lib.database.FakeDatabaseClient'
}

This module provides the `setup` object, that is used to access
SPLIGHT framework settings, checking for user settings first, then falling
back to the defaults.
"""


def yml_config_setting(settings: BaseSettings) -> Dict[str, Any]:
    config = {}
    config_file = os.path.join(SPLIGHT_HOME, "config")
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)
        if "workspaces" in config:  # splight format config
            workspace = config.get("current_workspace", "default")
            config = config["workspaces"].get(workspace, {})
    # Set the environment for each model. The models should reload the respective setup.
    for key, value in config.items():
        os.environ[key] = value
    return config


class SplightBaseSettings(BaseSettings):
    # TODO move all the private use only clients to private lib. Not need to define here those without remote implementation
    AUTH_CLIENT: str = 'fake_splight_lib.auth.FakeAuthClient'
    BLOCKCHAIN_CLIENT: str = 'fake_splight_lib.blockchain.FakeBlockchainClient'
    DATABASE_CLIENT: str = 'fake_splight_lib.database.FakeDatabaseClient'
    DATALAKE_CLIENT: str = 'fake_splight_lib.datalake.FakeDatalakeClient'
    DEPLOYMENT_CLIENT: str = 'fake_splight_lib.deployment.FakeDeploymentClient'
    CACHE_CLIENT: str = 'fake_splight_lib.cache.FakeCacheClient'
    COMMUNICATION_CLIENT: str = 'fake_splight_lib.communication.FakeCommunicationClient'
    NOTIFICATION_CLIENT: str = 'fake_splight_lib.notification.FakeNotificationClient'  # TODO deprecate this
    HUB_CLIENT: str = 'fake_splight_lib.hub.FakeHubClient'
    NAMESPACE: str = "NO_NAMESPACE"

    @property
    def importables(self):
        return [
            'AUTH_CLIENT',
            'BILLING_CLIENT',
            'BLOCKCHAIN_CLIENT',
            'DATABASE_CLIENT',
            'DATALAKE_CLIENT',
            'DEPLOYMENT_CLIENT',
            'CACHE_CLIENT',
            'NOTIFICATION_CLIENT',
            'HUB_CLIENT',
            'COMMUNICATION_CLIENT',
        ]

    class Config:

        extra = Extra.ignore

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, yml_config_setting, env_settings


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        ) from err


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class SplightSettings:

    def __init__(self, user_settings={}, base_settings_model: Type[SplightBaseSettings] = SplightBaseSettings):
        self._cached_attrs = set()
        self._base_settings_model = base_settings_model
        self._base_settings = self._base_settings_model()
        self.configure(user_settings)

    @property
    def settings(self) -> Type[SplightBaseSettings]:
        return self._base_settings

    def __getattr__(self, attr):
        if not hasattr(self._base_settings, attr):
            raise AttributeError("Invalid API setting: '%s'" % attr)
        val = getattr(self._base_settings, attr)

        # Coerce import strings into classes
        if attr in self._base_settings.importables:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def configure(self, user_settings: Optional[Dict[str, str]] = None):
        if user_settings is None:
            user_settings = {}

        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        # This is setting the environment and
        # each model reloads the respective setup from there
        for key, value in user_settings.items():
            os.environ[key] = value
        # Reload settings
        self._base_settings = self._base_settings_model.parse_obj(user_settings)
        return self


setup = SplightSettings()
