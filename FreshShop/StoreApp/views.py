import hashlib

from django.shortcuts import render
from django.core.paginator import Paginator  #导入分页模块
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse

from StoreApp.models import *
from BuyerApp.models import *

#校验登录页面传过来的的cookie和session是否相符，相符的话登录首页
def loginValid(fun):

    #判断用户是否用cookie登录，这段代码就是为了判断登录后是谁登录的！！
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            user = Seller.objects.filter(username = c_user).first()
            if user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/storeapp/login/")
    return inner

#密码加密
def set_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

#注册
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = set_password(password)
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect("/storeapp/login/")
    return render(request,"storeapp/register.html")

#登录
def login(request):
    response = render(request,"storeapp/login.html")
    response.set_cookie("login_form","login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password :
            user = Seller.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                cookies = request.COOKIES.get("login_form")
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/storeapp/index/")
                    response.set_cookie("username",username)
                    response.set_cookie("user_id", user.id)
                    request.session["username"] = username
                    #检验用户是否有店铺（查找数据库）
                    store = Store.objects.filter(user_id=user.id).first()
                    if store:
                        response.set_cookie("has_store",store.id)
                    else:
                        response.set_cookie("has_store","")
                    return response
    return response

@loginValid
def index(request):
    # user_id = request.COOKIES.get("user_id")
    return render(request,"storeapp/index.html") #法一
    # cookie_user = request.COOKIES.get("username") #法二
    # return render(request,"storeapp/index.html",)


#添加店铺
@loginValid
def register_store(request):
    type_list = StoreType.objects.all()
    if request.method=="POST":
        post_data = request.POST
        # print(post_data)
        # print(request.FILES)
        store_name = post_data.get("store_name")
        store_address = post_data.get("store_address")
        store_descripton = post_data.get("store_descripton")
        store_logo = request.FILES.get("store_logo")
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")
        type_lists = post_data.getlist("type")
        user_id = int(request.COOKIES.get("user_id"))

        #保存 非多对多 数据
        store = Store()
        store.store_name = store_name
        store.store_descripton = store_descripton
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_address = store_address
        store.user_id = user_id
        store.store_logo = store_logo
        store.save()
        #在生成的数据中添加 多对多 字段
        for i in type_lists:
            store_type = StoreType.objects.get(id = i)
            store.type.add(store_type)
            # print(store_type)
        store.save()
        response = HttpResponseRedirect("/storeapp/index/")
        response.set_cookie("has_store",store.id)
        return response
    return render(request,"storeapp/register_store.html",locals())

#添加商品
@loginValid
def add_goods(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_image = request.FILES.get("goods_image") #获取图片
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_store = request.POST.get("goods_store")
        goods_type = request.POST.get("goods_type")

        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image

        goods.goods_type = GoodsType.objects.get(id = int(goods_type))

        goods.store_id = Store.objects.get(id = int(goods_store)) #修改了

        goods.save()
        return HttpResponseRedirect("/storeapp/list_goods/up/")

    return render(request,"storeapp/add_goods.html",locals())

@loginValid
#商品列表页
def list_goods(request,state):
    #如果商品状态为上架
    if state == "up":
        state_num = 1
    #如果商品状态为下架
    else:
        state_num = 0
    keywords = request.GET.get("keywords","") #查找关键字
    page_num = request.GET.get("page",1) #页码

    #查询店铺
    store_id = request.COOKIES.get("has_store")
    store = Store.objects.get(id =int(store_id))

    if keywords: #如果关键字存在
        goods_list = store.goods_set.filter(goods_name__contains=keywords,goods_under=state_num) #完成模糊查询,商品列表页只显示商品状态为1的商品
    else: #如果关键字不存在，则查询所有
        goods_list = store.goods_set.filter(goods_under=state_num)

    #分页查询，每页3条数据
    paginator = Paginator(goods_list,3)
    page = paginator.page(int(page_num)) #具体页码的数据
    page_range = paginator.page_range #总数据条数 除以 3 得到一个page_range列表
    #返回分页数据
    return render(request,"storeapp/list_goods.html",{"page":page,"page_range":page_range,"keywords":keywords,"state":state})

#商品类型列表页
@loginValid
def goods_type_list(request):
    list_goods_type = GoodsType.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        picture = request.FILES.get("picture") #获取图片文件要用FILES获取，不能通过POST。

        goods_type = GoodsType()
        goods_type.name = name
        goods_type.descripton = description
        goods_type.picture = picture
        goods_type.save()
    return render(request,"storeapp/goods_type_list.html",locals())

#删除商品类型
@loginValid
def delete_goods_type(request):
    id = int(request.GET.get("id"))
    goods_type = GoodsType.objects.get(id = id)
    goods_type.delete()
    return HttpResponseRedirect("/storeapp/goods_type_list/")

@loginValid
#商品详情页
def goods(request,goods_id):
    goods_data = Goods.objects.filter(id = goods_id).first() #如果获取不到id, first()方法不会报错！
    return render(request,"storeapp/goods.html",locals())

@loginValid
#修改商品页
def update_goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_image = request.FILES.get("goods_image")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")

        # 开始修改数据
        goods = Goods.objects.get(id=int(goods_id))
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image:
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect("/storeapp/goods/%s"%goods_id)

    return render(request,"storeapp/update_goods.html",locals())

#获取商品状态
def set_goods(request,state):
    if state == "up": #如果商品状态为上架
        state_num = 1
    else:
        state_num = 0

    id = request.GET.get("id")
    referer = request.META.get("HTTP_REFERER")
    if id :
        goods = Goods.objects.filter(id = id ).first()
        if state == "delete": #如果商品状态为销毁
            goods.delete()
        else: #如果商品状态为下架或上架
            goods.goods_under = state_num #修改状态
            goods.save()
    return HttpResponseRedirect(referer)

#后台订单列表页（待处理订单）
@loginValid
def order_list(request):
    #要知道是哪家店铺的订单列表，所以需要从订单详情页中去取
    store_id = request.COOKIES.get("has_store")
    order_list = OrderDetail.objects.filter(order_id__order_status=2,goods_store=store_id) #订单详情
    return render(request,"storeapp/order_list.html",locals())

#拒绝发货（改变订单状态）
def delete_order(request):
    order_id = request.GET.get("order_id") #获取订单页订单编号
    if order_id:
        order = Order.objects.get(order_id=order_id)
        order.order_status = 0
        order.save()
        store_id = request.COOKIES.get("has_store")
        order_list = OrderDetail.objects.filter(order_id__order_status=2, goods_store=store_id)  # 订单详情
        return render(request,"storeapp/order_list.html",locals())
    return HttpResponseRedirect("/storeapp/order_list/")

#确认发货（改变订单状态）
def affirm_order(request):
    order_id = request.GET.get("order_id")  # 获取订单页订单编号
    if order_id:
        order = Order.objects.get(order_id=order_id)
        order.order_status = 3
        order.save()
        store_id = request.COOKIES.get("has_store")
        order_list = OrderDetail.objects.filter(order_id__order_status=2, goods_store=store_id)  # 订单详情
        return render(request, "storeapp/order_list.html", locals())
    return HttpResponseRedirect("/storeapp/order_list/")

#后台已完成订单列表页
def completed_order(request):
    store_id = request.COOKIES.get("has_store")
    order_list = OrderDetail.objects.filter(goods_store=store_id).exclude(order_id__order_status=2,goods_store=store_id)  # 订单详情
    return render(request, "storeapp/completed_order.html", locals())


def base(request):
    return render(request,"storeapp/base.html")

#退出登录
def logout(request):
    response = HttpResponseRedirect("/storeapp/login/")
    for key in request.COOKIES: #获取当前所有的cookie，从服务器下发删除命令，删除本地浏览器的cookie
        response.delete_cookie(key)
    return response


# Create your views here.
from StoreApp.serializers import *
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend #导入过滤器

class UserViewSet(viewsets.ModelViewSet):
    """
    查询所有的商品，并实现了分页
    """
    queryset = Goods.objects.all()  #具体返回的数据
    serializer_class = UserSerializer  #指定过滤的类

    filter_backends = [DjangoFilterBackend] #采用哪个过滤器
    filterset_fields = ["goods_name","goods_price"] #进行查询的字段

class TypeViewSet(viewsets.ModelViewSet):
    """
       返回具体查询的内容
    """
    queryset = GoodsType.objects.all()
    serializer_class = GoodsTypeSerializer


def ajax_goods_list(request):
    return render(request,"storeapp/ajax_list_goods.html")


from django.core.mail import send_mail
def sendMail(request):
    send_mail("邮件主题","邮件内容","from_email",["to_email"],fail_silently=False)

from CeleryTask.tasks import add
from django.http import JsonResponse

def get_add(request):
    add.delay(2,3)
    return JsonResponse({"status":200})


# def smail_White_views(request):
#     # print("我是小白视图")
#     # raise TypeError("就要犯错")
#     # return  HttpResponse("小白视图")
#
#     def hello():
#         return HttpResponse("hello world")
#     rep = HttpResponse("I am rep")
#     rep.render = hello
#     return rep


from django.views.decorators.cache import cache_page

# @cache_page(60*15) #对当前视图进行缓存，缓存寿命是15分钟
# def smail_White_views(request):
#     rep = HttpResponse("I am rep")
#     # rep.render = lambda: HttpResponse("hello world")
#     return rep


#路由粒度缓存
# def smail_White_views(request):
#     rep = HttpResponse("I am rep")
#     return rep

#底层接口缓存
from django.core.cache import cache
def smail_White_views(request):
    store_data = cache.get('store_data') #如果没有，返回None
    if store_data:
        store_data = store_data
    else:
        data = Store.objects.all()
        cache.set("store_data",data,30) #设置缓存，可以修改已经存在的缓存
        # cache.add("store_data",data,30) #add只会添加一个缓存，不会修改已经存在的缓存
        store_data = data
    return render(request,"storeapp/index.html",locals())


