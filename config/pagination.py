from rest_framework.pagination import LimitOffsetPagination as BaseLimitOffsetPagination


class LimitOffsetPagination(BaseLimitOffsetPagination):
    max_limit = 50
