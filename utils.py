import hashlib
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe
from strawberry import UNSET
from strawberry_django.filters import apply as filter_apply
from strawberry_django.pagination import apply as pagination_apply
from strawberry_django.ordering import apply as ordering_apply
from dataclasses import asdict


REDIS_TTL = 86400  # Seconds


async def get_async_list_from_queryset(qs):
    return [
        item async for item in qs
    ]


def generate_id_from_unique_field(unique_value):
    return int(hashlib.sha1(unique_value.encode("utf-8")).hexdigest(), 16) % (10 ** 8)


def generate_id_from_unique_fields(obj):
    unique_value = ''.join(
        [
            str(
                getattr(obj, item)
            ) for item in obj._meta.model._meta.unique_together[0]
        ]
    )
    return int(hashlib.sha1(unique_value.encode("utf-8")).hexdigest(), 16) % (10 ** 8)


def generate_id_from_unique_non_model_fields(unique_field_list):
    unique_value = ''.join([str(item) for item in unique_field_list])
    return int(hashlib.sha1(unique_value.encode("utf-8")).hexdigest(), 16) % (10 ** 8)


def set_redis_cache_data(*keys, value=None):
    redis_key = '-'.join(filter(None, list(keys)))
    return cache.set(redis_key, value, REDIS_TTL)


def get_redis_cache_data(*keys):
    redis_key = '-'.join(filter(None, list(keys)))
    return cache.get(redis_key)


def get_values_list_from_dataclass(data_class):
    if data_class:
        return [value for value in asdict(data_class).values() if value != UNSET]
    return []


def clean_filters(filters):
    # Filter out None values
    return {
        k: v
        for k, v in filters.items()
        if v is not None
    }


def cache_clear(request):
    cache.clear()
    messages.add_message(request, messages.INFO, mark_safe("Cache Cleared"))
    return HttpResponseRedirect(reverse('admin:index'))


async def get_filtered_ordered_paginated_qs(
    qs, filters, order, pagination
):
    if filters:
        qs = filter_apply(filters, qs)
    if order:
        qs = ordering_apply(order, qs)
    if pagination:
        qs = pagination_apply(pagination, qs)
    return await get_async_list_from_queryset(qs)
