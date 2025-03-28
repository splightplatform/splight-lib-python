from splight_lib.settings import SplightAPIVersion, api_settings

if api_settings.API_VERSION != SplightAPIVersion.V4:
    raise ImportError(
        f"Unable to import models from this module when API_VERSION is not set to '{SplightAPIVersion.V4}'"
    )


__all__ = []
