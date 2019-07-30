from django.db import models

class Buyer(models.Model):
    username = models.CharField(max_length=32,verbose_name="用户名")
    password = models.CharField(max_length=32,verbose_name="密码")
    email = models.EmailField(verbose_name="用户邮箱")
    phone = models.CharField(max_length=32,verbose_name="联系电话",blank=True,null=True)
    connect_address = models.TextField(verbose_name="联系地址",blank=True,null=True)

class Address(models.Model):
    address = models.TextField(verbose_name="收获地址")
    recver = models.CharField(max_length=32,verbose_name="接收人")
    recv_phone = models.CharField(max_length=32,verbose_name="收件人电话")
    post_number = models.CharField(max_length=32,verbose_name="邮编")
    buy_id = models.ForeignKey(to=Buyer,on_delete=models.CASCADE,verbose_name="用户id")


class Order(models.Model):
    """
    订单表

    订单状态：
    未支付：1
    待发货：2
    已发货：3
    已收货：4
    已退货：0
    """
    order_id = models.CharField(max_length=32,verbose_name="id订单编号")
    goods_count = models.IntegerField(verbose_name="商品数量")
    order_user = models.ForeignKey(to= Buyer,on_delete=models.CASCADE,verbose_name="订单用户") #用户和订单是一对多关系，多表中设置外键
    order_address = models.ForeignKey(to = Address,on_delete=models.CASCADE,verbose_name="订单地址",null=True,blank=True) #地址和订单是一对多
    order_price = models.FloatField(verbose_name="订单总价")

    order_status = models.IntegerField(default=1,verbose_name="订单状态") #新增字段

class OrderDetail(models.Model):
    """
    订单详情表
    """
    #订单和订单详情是一对多关系，多表中设置外键关联，订单详情表的order_id关联订单表的主键id
    order_id = models.ForeignKey(to=Order,on_delete=models.CASCADE,verbose_name="订单编号（多对一)") #外键

    goods_id = models.IntegerField(verbose_name="商品id")
    goods_name = models.CharField(max_length=32,verbose_name="商品名称")
    goods_price = models.FloatField(verbose_name="商品价格")
    goods_number = models.IntegerField(verbose_name="商品购买数量")
    goods_total = models.FloatField(verbose_name="单个商品总价")
    goods_store = models.IntegerField(verbose_name="商店id")

    goods_image = models.ImageField(verbose_name="商品图片")

#购物车
class Cart(models.Model):
    goods_name = models.CharField(max_length=32,verbose_name="商品名称")
    goods_price = models.FloatField(verbose_name="商品价格") #单价
    goods_total = models.FloatField(verbose_name="商品总价")
    goods_number = models.IntegerField(verbose_name="商品数量")
    goods_picture = models.ImageField(upload_to="buyerapp/images",verbose_name="商品图片")
    goods_id = models.IntegerField(verbose_name="商品id")
    goods_store = models.IntegerField(verbose_name="商品商店id")
    user_id = models.IntegerField(verbose_name="用户id")

# Create your models here.
