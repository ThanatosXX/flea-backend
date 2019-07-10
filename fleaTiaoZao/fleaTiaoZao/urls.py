"""fleaTiaoZao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path
from flea import views

urlpatterns = [
    path('flea/admin/', admin.site.urls),
    re_path(r'^flea/no_login/$', views.no_login, name='no_login'),
    re_path(r'^flea/get_openid/$', views.get_openid),
    re_path(r'^flea/submit_bind/$', views.submit_bind),
    re_path(r'^flea/get_bind_user_info/$', views.get_bind_user_info),
    re_path(r'^flea/get_goods_list/$', views.get_goods_list),
    re_path(r'^flea/get_goods_detail/$', views.get_goods_detail),
    re_path(r'^flea/submit_collection/$', views.submit_collection),
    re_path(r'^flea/submit_want_buy/$', views.submit_want_buy),
    re_path(r'^flea/submit_exchange/$', views.submit_exchange),
    re_path(r'^flea/submit_finish/$', views.submit_finish),
    re_path(r'^flea/submit_goods/$', views.submit_goods),
    re_path(r'^flea/submit_delete_goods/$', views.submit_delete_goods),
    re_path(r'^flea/get_publish_goods/$', views.get_publish_goods),
    re_path(r'^flea/get_exchange_goods/$', views.get_exchange_goods),
    re_path(r'^flea/get_publish_goods_detail/$', views.get_publish_goods_detail),
    re_path(r'^flea/get_exchange_goods_detail/$', views.get_exchange_goods_detail),
    re_path(r'^flea/get_collect_goods/$', views.get_collect_goods),
    re_path(r'^flea/get_sell_goods/$', views.get_sell_goods),
    re_path(r'^flea/get_buy_goods/$', views.get_buy_goods),
    re_path(r'^flea/get_delete_goods/$', views.get_delete_goods),
    re_path(r'^flea/get_edit_goods/$', views.get_edit_goods),
    re_path(r'^flea/submit_edit_goods/$', views.submit_edit_goods),
    re_path(r'^flea/get_order/$', views.get_order)
]
