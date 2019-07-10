from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, SESSION_KEY
from django.http import HttpResponse
from .config import APPID, SECRET
from django.utils import timezone
from django.db.models import Q
from .models import *
import requests
import decimal
import json

# Create your views here.


# 用户登陆获取openid
def get_openid(request):
    if request.method == "GET":
        try:
            code = request.GET.get('code')
            parmas = {
                'appid': APPID,
                'secret': SECRET,
                'jscode': code,
                'grant_type': 'authorization_code'
            }
            url = "https://api.weixin.qq.com/sns/jscode2session" + "?appid=" + str(parmas['appid'])+"&secret="+str(parmas['secret'])+"&js_code=" + str(parmas['jscode'])+"&grant_type=authorization_code"
            r = requests.get(url)
            openid = r.json().get('openid')
            if openid:
                try:
                    user = User.objects.get(openid=openid)
                    user.last_login = timezone.now()
                    user.save()
                    login(request, user)
                    return HttpResponse(json.dumps({'status': True, 'msg': '老用户登录成功'}))
                except ObjectDoesNotExist:
                    user = {
                        'openid': openid,
                        'is_bind': False,
                        'createTime': timezone.now(),
                        'last_login': timezone.now(),
                    }
                    login_user = User.objects.create(**user)
                    login(request, login_user)
                    return HttpResponse(json.dumps({'status': True, 'msg': '第一次登录成功'}))
            else:
                return HttpResponse(json.dumps({'status': False, 'msg': '获取openid失败'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '获取openid超时'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 未登录跳转
def no_login(request):
    return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))


# 身份绑定认证
# @login_required(redirect_field_name='no_login')
def submit_bind(request):
    if request.method == "POST":
        try:
            try:
                user_id = request.session[SESSION_KEY]
            except KeyError:
                return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
            student_id = request.POST.get('student_id')
            password = request.POST.get('password')
            name = request.POST.get('name')
            contact = request.POST.get('contact')
            url = 'http://my.csu.edu.cn/cgi-bin/login?method=login&userId=' + \
                str(student_id)+'&pwd='+str(password)+'&os=other&browser=chrome'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            r = requests.post(url, headers=headers)
            r.encoding = r.apparent_encoding
            result = json.loads(r.text)
            if result['errcode'] == '0':
                user = User.objects.get(id=user_id)
                user.student_id = student_id
                user.name = name
                user.contact = contact
                user.is_bind = 1
                user.save()
                return HttpResponse(json.dumps({'status': True, 'msg': '验证成功'}))
            else:
                return HttpResponse(json.dumps({'status': False, 'msg': '密码错误'}))
        except RuntimeWarning:
            return HttpResponse(json.dumps({'status': False, 'msg': '请求绑定超时'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 获取绑定用户的信息
def get_bind_user_info(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'GET':
        user_info = User.objects.get(id=user_id)
        user_info_list = {
            'name': user_info.name,
            'contact': user_info.contact,
            'student_id': user_info.student_id,
        }
        return HttpResponse(json.dumps({'status': True, 'user_info': user_info_list, 'msg': '成功获取'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 首页全部商品
def get_goods_list(request):
    if request.method == 'POST':
        goods_id = int(request.POST.get('goods_page'))
        if goods_id <= 1:
            try:
                goods_list = Goods.objects.filter(Q(status=0)).order_by("-createTime")
                final_goods_list = []
                for goods in goods_list[:6]:
                    goods_info = {
                        'id': goods.id,
                        'title': goods.title,
                        'price': goods.price,
                        'image': goods.image,
                        'content': goods.content
                    }
                    final_goods_list.append(goods_info)
                return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取商品列表'}))
            except ObjectDoesNotExist:
                return HttpResponse(json.dumps({'status': True, 'msg': '暂无商品'}))
        else:
            try:
                goods_list = Goods.objects.filter(Q(status=0)).order_by("-createTime")
                final_goods_list = []
                for goods in goods_list[(goods_id-1)*6:goods_id*6]:
                    goods_info = {
                        'id': goods.id,
                        'title': goods.title,
                        'price': goods.price,
                        'image': goods.image,
                        'content': goods.content
                    }
                    final_goods_list.append(goods_info)
                return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取商品列表'}))
            except ObjectDoesNotExist:
                return HttpResponse(json.dumps({'status': True, 'msg': '该页暂无商品'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 商品详情
def get_goods_detail(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            goods_info_obj = Goods.objects.get(id=goods_id)
            isPublisher = False
            if goods_info_obj.publisher.id == int(user_id):
                isPublisher = True
            goods_info = {
                'id': goods_info_obj.id,
                'title': goods_info_obj.title,
                'price': goods_info_obj.price,
                'image': goods_info_obj.image,
                'content': goods_info_obj.content,
                'publisher': goods_info_obj.publisher.id,
                'createTime': str(goods_info_obj.createTime),
                'type': goods_info_obj.status,
                'isPublisher': isPublisher
            }
            host_info = {
                'id': goods_info_obj.publisher.id,
                'name': goods_info_obj.publisher.name,
                'contact': goods_info_obj.publisher.contact
            }
            try:
                goods_in_collection = Collection.objects.filter(type__lte=2).get(goods=goods_id, user=user_id)
                goods_type = int(goods_in_collection.type)
            except ObjectDoesNotExist:
                goods_type = -1
            return HttpResponse(json.dumps({'status': True,'host_info': host_info, 'goods_type': goods_type, 'goods_info': goods_info, 'msg': '成功获取'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': True, 'msg': '暂无该商品'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 点击收藏按钮
def submit_collection(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            goods_obj = Goods.objects.get(id=goods_id)
            user_obj = User.objects.get(id=user_id)
            collection = {
                'type': 0,
                'goods': goods_obj,
                'user': user_obj,
                'createTime': timezone.now()
            }
            try:
                collection_obj = Collection.objects.filter(type__lte=2).get(goods=goods_id, user=user_id)
                if collection_obj.type == 1:
                    collection_obj.type = 2
                    collection_obj.save()
                    collection['type'] = collection_obj.type
                else:
                    collection['type'] = collection_obj.type
            except ObjectDoesNotExist:
                Collection.objects.create(**collection)
            return HttpResponse(json.dumps({'status': True, 'goods_type': collection['type'], 'msg': '收藏成功'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '信息不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 点击我要买按钮
def submit_want_buy(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            goods_obj = Goods.objects.get(id=goods_id)
            user_obj = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '信息不存在'}))
        collection = {
            'type': 1,
            'goods': goods_obj,
            'user': user_obj,
            'createTime': timezone.now()
        }
        try:
            collection_obj = Collection.objects.filter(type__lte=2).get(goods=goods_id, user=user_id)
            if collection_obj.type == 0:
                collection_obj.type = 2
                collection_obj.save()
                collection['type'] = collection_obj.type
            else:
                collection['type'] = collection_obj.type
        except ObjectDoesNotExist:
            Collection.objects.create(**collection)
        return HttpResponse(json.dumps({'status': True, 'goods_type': collection['type'], 'msg': '购买成功'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 卖家确定开始交易物品
def submit_exchange(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        buy_user_id = request.POST.get('user_id')
        goods_id = request.POST.get('goods_id')
        try:
            goods_obj = Goods.objects.get(id=goods_id)
            buy_user_obj = User.objects.get(id=buy_user_id)
            goods_obj.buy_user = buy_user_obj
            goods_obj.status = 1
            goods_obj.save()
            try:
                collections_obj = Collection.objects.filter(Q(goods=goods_obj) & (Q(type=1) | Q(type=2)))
                seller_obj = User.objects.get(id=user_id)
                record = {
                    'type': 4,
                    'goods': goods_obj,
                    'user': seller_obj,
                    'createTime': timezone.now()
                }
                Collection.objects.create(**record)
                for collection_obj in collections_obj:
                    record = {
                        'type': 3,
                        'goods': goods_obj,
                        'user': collection_obj.user,
                        'createTime': timezone.now()
                    }
                    if int(collection_obj.user.id) == int(buy_user_id):
                        record['type'] = 4
                    try:
                        if_collection_obj = Collection.objects.get(type=3, user=collection_obj.user, goods=goods_obj)
                    except ObjectDoesNotExist:
                        Collection.objects.create(**record)
            except ObjectDoesNotExist:
                return HttpResponse(json.dumps({'status': False, 'msg': '交易失败'}))
            return HttpResponse(json.dumps({'status': True, 'msg': '开始交易'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '该商品不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 确定交易完成
def submit_finish(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            goods = Goods.objects.get(id=goods_id)
            # if int(goods.publisher.id) == int(user_id):
            goods.status = 2
            goods.finished_time = timezone.now()
            goods.save()
            if int(user_id) == goods.publisher.id:
                record = {
                    'type': 5,
                    'goods': goods,
                    'user': goods.buy_user,
                    'createTime': timezone.now()
                }
                Collection.objects.create(**record)
            elif int(user_id) == goods.buy_user.id:
                record = {
                    'type': 5,
                    'goods': goods,
                    'user': goods.publisher,
                    'createTime': timezone.now()
                }
                Collection.objects.create(**record)
            record = {
                'type': 5,
                'goods': goods,
                'user': User.objects.get(id=user_id),
                'createTime': timezone.now()
            }
            Collection.objects.create(**record)
            return HttpResponse(json.dumps({'status': True, 'msg': '交易完成'}))
            # else:
            #    return HttpResponse(json.dumps({'status': False, 'msg': '该用户不是商品所有者'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '该商品不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 发布页面提交
def submit_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        user_obj = User.objects.get(id=user_id)
        goods = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content'),
            'price': float(request.POST.get('price')),
            'image': request.POST.get('image'),
            'createTime': timezone.now(),
            'status': 0,
            'publisher': user_obj,
        }
        Goods.objects.create(**goods)
        return HttpResponse(json.dumps({'status': True, 'msg': '发布成功'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 删除已经发布/取消交易中的物品
def submit_delete_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            good = Goods.objects.get(id=goods_id)
            print(int(good.status))
            if int(good.status) == 0:
                good.status = 3
                good.save()
                return HttpResponse(json.dumps({'status': True, 'msg': '商品删除成功'}))
            elif int(good.status) == 1:
                good.status = 0
                good.save()
                if int(user_id) == int(good.publisher.id):
                    record = {
                        'type': 6,
                        'goods': good,
                        'user': good.buy_user,
                        'createTime': timezone.now()
                    }
                    Collection.objects.create(**record)
                elif int(user_id) == int(good.buy_user.id):
                    record = {
                        'type': 6,
                        'goods': good,
                        'user': good.publisher,
                        'createTime': timezone.now()
                    }
                    Collection.objects.create(**record)
                record = {
                    'type': 6,
                    'goods': good,
                    'user': User.objects.get(id=user_id),
                    'createTime': timezone.now()
                }
                Collection.objects.create(**record)
                return HttpResponse(json.dumps({'status': True, 'msg': '商品取消交易成功'}))
            else:
                return HttpResponse(json.dumps({'status': False, 'msg': '该商品不能进行此操作'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '商品不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 得到发布中的商品
def get_publish_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        try:
            goods_list = Goods.objects.filter(publisher=user_id).filter(status=0).order_by("-createTime")
            final_goods_list = []
            for goods in goods_list:
                ifHaveCustomer = False
                try:
                    goods_id = goods.id
                    collects_obj = Collection.objects.filter(goods=goods_id, type__lte=2)
                    for collect_obj in collects_obj:
                        if collect_obj.type == 1:
                            ifHaveCustomer = True
                        elif collect_obj.type == 2:
                            ifHaveCustomer = True
                        else:
                            ifHaveCustomer = False
                except ObjectDoesNotExist:
                    ifHaveCustomer = False
                goods_info = {
                    'id': goods.id,
                    'title': goods.title,
                    'price': goods.price,
                    'image': goods.image,
                    'content': goods.content,
                    'type': goods.status,
                    'createTime': str(goods.createTime),
                    'ifHaveCustomer': ifHaveCustomer
                }
                final_goods_list.append(goods_info)
            return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取发布商品'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '商品列表不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 发布中的商品的详情
def get_publish_goods_detail(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            goods_info = Goods.objects.get(id=goods_id)
            final_goods_info = {
                'id': goods_info.id,
                'title': goods_info.title,
                'price': goods_info.price,
                'image': goods_info.image,
                'content': goods_info.content,
                'publisher': goods_info.publisher.id,
              	'type': goods_info.status,
                'createTime': str(goods_info.createTime)
            }
            try:
                customer_list = []
                user_in_collections = Collection.objects.filter(goods=goods_id).filter(Q(type=1) | Q(type=2))
                for user_in_collection in user_in_collections:
                    user = User.objects.get(id=int(user_in_collection.user.id))
                    user_info = {
                        'id': user.id,
                        'name': user.name,
                        'contact': user.contact,
                    }
                    customer_list.append(user_info)
            except ObjectDoesNotExist:
                customer_list = 0
            return HttpResponse(json.dumps(
                {'status': True, 'customer_list': customer_list, 'goods_info': final_goods_info, 'msg': '成功获取'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': True, 'msg': '暂无该商品'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 得到交易中的商品
def get_exchange_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        try:
            goods_list = Goods.objects.filter(Q(publisher=user_id) | Q(buy_user=user_id)).filter(status=1).order_by("-createTime")
            final_goods_list = []
            for goods in goods_list:
                goods_info = {
                    'id': goods.id,
                    'title': goods.title,
                    'price': goods.price,
                    'image': goods.image,
                    'content': goods.content
                }
                if int(goods.publisher.id) == int(user_id):
                    goods_info['type'] = 0
                else:
                    goods_info['type'] = 1
                final_goods_list.append(goods_info)
            return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取交易中的商品'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '商品列表不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 交易中的商品的详情
def get_exchange_goods_detail(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            goods_info = Goods.objects.get(id=goods_id)
            final_goods_info = {
                'id': goods_info.id,
                'title': goods_info.title,
                'price': goods_info.price,
                'image': goods_info.image,
                'content': goods_info.content
            }
            if int(goods_info.buy_user.id) == int(user_id):
                contact_id = goods_info.publisher.id
                user = User.objects.get(id=contact_id)
                user_info = {
                    'id': user.id,
                    'name': user.name,
                    'contact': user.contact,
                }
                return HttpResponse(json.dumps({'status': True, 'user_type': 1, 'host': user_info, 'goods_info': final_goods_info, 'msg': '成功获取,此时登陆用户为买家'}))
            elif int(goods_info.publisher.id) == int(user_id):
                contact_id = goods_info.buy_user.id
                user = User.objects.get(id=contact_id)
                user_info = {
                    'id': user.id,
                    'name': user.name,
                    'contact': user.contact,
                }
                return HttpResponse(json.dumps({'status': True, 'user_type': 0, 'customer': user_info, 'goods_info': final_goods_info, 'msg': '成功获取,此时登陆用户为卖家'}))
            else:
                return HttpResponse(json.dumps({'status': False, 'msg': '登录用户没有权限访问'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': True, 'msg': '暂无该商品'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 得到已收藏的商品
def get_collect_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        try:
            collect_list = Collection.objects.filter(user=user_id).filter(Q(type=0) | Q(type=2)).order_by("-createTime")
            goods_list = []
            for collect in collect_list:
                goods_list.append(collect.goods)
            final_goods_list = []
            for goods in goods_list:
                goods_info = {
                    'id': goods.id,
                    'title': goods.title,
                    'price': goods.price,
                    'image': goods.image,
                    'content': goods.content
                }
                final_goods_list.append(goods_info)
            return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取收藏的商品'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '商品列表不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))



# 得到已卖出的商品
def get_sell_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        try:
            goods_list = Goods.objects.filter(publisher=user_id).filter(status=2).order_by("-createTime")
            final_goods_list = []
            for goods in goods_list:
                goods_info = {
                    'id': goods.id,
                    'title': goods.title,
                    'price': goods.price,
                    'image': goods.image,
                    'content': goods.content,
                  	'createTime': str(goods.createTime),
                  	'finished_time': str(goods.finished_time)
                }
                final_goods_list.append(goods_info)
            return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取卖出的商品'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '商品列表不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 得到已买入的商品
def get_buy_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        try:
            goods_list = Goods.objects.filter(buy_user=user_id).filter(status=2).order_by("-createTime")
            final_goods_list = []
            for goods in goods_list:
                goods_info = {
                    'id': goods.id,
                    'title': goods.title,
                    'price': goods.price,
                    'image': goods.image,
                    'content': goods.content,
                  	'finished_time': str(goods.finished_time)
                }
                final_goods_list.append(goods_info)
            return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取买入的商品'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '商品列表不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 得到已删除的商品
def get_delete_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        try:
            goods_list = Goods.objects.filter(publisher=user_id).filter(status=3)
            final_goods_list = []
            for goods in goods_list:
                goods_info = {
                    'id': goods.id,
                    'title': goods.title,
                    'price': goods.price,
                    'image': goods.image,
                    'content': goods.content
                }
                final_goods_list.append(goods_info)
            return HttpResponse(json.dumps({'status': True, 'goods_list': final_goods_list, 'msg': '成功获取删除的商品'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '商品列表不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 修改页面的信息
def get_edit_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            good_info = Goods.objects.get(id=goods_id)
            final_goods_info = {
                'id': good_info.id,
                'title': good_info.title,
                'price': good_info.price,
                'image': good_info.image,
                'content': good_info.content
            }
            return HttpResponse(json.dumps(
                {'status': True, 'goods_info': final_goods_info,
                 'msg': '成功获得信息'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '该商品不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 修改页面提交信息
def submit_edit_goods(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            goods_info = Goods.objects.get(id=goods_id)
            if int(goods_info.publisher.id) == int(user_id):
                if goods_info.status == 1:
                    return HttpResponse(json.dumps({'status': False, 'msg': '此商品正在交易中，不能修改'}))
                elif goods_info.status == 2:
                    return HttpResponse(json.dumps({'status': False, 'msg': '该商品交易已完成，不能修改'}))
                elif goods_info.status == 3:
                    return HttpResponse(json.dumps({'status': False, 'msg': '该商品交易已删除，不能修改'}))
                else:
                    goods_info.title = request.POST.get('title')
                    goods_info.content = request.POST.get('content')
                    goods_info.price = float(request.POST.get('price'))
                    goods_info.image = request.POST.get('image')
                    goods_info.save()
                return HttpResponse(json.dumps(
                    {'status': True, 'msg': '成功修改信息'}))
            else:
                return HttpResponse(json.dumps({'status': False, 'msg': '该用户没有权限修改'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '该商品不存在'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))


# 获得商品记录
def get_order(request):
    try:
        user_id = request.session[SESSION_KEY]
    except KeyError:
        return HttpResponse(json.dumps({'status': False, 'msg': '用户未登陆'}))
    if request.method == 'POST':
        try:
            good_list = Collection.objects.filter(user=user_id, type__gte=3).order_by("-id")
            msg_list = []
            for item in good_list:
                item_name = item.goods.title
                if int(item.type) == 3:
                    ms = '商品{} 已经被其他人购买'.format(item_name)
                elif int(item.type) == 4:
                    ms = '商品{} 开始交易'.format(item_name)
                elif int(item.type) == 5:
                    ms = '商品{} 交易完成'.format(item_name)
                elif int(item.type) == 6:
                    ms = '商品{} 交易取消'.format(item_name)
                else:
                    ms = '商品{} 状态未知'.format(item_name)
                    pass
                info = {
                    'msg': ms,
                    'time': str(item.createTime)
                }
                msg_list.append(info)
            return HttpResponse(json.dumps({'status': True, 'msg_list': msg_list, 'msg': '获取交易记录成功'}))
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'msg': '获取交易记录失败'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'msg': '访问方式错误'}))