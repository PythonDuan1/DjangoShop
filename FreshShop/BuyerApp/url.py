from django.urls import path,include
from BuyerApp.views import *
urlpatterns = [
    path('base/',base),
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('logout/',logout),
    path('goods_list/',goods_list),#商品列表页
    path('goods_detail/',goods_detail), #商品详情页
    path('goods_cart/',goods_cart), #商品购物车页
    path('count_cart/',count_cart), #统计购物车内商品数量

    path('place_order/',place_order), #商品提交订单页

]

urlpatterns += [
    path('base/',base),
    path('base1/',base_1),#购物车与提交订单页面
    path('pay_order/',pay_order), #商品支付订单页面
    path('pay_result/',pay_result), #支付结果页面

]
