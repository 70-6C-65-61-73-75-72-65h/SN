from rest_framework.response import Response

from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
    )


# offset - смещение с какого елемента будет счет
# limit - к-во елементов для запроса
class SNUserLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class SNUserPageNumberPagination(PageNumberPagination):
    page_size = 5
    
    def get_paginated_response(self, data):

        results = error = items = totalCount = None
        try: 
            items = [{"userId": user['userId'], "name": user['name'], "status": user['status'], "photos": user['photos'], "userRelation": user['userRelation']} for user in data]
 
        except Exception as ex:
            error = str(ex) 
        results = {
                "items": items,
                "totalCount": self.page.paginator.count,
                "error": error
                } 

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'users': results
        })