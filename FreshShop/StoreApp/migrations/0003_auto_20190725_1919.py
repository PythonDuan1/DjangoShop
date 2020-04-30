# Generated by Django 2.1.8 on 2019-07-25 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('StoreApp', '0002_auto_20190725_0920'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='商品类型名称')),
                ('descripton', models.TextField(max_length=32, verbose_name='商品类型描述')),
                ('picture', models.ImageField(upload_to='buyerapp/images')),
            ],
        ),
        migrations.AddField(
            model_name='goods',
            name='goods_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='StoreApp.GoodsType', verbose_name='商品类型'),
            preserve_default=False,
        ),
    ]