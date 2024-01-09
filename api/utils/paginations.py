from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response

class CustomPagination(LimitOffsetPagination):
    """
    Custom pagination class that modifies the default LimitOffsetPagination behavior in Django Rest Framework.
    This class sets a custom default limit for items per page and introduces an additional 'geom_count' in the response.

    Attributes:
        default_limit (int): Overrides the global 'PAGE_SIZE' setting from DRF if set. Defines the default number 
                             of items to display per page. Default is set to 25.
        geom_count (int): Attribute to store the count of features with non-null 'geom' fields.
    """
    default_limit = 25
    geom_count = 0  # Initialize attribute to store geom count

    def paginate_queryset(self, queryset, request, view=None):
        """
        Overrides paginate_queryset to compute the count of Features with non-null 'geom'.

        This method is called before the pagination of the queryset to capture the count of Features
        with non-null 'geom' and store it in a class attribute for later use.

        Parameters:
            queryset: The queryset to be paginated.
            request: The HttpRequest object.
            view: The view using this pagination.

        Returns:
            list: The list of objects after applying pagination.
        """
        # Compute the count before pagination
        self.geom_count = queryset.filter(geom__isnull=False).count()

        # Call parent method to perform actual pagination
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """
        Overrides the standard paginated response to include the 'geom_count' field.

        This method extends the standard paginated response by adding the 'geom_count' field, 
        which represents the count of Feature objects with non-null 'geom' fields in the queryset. 
        This additional information is useful for front-end applications, particularly for map-based interfaces.

        Parameters:
            data (list): The list of serialized data objects for the current page.

        Returns:
            Response: The paginated response with standard details and an additional 'geom_count'.
        """
        # Use the geom_count attribute for the paginated response
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'geom_count': self.geom_count,
            'results': data
        })


class SimplePagination(PageNumberPagination):
    """
    Simplified custom pagination class inheriting from PageNumberPagination in Django Rest Framework.

    This class offers basic pagination functionality with adjustable page size through query parameters. 
    It also imposes a maximum limit on page size for performance considerations.

    Attributes:
        page_size (int): The default number of items per page. Can be overridden by client's request.
        page_size_query_param (str): Query parameter for clients to specify desired page size.
        max_page_size (int): The upper limit for page size to prevent performance degradation on large requests.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
