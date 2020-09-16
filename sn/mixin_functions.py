from functools import wraps
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sites.shortcuts import get_current_site

import traceback
 

def showEmptyPage(resultType): # resultType === 'chats' or 'messages'
    return {
            'links': {
                'next': None,
                'previous': None
            },
            'currentPage': 0,
            'pagesNumber': 0,
            resultType: {
                        "items": [],
                        "totalCount": 0, # all elements accross all pages
                        "error": None
                    }
            }
 
def listsPaginatorP(request, queryset_list, query, resultType): 
    page = request.GET.get("page") # при каждой прогрузке увеличиваем в реакте
    paginator = Paginator(queryset_list, 5)

    try:
        queryset = paginator.page(page) # its now paginator
    except PageNotAnInteger: 
        if len(paginator.object_list) == 0:
            return showEmptyPage(resultType)
        else:
            queryset = paginator.page(1)
            
    except EmptyPage: 
        if paginator.num_pages == 0:
            return showEmptyPage(resultType)
        else:
            queryset = paginator.page(paginator.num_pages)

    results = {
            "items": [item for item in queryset],
            "totalCount": len(paginator.object_list), # all elements accross all pages
            "error": None
            }

    nextLink = None
    prevLink = None
    if queryset.has_next():
        if query:
            nextLink = get_current_site(request).domain  + request.path + '?page=' + str(queryset.next_page_number()) + '&q=' + query
        else:
            nextLink = get_current_site(request).domain  + request.path + '?page=' + str(queryset.next_page_number())

    if queryset.has_previous():
        if query:
            prevLink = get_current_site(request).domain  + request.path + '?page=' + str(queryset.previous_page_number()) + '&q=' + query
        else:
            prevLink = get_current_site(request).domain  + request.path + '?page=' + str(queryset.previous_page_number())

    return {
        'links': {
            'next': nextLink,
            'previous': prevLink 
        }, 
        'currentPage': queryset.number,
        'pagesNumber': paginator.num_pages, 
        resultType: results
    }



 
def listsPaginatorM(request, queryset_list, readFromIndex, readFromIndexNext, readFromIndexBefore):  
    totalCount = len(queryset_list)
    msgsToShow=[]
    for msg in queryset_list:
        if msg['id'] >= readFromIndex:
            msgsToShow.append(msg)
    results = { # readFromIndex = msgs[0] so we dont dispatch it 
            "items": msgsToShow,
            "totalCount": totalCount, # all elements accross all pages
            "readFromIndexNext": readFromIndexNext,
            "readFromIndexBefore": readFromIndexBefore,
            "error": None
            } 
    return results




def responseDecorator(method):
    @wraps(method)
    def _impl(self, request, *method_args, **method_kwargs): 
        resultCode = 0
        messages = []
        status = HTTP_200_OK
        method_output = None # is a dict of data
        
        try: 
            method_output = method(self, request, *method_args, **method_kwargs) 
            if(isinstance(method_output, tuple)):
                if(len(method_output) > 2): # e.i. there was an error in request and there is some error messages 
                    if('errorMessage' in method_output[2]):
                        messages.append(method_output[2]['errorMessage'])
                        resultCode = 1
                    else:
                        raise KeyError('there is no appropriate key (errorMessage) in error dictionary')
                status = method_output[1] 
                method_output = method_output[0] 
        except Exception:
            resultCode = 1
            status = HTTP_400_BAD_REQUEST
            messages.append(f'Error while running method {method} with args: {method_args} and kwargs {method_kwargs} \n')
            messages.append(f'{traceback.format_exc()}')
        
        response = {
            'data': method_output, # true // false ( witch method was (post or delete)),
            'resultCode': resultCode,
            'messages': messages
        }

        return Response(response, status=status)

    return _impl
