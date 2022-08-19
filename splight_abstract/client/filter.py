import re
from typing import List, Any

class FilterMixin:
    reserved_filter_keys = ["__in", "__contains", "__lte", "__gte"]

    def _get_field_value(self, x: Any, field: str):
        for reserved_key in self.reserved_filter_keys:
            field = field.replace(reserved_key, "")

        if "__" in field:
            key, subkey = field.split("__")
            try:
                return x.get(key, {}).get(subkey)
            except:
                pass
            try:
                return getattr(x, key).get(subkey)
            except:
                return None
        return getattr(x, field)

    def _check_in(self, x: Any, field: str, value: Any):
        field = self._get_field_value(x,field)
        try:
            return field in value
        except:
            return False

    def _check_contains(self, x: Any, field: str, value: Any):
        field = self._get_field_value(x, field)
        try:
            return value in field
        except:
            return False

    def _filter(self, queryset: list, **kwargs) -> list:
        '''
        Filter a queryset by the given kwargs.
        '''
        field_filters = [
            lambda x, field=field, value=value: self._get_field_value(x, field) == value for field, value in kwargs.items() if "__" not in field
        ]
        in_filters = [
            lambda x, field=field, values=values: self._check_in(x, field, values) for field, values in kwargs.items() if field.endswith("__in")
        ]
        contains_filters = [
            lambda x, field=field, value=value: self._check_contains(x, field, value) for field, value in kwargs.items() if field.endswith("__contains")
        ]
        dict_filters = [
            lambda x, field=field, value=value: self._get_field_value(x, field) == value for field, value in kwargs.items() if "__" in field and not any(field.endswith(reserved_key) for reserved_key in self.reserved_filter_keys)
        ]
        filters = field_filters + in_filters + contains_filters + dict_filters

        return [obj for obj in queryset if all([f(obj) for f in filters])]

    def _validated_kwargs(self, allowed_fields: List[str], **kwargs):
        '''
        Validate the given kwargs.
        '''
        valid_kwargs = [
            f"{field}__in" for field in allowed_fields
        ] + [
            f"{field}__contains" for field in allowed_fields
        ] + [
            f"{field}__lte" for field in allowed_fields
        ] + [
            f"{field}__gte" for field in allowed_fields
        ] + allowed_fields

        invalid_kwargs = []
        for key in kwargs.keys():
            if key not in valid_kwargs and not any(key.startswith(f"{allowed_field}__") for allowed_field in allowed_fields):
                invalid_kwargs.append(key)

        for key in invalid_kwargs:
            kwargs.pop(key)
        return kwargs
