from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json
from .models import UserProfile,Userpassword
from dadashop.utils import md5
from dadashop.utils import jwt_encode, jwt_decode,verify
from django.core.mail import send_mail
from django.template.loader import render_to_string
import random
import base64
from django_redis import get_redis_connection
from django.conf import settings
# 通过第三方的运营平台发送手机短信
from ronglian_sms_sdk import SmsSDK
from .models import Address
from django.views import View
from django.db.models import F
from dadashop.decorators import require_login
import datetime
import requests


# Convert a function decorator into a method decorator
from django.utils.decorators import method_decorator

# Create your views here.
def register(request):
    # 1.获取数据
    data = json.loads(request.body)
    uname = data.get('uname')
    password = data.get('password')
    phone = data.get('phone')
    email = data.get('email')
    verify = data.get('verify')
    # 2.校验数据
    if len(uname) == 0:
        context = {
            'code': 10001,
            'error': '用户名没有填写'
        }
        return JsonResponse(context)
    if len(uname) < 6:
        context = {
            'code': 10002,
            'error': '用户名长度少于6位'
        }
        return JsonResponse(context)
    if len(uname) > 11:
        context = {
            'code': 10003,
            'error': '用户名长度超过11位'
        }
        return JsonResponse(context)
    ###########################################
    redis_sms_conn = get_redis_connection('sms')
    if not redis_sms_conn.exists('register_sms_' + phone):
        context = {
            'code': 10019,
            'error': '验证码逾期'
        }
        return JsonResponse(context)

    sms_value = redis_sms_conn.get('register_sms_' + phone).decode('utf-8')

    if verify != sms_value:
        context = {
            'code': 10018,
            'error': '验证码错误'
        }
        return JsonResponse(context)

    ###########################################
    if UserProfile.objects.filter(username=uname):
        context = {
            'code': 10005,
            'error': '用户名已经被占用'
        }
        return JsonResponse(context)
    # 3.将获取的到数据写入到`UserProfile`模型中
    user = UserProfile.objects.create(
        username=uname,
        password=md5(password),
        phone=phone,
        email=email
    )
    userpassword=Userpassword.objects.create(
        expire_at=datetime.datetime.now(),
        password=md5(password),
        user=user
    )
    # 4.发送激活邮件
    # 4.1获取1000~9999之间的随机数
    rand = random.randint(1000, 9999)
    # 4.2 组织动态数据(将传递到激活邮件的正文中)
    ur = uname + '*' + str(rand)
    ###############################
    redis_conn = get_redis_connection('default')
    key = 'register_activation_' + uname
    redis_conn.set(key, rand)
    ###############################
    code = base64.b64encode(ur.encode()).decode('utf-8')
    context = {
        'username': uname,
        'code': code
    }
    # 4.3获取模板的内容，同时完成了动态数据的传递工作
    html = render_to_string('activation.html', context)
    # 4.4 发送激活邮件
    send_mail(
        subject='达达商城::用户激活邮件',
        message=None,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=html
    )
    context = {
        'code': 200,
        'username': uname,
        'token': jwt_encode(
            {
                'id': user.pk,
                'username': uname
            }
        ),
        'carts_count': 0
    }
    return JsonResponse(context)


def activation(request):
    # 1.获取地址栏中的数据(用户名和随机数进行BASE64的编码)
    code = request.GET.get('code')
    # 2.解码操作
    b64_decode_str = base64.b64decode(code.encode()).decode('utf-8')
    # 3.将解析后的字符串分割为用户名和随机数两部分
    uname, rand = b64_decode_str.split('*')
    ###############################################
    redis_conn = get_redis_connection('default')
    key = 'register_activation_' + uname
    if not redis_conn.exists(key):
        context = {
            "code": 10022,
            "error": "激活码过期"
        }
        return JsonResponse(context)
    # 获取缓存中的随机数
    cache_value = redis_conn.get(key).decode('utf-8')
    if rand != cache_value:
        context = {
            "code": 10023,
            "error": "激活码错误"
        }
        return JsonResponse(context)
    if not UserProfile.objects.filter(username=uname):
        context = {
            "code": 10021,
            "error": "指定用户不存在导致激活失败"
        }
        return JsonResponse(context)
    UserProfile.objects.filter(username=uname).update(is_active=True)
    # 激活成功后删除缓存中的数据
    redis_conn.delete(key)
    context = {
        "code": 200
    }
    ###############################################

    return JsonResponse(context)


def smscode(request):
    # 1.获取数据
    data = json.loads(request.body)
    phone = data.get('phone')

    # 利用工具中的函数发送验证码
    key="register_sms_" + phone
    res=verify(phone,'sms',300,1,4,key)

    if res.get('statusCode') == '000000':
        context = {

            'code': 200
        }
    else:

        context = {
            'code': res.get('statusCode'),
            'error': res.get('statusMsg')
        }
    return JsonResponse(context)


def check(request):
    uname = request.GET.get('uname')
    if UserProfile.objects.filter(username=uname):
        context = {
            'code': 60001,
            'error': '用户名已经存在'
        }
    else:
        context = {
            'code': 200,
            'message': '用户名可以使用'
        }
    return JsonResponse(context)


def login(request):
    # 1.获取数据
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    carts = data.get('carts')
    # 2.校验数据 -- Homework
    # 3.检测用户是否存在，以决定用户登录是否成功
    # QuerySet
    user = UserProfile.objects.filter(username=username)
    if not user:
        context = {
            'code': 10031,
            'error': '用户不存在'
        }
        return JsonResponse(context)
    # 当前这个用户的密码 不等于 用户输入的密码:
    if user.first().password != md5(password):
        context = {
            'code': 10032,
            'error': '密码错误'
        }
        return JsonResponse(context)
    # 4.登录成功
    context = {
        'code': 200,
        'username': username,
        'token': jwt_encode(
            {
                'id': user.first().pk,
                'username': username
            }
        ),
        'carts_count': carts
    }

    # 前端收到消息，在回调函数中会将其存储到浏览器的本地存储中
    #

    #  //window.localStorage.setItem('dashop_count', data.data.length);
    # 	window.localStorage.setItem('dashop_token', data.token);
    # 	window.localStorage.setItem('dashop_user', data.username);
    # 	window.localStorage.setItem('dashop_count', data.carts_count);
    return JsonResponse(context)


class AddressView(View):

    @method_decorator(require_login)

    def get(self, request, username):
        # 反向关系
        addresses = UserProfile.objects.get(username=username).address_set.values('id', 'receiver', 'postcode', 'tag',
                                                                                  'address', 'is_default',
                                                                                  'receiver_mobile',
                                                                                  is_recycle=F('is_delete')).filter(is_delete=False)
        context = {
            'code': 200,
            'addresslist': list(addresses)
        }
        return JsonResponse(context)

    @method_decorator(require_login)
    def post(self, request, username):
        if not request.headers.get('Authorization'):
            context = {
                'code': 10033,
                'error': '请先登录'
            }
            return JsonResponse(context)

        jwt_str = request.headers.get('Authorization')
        payload = jwt_decode(jwt_str)
        if payload.get('username') != username:
            context = {
                'code': 10033,
                'error': '请先登录'
            }
            return JsonResponse(context)
        # 1.获取数据
        data = json.loads(request.body)
        receiver = data.get('receiver')
        receiver_phone = data.get('receiver_phone')
        address = data.get('address')
        postcode = data.get('postcode')
        tag = data.get('tag')

        # 2.校验数据
        # 3.保存地址信息
        user_profile = UserProfile.objects.filter(username=username)
        # 反向查找
        # 模型实例.Address_set
        aa=user_profile.first().address_set.filter(is_delete=False).exists()
        print(aa)
        address = Address.objects.create(
            receiver=receiver,
            address=address,
            postcode=postcode,
            receiver_mobile=receiver_phone,
            tag=tag,
            # user_profile = user_profile
            user_profile_id=user_profile.first().pk,
            # 取决于用户是否设置默认地址，如果这个
            is_default=not aa

        )
        context = {
            "code": 200,
            "data": "收货地址添加成功"
        }
        return JsonResponse(context)

    @method_decorator(require_login)
    def put(self, request, username, id):
        # 1.获取数据
        data = json.loads(request.body)
        address = data.get("address")
        receiver = data.get("receiver")
        tag = data.get("tag")
        receiver_mobile = data.get("receiver_mobile")
        id = data.get("id")
        # 2.校验数据
        # 3.更新数据
        Address.objects.filter(id=id).update(
            address=address,
            receiver=receiver,
            tag=tag,
            receiver_mobile=receiver_mobile
        )
        context = {
            "code": 200,
            "data": "收货地址修改成功"
        }
        return JsonResponse(context)

    @method_decorator(require_login)
    def delete(self, request, username, id):
        # 1.获取数据
        data = json.loads(request.body)
        submit_username = data.get('username')
        submit_id = data.get('id')
        # 2.校验数据
        # 3.更新数据
        # 如果原来地址为is_default=fause,在经过Mysql更新中，被忽略
        Address.objects.filter(id=id).update(is_delete=True,is_default=False)
        context = {
            "code": 200,
            "data": "删除地址成功"
        }
        return JsonResponse(context)

@require_login
def default_addess(request, username):

    data=json.loads(request.body)

    id=data.get('id')


    # 第一种方式
    # UserProfile.objects.get(username=username).address_set.filter(is_delete=False,is_default=True).update(is_default=False)

    # 第二种方式
    #  Address.objects.get(pk=id)  地址模型实例
    #  Address.objects.get(pk=id).user_profie 用户的模型实例

    Address.objects.get(pk=id).user_profile.address_set.filter(is_delete=False,is_default=True).update(is_default=False)
    Address.objects.filter(pk=id).update(is_default=True)


    context={
        'code':200,
        'data':'设置默认地址成功'

    }

    return JsonResponse(context)

def password_sms(request):



    data=json.loads(request.body)
    email=data.get('email')
    rand=random.randrange(100000,999999)

    redis_password=get_redis_connection('default')
    key=f'email{rand}'
    print(key)
    redis_password.set(key,rand,300)

    context={
        'code':rand
    }
    html = render_to_string('password_sms.html',context)

    send_mail(
        subject='密码找回',
        message=None,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=html
    )

    context={
        'code':200
    }

    return JsonResponse(context)

def verification(request):
    data=json.loads(request.body)
    code=data.get('code')
    email=data.get('email')
    redis_verify=get_redis_connection('default')
    key=f'email{code}'


    if not redis_verify.exists(key):

        context={
            'code':10001,
            'error':'验证码错误'
        }
        return JsonResponse(context)

    context={

        'code':200,
        'data':'OK'
    }
    return JsonResponse(context)

def password_new(request):

    data = json.loads(request.body)

    password1=data.get('password1')
    password2 = data.get('password2')
    email=data.get('email')

    if password1 != password2:
        context={
            'code':10001,
            'error':'两次密码不一致'
        }
        return JsonResponse(context)
    # 所以在注册时需保证邮箱的唯一性
    #
    # 判断密码在3个月内是否使用过
    user=UserProfile.objects.filter(email=email)

    up=Userpassword.objects.filter(password=password1,user=user)
    # #校验up[0]或up.first()中的expire_at 是否比当前日期时间 + 90 天


    print(up.first().expire_at)
    # if up.first().expire_at > datetime.datetime.now()+datetime.timedelta(days = 90):
    #     context={
    #         'code':10001,
    #         'error':'密码在3个月内使用过'
    #     }
    #     return JsonResponse(context)
    #
    # UserProfile.objects.filter(email=email).update(password=md5(password1))
    
    context={
        'code':200,
        'data':'OK'
    }

    return JsonResponse(context)

def password(request,username):

    data=json.loads(request.body)
    oldpassword=data.get('oldpassword')
    password1=data.get('password1')
    password2=data.get('password2')



    context={



    }
    return JsonResponse(context)

def weibo_authorization(request):

    # 打开新浪微博的授权页面
    url = 'https://api.weibo.com/oauth2/authorize?client_id=3437431638&redirect_uri=http://127.0.0.1:7000/dadashop/templates/callback.html&response_type=code'
    # requests.get(url)

    context={

        'code':200,
        # 前端代码回调函数中有  window.location.href=response.oauth_url >>>跳转到指定url

        'oauth_url':url

    }
    return JsonResponse(context)

def weibo_users(request):
    code = request.GET.get('code')

    # 向服务器发送code，以换取token
    url='https://api.weibo.com/oauth2/access_token'
    data={
        'client_id':'3437431638',
        'client_secret':'b4913cf059e7247bc4f3835469d53193',
        'grant_type':'authorization_code',
        'redirect_uri':'http://127.0.0.1:7000/dadashop/templates/callback.html',
        'code':code
    }
    res = requests.post(url,data)
    jres=json.loads(res.content)

    access_token=jres.get('access_token')
    
    context={
        'code':200,
        'access_token':access_token
    }

    
    return JsonResponse(context)