# Generated by Django 2.1.8 on 2019-08-01 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BuyerApp', '0007_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='goods_store',
            field=models.IntegerField(verbose_name='商品商店id'),
        ),
    ]
