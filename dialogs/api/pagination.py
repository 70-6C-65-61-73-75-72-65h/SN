from rest_framework.response import Response

from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
    )


# offset - смещение с какого елемента будет счет
# limit - к-во елементов для запроса
class ChatLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100
