from importlib import import_module

from splight_lib.settings import api_settings

# TODO: hacer mas explicito sin magia de imports
# NOTE: dejar dl en paz
# NOTE: compatir db client

# Get API version
api_version = api_settings.API_VERSION

# Import the version module
models_module = import_module(f"splight_lib.models._{api_version}")

# Select the exposed models only
model_names = getattr(models_module, "__all__", [])

# Bring those models to this scope
for model_name in model_names:
    globals()[model_name] = getattr(models_module, model_name)

# Restrict what we expose from this module
__all__ = model_names
