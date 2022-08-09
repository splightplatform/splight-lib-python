from typing import List

class FilterMixin:
    def _filter(self, queryset: list, **kwargs) -> list:
        '''
        Filter a queryset by the given kwargs.
        '''
        field_filters = [
            lambda x, field=field, value=value: getattr(x, field) == value for field, value in kwargs.items() if "__" not in field
        ]
        in_filters = [
            lambda x, field=field, values=values: getattr(x, field.replace("__in", "")) in values for field, values in kwargs.items() if field.endswith("__in")
        ]
        contains_filters = [
            lambda x, field=field, value=value: value in getattr(x, field.replace("__contains", "")) for field, value in kwargs.items() if field.endswith("__contains")
        ]

        filters = field_filters + in_filters + contains_filters

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

        invalid_kwargs = [key for key in kwargs.keys() if key not in valid_kwargs]
        for key in invalid_kwargs:
            kwargs.pop(key)
        return kwargs
