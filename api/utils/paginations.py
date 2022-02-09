from rest_framework.pagination import LimitOffsetPagination
from rest_framework import pagination

class CustomPagination(LimitOffsetPagination):
    default_limit = 25

class SimplePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
