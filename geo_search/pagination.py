from rest_framework.pagination import PageNumberPagination
from urllib.parse import unquote


class Pagination(PageNumberPagination):
    page_size_query_param = "page_size"

    def get_next_link(self):
        link = super().get_next_link()
        if link:
            link = unquote(link)
        return link

    def get_previous_link(self):
        link = super().get_previous_link()
        if link:
            link = unquote(link)
        return link
