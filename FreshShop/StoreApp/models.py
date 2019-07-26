from django.db import models

#卖家类
class Seller(models.Model):
    username = models.CharField(max_length=32,verbose_name="用户名")
    password = models.CharField(max_length=32,verbose_name="密码")
    nickname = models.CharField(max_length=32, verbose_name="昵称",null=True,blank=True)
    phone = models.CharField(max_length=32, verbose_name="电话",null=True,blank=True)
    email = models.EmailField(verbose_name="邮箱",null=True,blank=True)
    picture = models.ImageField(upload_to="store/images",verbose_name="用户头像",null=True,blank=True)
    address = models.CharField(max_length=32,verbose_name="地址",null=True,blank=True)
    card_id = models.CharField(max_length=32,verbose_name="身份证",null=True,blank=True)

#店铺类型类
class StoreType(models.Model):
    store_type = models.CharField(max_length=32,verbose_name="店铺类型名称")
    type_descripton = models.TextField(verbose_name="类型描述")

#店铺类
class Store(models.Model):
    store_name = models.CharField(max_length=32,verbose_name="店铺名称")
    store_address = models.CharField(max_length=32,verbose_name="店铺地址")
    store_descripton = models.TextField(verbose_name="店铺描述")
    store_logo = models.ImageField(upload_to="store/images",verbose_name="店铺logo")
    store_phone = models.CharField(max_length=32,verbose_name="店铺电话")
    store_money = models.FloatField(verbose_name="店铺注册资金")

    user_id = models.IntegerField(verbose_name="店铺主人") #卖家id （店铺和卖家是一对一）

    type = models.ManyToManyField(to=StoreType,verbose_name="店铺和类型多对多")


#商品类型类
class GoodsType(models.Model):
    name = models.CharField(max_length=32,verbose_name="商品类型名称")
    descripton = models.TextField(max_length=32,verbose_name="商品类型描述")
    picture = models.ImageField(upload_to="buyerapp/images")


#商品类
class Goods(models.Model):
    goods_name = models.CharField(max_length=32,verbose_name="商品名称")
    goods_price = models.FloatField(verbose_name="商品价格")
    goods_image = models.ImageField(upload_to="store/images",verbose_name="商品图片")
    goods_number = models.IntegerField(verbose_name="商品数量库存")
    goods_description = models.TextField(verbose_name="商品描述")
    goods_date = models.DateField(verbose_name="出厂日期",blank=True,null=True)
    goods_safeDate = models.IntegerField(verbose_name="保质期")
    store_id = models.ManyToManyField(to=Store,verbose_name="商品 店铺 多对多") #多对多

    goods_under = models.IntegerField(verbose_name="商品状态",default=1) #0 下架 ， 1待售

    goods_type = models.ForeignKey(to=GoodsType,on_delete=models.CASCADE, verbose_name="商品类型")
    #商品类型和商品是一对多关系，多表中设置外键。


#商品图片
class GoodsImg(models.Model):
    img_address = models.ImageField(upload_to="store/images",verbose_name="图片地址")
    img_description = models.TextField(max_length=32,verbose_name="图片描述")
    goods_id = models.ForeignKey(to=Goods,on_delete=models.CASCADE,verbose_name="商品id") #商品和商品图片是一对多




# Create your models here.
