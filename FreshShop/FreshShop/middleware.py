#coding:utf-8
import os
import datetime
from django.http import HttpResponse
from FreshShop.settings import BASE_DIR
from django.utils.deprecation import MiddlewareMixin

class MiddlewareTest(MiddlewareMixin):
    def process_response(self,request,response):
        response.set_cookie("hhh","666")
        return response



# class MiddlewareTest(MiddlewareMixin):
#     def process_template_response(self,request,response):
#         print("这是process_template_response")
#         return response

# class MiddlewareTest(MiddlewareMixin):
#     def process_exception(self,request,exception):
#         now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         level = "Error"
#         content = str(exception)
#         log_result = "%s [%s] %s\n"%(now,level,content)
#         file_path = os.path.join(BASE_DIR,"error.log")
#         with open(file_path,"a") as f:
#             f.write(log_result)
#         print(exception)


# class MiddlewareTest(MiddlewareMixin):
#     def process_view(self,request,view_func,view_args,view_kwargs):
#         print(view_func)


# class MiddlewareTest(MiddlewareMixin):
#     def process_request(self,request):
#         username = request.GET.get("username")
#         if username and username=="xd":
#             return HttpResponse("404")


# class MiddlewareTest(MiddlewareMixin):
#     def process_request(self,request):
#         print("这是process_request")
#
#     def process_view(self,request,view_func,view_args,view_kwargs):
#         print("这是process_view")
#
#     def process_exception(self,request,exception):
#         print("这是process_exception")
#
#     def process_template_response(self,request,response):
#         print("这是process_template_response")
#         return response
#
#     def process_response(self,request,response):
#         print("这是process_response")
#         return response


# class MiddlewareTest1(MiddlewareMixin):
#     def process_request(self,request):
#         print("这是process_request1")
#
#     def process_response(self,request,response):
#         print("这是process_response1")
#         return response
#
#
# class MiddlewareTest2(MiddlewareMixin):
#     def process_request(self,request):
#         print("这是process_request2")
#
#     def process_response(self,request,response):
#         print("这是process_response2")
#         return response