# TODO MOVE THIS STUFF 
import os, sys
TESTING = "test" in sys.argv or "pytest" in sys.argv
SPLIGHT_HOME = os.path.join(os.getenv('HOME'), '.splight')
USE_TZ = True

"""
Settings for SPLIGHT framework are all namespaced in the SPLIGHT_FRAMEWORK setting.
For example your project's `settings.py` file might look like this:

SPLIGHT_FRAMEWORK = {
    'DEFAULT_DATABASE_CLIENT': 'splight_lib.database.FakeDatabaseClient'
}

This module provides the `splight_settings` object, that is used to access
SPLIGHT framework settings, checking for user settings first, then falling
back to the defaults.
"""
from importlib import import_module
import os
import sys


DEFAULTS = {
    'BLOCKCHAIN_CLIENT': 'fake_splight_lib.blockchain.FakeBlockchainClient',
    'DATABASE_CLIENT': 'fake_splight_lib.database.FakeDatabaseClient',
    'DATALAKE_CLIENT': 'fake_splight_lib.datalake.FakeDatalakeClient',
    'DEPLOYMENT_CLIENT': 'fake_splight_lib.deployment.FakeDeploymentClient',
    'CACHE_CLIENT': 'fake_splight_lib.cache.RedisClient',
    'NOTIFICATION_CLIENT': 'fake_splight_lib.notification.FakeNotificationClient',
    'STORAGE_CLIENT': 'fake_splight_lib.storage.FakeStorageClient',
    'HUB_CLIENT': 'fake_splight_lib.hub.FakeHubClient',
    'INTERNAL_COMMUNICATION_CLIENT': 'fake_splight_lib.communication.FakeCommunicationClient',
    'EXTERNAL_COMMUNICATION_CLIENT': 'fake_splight_lib.communication.FakeCommunicationClient',
    'DATABASE_CLASSMAP': 'algo'
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = [
    'BLOCKCHAIN_CLIENT',
    'DATABASE_CLIENT',
    'DATALAKE_CLIENT',
    'DEPLOYMENT_CLIENT',
    'CACHE_CLIENT',
    'NOTIFICATION_CLIENT',
    'STORAGE_CLIENT',
    'HUB_CLIENT',
    'INTERNAL_COMMUNICATION_CLIENT',
    'EXTERNAL_COMMUNICATION_CLIENT',
]

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
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()
        self._user_settings = {}

    @property
    def user_settings(self):
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        return user_settings

    def reload(self, user_setttings={}):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if user_setttings:
            self._user_settings = user_setttings


splight_settings = SplightSettings(None, DEFAULTS, IMPORT_STRINGS)

def splight_configure(settings_dict):
    splight_settings.reload(user_setttings=settings_dict)
