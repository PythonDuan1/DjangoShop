import hashlib

from django.shortcuts import render
from django.core.paginator import Paginator  #导入分页模块
from django.shortcuts import HttpResponseRedirect

from StoreApp.models import *

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
                    reponse = HttpResponseRedirect("/storeapp/index/")
                    reponse.set_cookie("username",username)
                    reponse.set_cookie("user_id", user.id)
                    request.session["username"] = username
                    return reponse
    return response

#校验登录页面传过来的的cookie和session是否相符，相符的话登录首页
def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            user = Seller.objects.filter(username = c_user).first()
            if user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/storeapp/login/")
    return inner

@loginValid
def index(request):
    user_id = request.COOKIES.get("user_id")
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    store = Store.objects.filter(user_id= user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0
    return render(request,"storeapp/index.html",{"is_store":is_store}) #法一
    # cookie_user = request.COOKIES.get("username") #法二
    # return render(request,"storeapp/index.html",)


#添加店铺
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
            print(store_type)

        store.save()

    return render(request,"storeapp/register_store.html",locals())

#添加商品
def add_goods(request):
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_image = request.FILES.get("goods_image")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_store = request.POST.get("goods_store")

        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.save()

        goods.store_id.add(
            Store.objects.get(id = int(goods_store))
        )
        goods.save()
        return HttpResponseRedirect("/storeapp/list_goods/")

    return render(request,"storeapp/add_goods.html")

#商品列表页
def list_goods(request):

    keywords = request.GET.get("keywords","") #查找关键字
    page_num = request.GET.get("page",1) #页码
    if keywords: #如果关键字存在
        goods_list = Goods.objects.filter(goods_name__contains=keywords) #完成模糊查询
    else: #如果关键字不存在，则查询所有
        goods_list = Goods.objects.all()

    #分页查询，每页3条数据
    paginator = Paginator(goods_list,3)
    page = paginator.page(int(page_num)) #具体页码的数据
    page_range = paginator.page_range #总数据条数 除以 3 得到一个page_range列表
    #返回分页数据
    return render(request,"storeapp/list_goods.html",{"page":page,"page_range":page_range,"keywords":keywords})

def base(request):
    return render(request,"storeapp/base.html")


# Create your views here.
