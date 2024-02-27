import hashlib
import jwt
from django.conf import settings
import random
from ronglian_sms_sdk import SmsSDK
import json
from django_redis import get_redis_connection
import base64
from django.core.mail import send_mail
from django_redis import get_redis_connection
from django.template.loader import render_to_string

def md5(str):
    md5 = hashlib.md5()
    md5.update(str.encode('utf-8'))
    return md5.hexdigest()

'''
 def encode(
        self,
        payload: Dict[str, Any],
        key: str,
        algorithm: Optional[str] = "HS256",
        headers: Optional[Dict] = None,
        json_encoder: Optional[Type[json.JSONEncoder]] = None,
    )
'''
def jwt_encode(payload):
    jwt_str = jwt.encode(

        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm='HS256'
    )
    return jwt_str


def jwt_decode(jwt_str):
    payload = jwt.decode(
        jwt=jwt_str,
        key=settings.JWT_SECRET_KEY,
        algorithms='HS256'
    )
    return payload


def build_random_string(type=1, lengh=4):
    if type == 1:
        string = '0647825391'
    elif type == 2:
        string = 'abcdefghijklmnopqrstuvwxyz'
    elif type == 3:
        string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    else:
        string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    random_string = ''

    for i in range(lengh):
        random_string = random_string + string[random.randint(0, len(string) - 1)]
    return random_string


def verify(phone,db_num,time,type,lengh,key):
    # 构造函数
    sms = SmsSDK(
        accId=settings.SMS_ACCOUNT_SID,
        accToken=settings.SMS_AUTH_TOKEN,
        appId=settings.SMS_APP_ID
    )

    rand = build_random_string(type=type,lengh=lengh)
    # 将随机数保存到redis中
    redis_conn = get_redis_connection(db_num)
    redis_conn.set(key, rand, time)
    # 发送短信
    res = sms.sendMessage(settings.SMS_TEMPLATE_REGISTER_ID, phone, (rand,))
    return json.loads(res)

# def email(context,key,subject,):
#
#
#     rand = random.randint(1000, 9999)
#
#     ur = uname + '*' + str(rand)
#     ###############################
#     redis_conn = get_redis_connection('default')
#
#     redis_conn.set(key, rand)
#     ###############################
#     code = base64.b64encode(ur.encode()).decode('utf-8')
#
#     # 4.3获取模板的内容，同时完成了动态数据的传递工作
#     html = render_to_string('activation.html', context)
#     # 4.4 发送激活邮件
#     send_mail(
#         subject='达达商城::用户激活邮件',
#         message=None,
#         from_email=settings.EMAIL_HOST_USER,
#         recipient_list=[email],
#         html_message=html
#     )



