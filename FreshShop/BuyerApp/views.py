import time

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect
from django.db.models import Sum

from BuyerApp.models import *
from StoreApp.views import set_password
from StoreApp.models import *

from alipay import AliPay


def loginValid(fun):

    #判断用户是否用cookie登录，这段代码就是为了判断登录后是谁登录的！！
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            user = Buyer.objects.filter(username = c_user).first()
            if user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/buyerapp/login/")
    return inner

def base(request):
    return render(request,"buyerapp/base.html")
# Create your views here.


def register(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")

        buyer = Buyer()
        buyer.username = username
        buyer.password = set_password(password)
        buyer.email = email
        buyer.save()
        return HttpResponseRedirect("/buyerapp/login/")
    return render(request,"buyerapp/register.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                if user.password == web_password:
                    response = HttpResponseRedirect("/buyerapp/index/")
                    response.set_cookie("username",user.username)
                    request.session["username"] = user.username

                    response.set_cookie("user_id",user.id)
                    return response
    return render(request,"buyerapp/login.html")

#商品前台首页
@loginValid
def index(request):
    result_list = []
    goods_type_list = GoodsType.objects.all()
    for goods_type in goods_type_list:
        goods_list = goods_type.goods_set.values()[:4] #values()输出一个Query列表嵌套字典的对象
        if goods_list:
            goodsType = {
                "id":goods_type.id,
                "name":goods_type.name,
                "descripton":goods_type.descripton,
                "picture":goods_type.picture,
                "goods_list":goods_list
            }
            result_list.append(goodsType)

    return render(request,"buyerapp/index.html",locals())

#商品列表页
@loginValid
def goods_list(request):
    goodsList = []
    type_id = request.GET.get("type_id")
    #获取类型
    goods_type = GoodsType.objects.filter(id = type_id).first()
    if goods_type:
        #获取所有上架的商品
        goodsList = goods_type.goods_set.filter(goods_under=1)
    return render(request,"buyerapp/goods_list.html",locals())


#前台商品详情页
@loginValid
def goods_detail(request):
    goods_id = request.GET.get("id")
    if goods_id:
        goods = Goods.objects.filter(id = goods_id).first()
        if goods:
            return render(request,"buyerapp/goods_detail.html",locals())
    return HttpResponse("没有您指定的商品")



#前台商品购物车页（从数据库中取数据进行展示）
@loginValid
def goods_cart(request):
    user_id = request.COOKIES.get("user_id")
    goods_list = Cart.objects.filter(user_id = user_id) #当前用户购物车内的每条商品信息（数据库中取数据）
    if request.method == "POST":
        post_data = request.POST
        cart_data = [] #收集前端传过来的商品
        for k,v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(Cart.objects.get(id = int(v))) #加的是购物车中一个个的商品实例
        # print(cart_data)
        # print(len(cart_data))
        # print(sum([int(i.goods_total)for i in cart_data]))
        goods_count = len(cart_data) #购物车提交过来商品条数
        goods_tatal = sum([int(i.goods_total)for i in cart_data]) #订单总价

        """
         #修改使用聚类查询返回指定商品的总价
        #1、查询到所有的商品
        cart_data = []  # 收集前端传过来的商品的id
        for k, v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(int(v)) # v 是购物车的id
        #2、使用 in 方法 进行范围的划定，然后使用Sum方法进行计算
        cart_goods = Cart.objects.filter(id__in=cart_data).aggregate(Sum("goods_total")) #获取到总价
        print(cart_goods)
        """
        #保存订单
        order = Order()
        order.order_id = setOrder_id(user_id,goods_count,"2")
        order.goods_count = goods_count #总共买了几种商品
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = goods_tatal
        order.order_status = 1
        order.save()

        #保存订单详情
        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order
            order_detail.goods_id = detail.goods_id
            order_detail.goods_name = detail.goods_name
            order_detail.goods_price = detail.goods_price
            order_detail.goods_number = detail.goods_number #同一个商品买了几件
            order_detail.goods_total = detail.goods_total
            order_detail.goods_store = detail.goods_store
            order_detail.goods_image = detail.goods_picture
            order_detail.save()
        url = "/buyerapp/place_order/?order_id=%s"%order.id
        return HttpResponseRedirect(url) #重定向到提交订单页面

    return render(request,"buyerapp/goods_cart.html",locals())

#向购物车添加商品（保存到数据库）
@loginValid
def add_cart(request):
    result = {"state":"error","data":""}
    if request.method == "POST":
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")

        goods = Goods.objects.get(id = int(goods_id)) #获取商品详情页中的具体商品，然后加入购物车

        user_id = request.COOKIES.get("user_id")

        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_price = goods.goods_price #商品单价
        cart.goods_total = goods.goods_price*count #商品总价
        cart.goods_number = count #商品数量
        cart.goods_picture = goods.goods_image
        cart.goods_id = goods.id
        cart.goods_store = goods.store_id.id #商品商店id
        cart.user_id = user_id
        cart.save()
        result["state"]="success"
        result["data"]="商品添加购物车成功"
    else:
        result["data"]="请求错误"
    return JsonResponse(result)


#设置订单编号
def setOrder_id(user_id,goods_id,store_id):
    strtime = time.strftime("%Y%m%d%H%M%S",time.localtime())
    return strtime+str(user_id)+str(goods_id)+str(store_id)

#商品提交订单页
@loginValid
def place_order(request):
    if request.method == "POST":
        #post数据
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")

        #cookie数据
        user_id = request.COOKIES.get("user_id")

        #数据库数据
        goods = Goods.objects.get(id = goods_id)
        store_id = goods.store_id.id #获取商品对应的店铺的id（店铺商品现在是一对多关系）
        price = goods.goods_price

        #保存订单表
        order = Order()
        order.order_id = setOrder_id(str(user_id),str(goods_id),str(store_id))
        order.goods_count = count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = count * price
        order.order_status = 1 #补充生成订单时，订单状态是未支付（1）
        order.save()

        #保存订单详情表
        order_detail = OrderDetail()
        order_detail.order_id = order
        order_detail.goods_id= goods_id
        order_detail.goods_name=goods.goods_name
        order_detail.goods_price = goods.goods_price
        order_detail.goods_number = count
        order_detail.goods_total = count*goods.goods_price
        order_detail.goods_store = store_id
        order_detail.goods_image = goods.goods_image

        order_detail.save()

        detail = [order_detail]

        return render(request,"buyerapp/place_order.html",locals())
    else:
        order_id = request.GET.get("order_id")
        if order_id:
            order = Order.objects.get(id = order_id)
            detail = order.orderdetail_set.all()
            return render(request,"buyerapp/place_order.html",locals())
        else:
            return HttpResponseRedirect("非法请求")



#退出登录
def logout(request):
    response = HttpResponseRedirect("/buyerapp/login/")
    #删除所有请求携带的cookie
    for key in request.COOKIES:
        response.delete_cookie(key)
    #删除session
    del request.session["username"]
    return response


#商品支付订单
def pay_order(request):
    money = request.GET.get("money") #获取订单金额
    order_id = request.GET.get("order_id") #获取订单id

    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Rio67fmfG792RGbb9kuQTqRJGKPlflZO8UPSzSsp257+fzxHq7Tlijak38HcjOeq/3uZMzml39c3Lz2y6kDQ9fh7BmAFaUbfymYUnOSVTlKmFuCUey75AZloe+5dl1qNPhW9u9wp9MpPjcggn35ByQ3wwS4zDtIYEKHZ8DIvo1ELRxbTTkydNSq+SRzHqgwPeRiWumOvUHIAvf4Ij6arM/3IZq3/lFuBcWM/SDMUIxrhbsFAxHR8bkA038gcG6Lp2dTZVwlsbLqN80wTqbxqLJuZUUPALhEETHD7mOQBkqs8nUx/OZPC0iHoQWq82Bkj43j/pZQCZwxiky7zrcAlQIDAQAB
    -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEA0Rio67fmfG792RGbb9kuQTqRJGKPlflZO8UPSzSsp257+fzxHq7Tlijak38HcjOeq/3uZMzml39c3Lz2y6kDQ9fh7BmAFaUbfymYUnOSVTlKmFuCUey75AZloe+5dl1qNPhW9u9wp9MpPjcggn35ByQ3wwS4zDtIYEKHZ8DIvo1ELRxbTTkydNSq+SRzHqgwPeRiWumOvUHIAvf4Ij6arM/3IZq3/lFuBcWM/SDMUIxrhbsFAxHR8bkA038gcG6Lp2dTZVwlsbLqN80wTqbxqLJuZUUPALhEETHD7mOQBkqs8nUx/OZPC0iHoQWq82Bkj43j/pZQCZwxiky7zrcAlQIDAQABAoIBAQDNT/h11FJmNpndbfOBZPCNLhPcdUbmDTv4e2uj/enWUZ88fYjJBwNNu3m8QIwwL82KtkFCCwwVEAM/3/A5VBCXqj/1E6j4F/Ii79XYiBDUy/eaGKijBuALa9iZpIkoV1t0/bBusfedYrNpmrm6SDWhNIfoXxeRulg75LeOQfcbWlRAyZI5PltIPWGqwQKeUDMQUV6g63Ns23Rf7X3uFmNsTR6cjI4FuH1EQQweOWO/oyvRXnaVC7ltmhMMmnCEz//KPx25z9XV84+Jsxup0rkx7fVSv9iruZNv+NO3bOPOSpMD+gsoqh5yyoNOwzBA1oXvlS1B8B7dYgy3ngKTwel1AoGBAP/ckJURsP6ayCzmTjHRnBakaUQtEWwOkejA/OYUtdWxVfE6Cerwdkz207NQ58HESwwtc2OcnCSt6ggiDYuZIzZZoPXc5mT2f1gEJ+8M0NpTclSiivHtGOHWXQO30KcdaxyrfaPafNQUEscCdmxDdPHeZ/g8tCbrxeMNbT1yvD8DAoGBANE1nk3/KCa2ouhs/uojQNJDwuV9JB0IOXPfhnZtlQxO8t1bM+h9lMhyBSWfhLnp+02LV7bmeO3Ya2AFDh9VGy/WGHmjofjEzqOBe+qKgRPLNv5aJdtj/y6B3UsRD6kjgJJCmEHfs2cIBqFlwtV43NExetgEZKZV9i/15fsyEUKHAoGBAIkRey8w1BYBi31qP7e2qB0FJRON5UhzIb2ELbeAns0E/JqHUirXeTjP/ieRDych5mZ2rttNWeTYeoiy3XjMqC2EpJMyLQcnep8HUvFgdz6O96/ZiAAE2ZCayyejwJbWTryELoGqGbdvrYOJkTF8jdjJIf+9XXGAW3nAhqYloi1LAoGAaCMWb6Co7cxPfv5yTT3LEF7mbrFB/qmPX5xOJDkbzgqmXYT+a6XHH5eR9E5ZFOnhS5Im0UYbv9jQafVaOEJ2y/L4L+RBxcDBUyYq9m6HHcEz2Jwq5+/4n7/I1YrijsC7SRKZE4E0nf6ivkgXGYeV8xN8IHbfWuTDLNBr8APWD5UCgYBEeIGIYpo6Kk0DpanYFPXdlE8KBj360ONpJVSQpMLvBIRQ5BnSCIhjYkhWF1ioBGSPbbu4d2wByvGy6U+xm9jSQTlZ3lEE5makYBoitFYE4DEmi9XfnhyjP9n77umT1u8RKhxvuEA+8FhWjArKfITOYZP2DKqzr7ZOz6HLMJOyoA==
    -----END RSA PRIVATE KEY-----"""

    # 实例化支付应用
    alipay = AliPay(
        appid="2016101000652514",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    # 发起支付请求
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id, #订单号
        total_amount=str(money), #支付金额
        subject="水果交易", #交易主题
        return_url="http://127.0.0.1:8000/buyerapp/pay_result/",#支付完成要跳转的本地路由
        notify_url="http://127.0.0.1:8000/buyerapp/pay_result/" #支付完成要跳转的本地异步路由
    )
    #支付完成后，订单状态变为 2
    order = Order.objects.get(order_id = order_id)
    order.order_status = 2
    order.save()

    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string) #跳转支付路由

#商品支付结果
def pay_result(request):
    """
    支付宝支付成功自动用get请求返回的参数

    http://127.0.0.1:8000/buyerapp/pay_result/?
    charset=utf-8&out_trade_no=fruit03&method=alipay.trade.page.pay.return&total_amount=20000.00&sign=kDmz9Q3OeqoN9ilBAexGYO0Qox3DYZV87BHnhDIVVoZcAn%2F9pCZrYE0dhFrXQLMxQbqiN1vgkIaeaSY%2Fyp%2Bk8BHhpJ7m1qmPiPOXSUvnhb6NSqhDLFLzrEBlCRfdQz3lfxXMWp%2B%2FVvUARYwgppc74z%2FLT0jz9poE%2FEqPnIBOvSVhr7vsmiQnu9Awo2FNDIbJuPBcvQmkK%2FbdthVuGhcf1JqHUlcg6tahQDGqPxYmtJY8HPoG%2FwIRpM2Npq4hB9c1Vx5D4aEi2GqBFXyBx216Zt%2B%2FFHbG%2BR%2Bq1CWe0avln%2BV5yvp4mquOHKqasnAMXTrSqdk7qrI4rVsVQK072PI95A%3D%3D&trade_no=2019072622001415611000033436&auth_app_id=2016101000652514&version=1.0&app_id=2016101000652514&sign_type=RSA2&seller_id=2088102178922822&timestamp=2019-07-26+19%3A17%3A04

    拆解开来看：

    #编码方式
    charset=utf-8

    #订单号
    out_trade_no=fruit03

    #订单类型
    method=alipay.trade.page.pay.return

    #订单金额
    total_amount=20000.00

    #校验值
    sign=kDmz9Q3OeqoN9ilBAexGYO0Qox3DYZV87BHnhDIVVoZcAn%2F9pCZrYE0dhFrXQLMxQbqiN1vgkIaeaSY%2Fyp%2Bk8BHhpJ7m1qmPiPOXSUvnhb6NSqhDLFLzrEBlCRfdQz3lfxXMW
    p%2B%2FVvUARYwgppc74z%2FLT0jz9poE%2FEqPnIBOvSVhr7vsmiQnu9Awo2FNDIbJuPBcvQmkK%2FbdthVuGhcf1JqHUlcg6tahQDGqPxYmtJY8HPoG%2FwIRpM2Npq4hB9c1Vx5D4aEi2
    GqBFXyBx216Zt%2B%2FFHbG%2BR%2Bq1CWe0avln%2BV5yvp4mquOHKqasnAMXTrSqdk7qrI4rVsVQK072PI95A%3D%3D

    #订单号
    trade_no=2019072622001415611000033436

    #用户的应用Id
    auth_app_id=2016101000652514

    #版本
    version=1.0

    #商家的应用id
    app_id=2016101000652514

    #加密方式
    sign_type=RSA2

    #商家id
    seller_id=2088102178922822

    #时间
    timestamp=2019-07-26+19%3A17%3A04

    """
    return render(request,"buyerapp/pay_result.html",locals())


#购物车和提交订单base页
def base_1(request):
    return render(request,"buyerapp/base-1.html")






