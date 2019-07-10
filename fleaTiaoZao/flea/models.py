from django.utils import timezone
from django.db import models

# Create your models here.


class User(models.Model):
    """用户信息表"""
    # uid = models.AutoField(primary_key=True)
    openid = models.CharField(max_length=100)
    student_id = models.CharField(max_length=16, null=True)
    name = models.TextField(max_length=20, null=True)
    contact = models.TextField(max_length=100, null=True)
    is_bind = models.BooleanField(default=False)
    createTime = models.DateField()
    last_login = models.DateTimeField(default=timezone.now)


class Goods(models.Model):
    """商品信息表"""
    # gid = models.AutoField(primary_key=True)
    title = models.TextField(max_length=50)
    content = models.TextField(max_length=200)
    price = models.FloatField()
    image = models.CharField(max_length=255, null=True)
    publisher = models.ForeignKey("User", related_name='good_publisher', db_column='publisher', on_delete=models.CASCADE, to_field='id')
    buy_user = models.ForeignKey("User", related_name='good_buy_user', db_column='buy_user', on_delete=models.CASCADE, to_field='id', null=True)
    finished_time = models.DateField(null=True)
    createTime = models.DateField()
    status = models.IntegerField()


class Collection(models.Model):
    """收藏/我要买/交易记录信息表"""
    """
    type 说明
    -1: 未收藏未购买 0：已收藏未购买 1： 未收藏已购买 2： 已收藏已购买 
    3： 商品状态0-1非交易者记录
    4： 商品状态0-1交易者记录
    5： 商品状态1-2记录
    6： 商品状态1-0记录
    
    """
    # cid = models.AutoField(primary_key=True)
    goods = models.ForeignKey("Goods", db_column='goods', related_name="user_collection", to_field='id', on_delete=models.CASCADE)
    user = models.ForeignKey("User", db_column='user', to_field='id', on_delete=models.CASCADE)
    type = models.IntegerField()  # -1: 未收藏未购买 0：已收藏未购买 1： 未收藏已购买 2： 已收藏已购买
    createTime = models.DateField()


