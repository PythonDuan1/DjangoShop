from django.urls import path,re_path
from StoreApp.views import *

urlpatterns = [
    path('register/',register),

    path('login/',login),
    path('logout/',logout),

    path('index/',index),
    re_path('^$',index),
    path('base/',base),
    path('rs/',register_store),
    path('add_goods/',add_goods),

    path('goods_type_list/',goods_type_list),#商品类型列表页
    path('delete_goods_type/',delete_goods_type),#删除商品类型

    path('order_list/',order_list),#订单列表页
    path('delete_order/',delete_order),#删除订单（卖家拒绝发货）
    path('affirm_order/',affirm_order), #确认发货
    path('completed_order/',completed_order),#已完成订单

    re_path(r'list_goods/(?P<state>\w+)/',list_goods),
    re_path(r'^goods/(?P<goods_id>\d+)',goods),
    re_path(r'update_goods/(?P<goods_id>\d+)',update_goods),
    re_path(r'set_goods/(?P<state>\w+)/',set_goods),

]

urlpatterns += [
    path('agl/',ajax_goods_list),
]