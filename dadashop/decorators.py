from django.http import JsonResponse
from .utils import jwt_decode
def require_login(func):
    def wrapper(request, *args, **kwargs):
        # 如需判断，requests模块(爬虫等)，发送请求的判断

        print(request.headers.get('authorization'))
        # 如果有，
        if request.headers.get("authorization"):
            # 对拿到的JWT进行解码，获取到payload，并判断与jwt中的是否一致
            try:
                payload=jwt_decode (request.headers.get('authorization'))
                return func(request, *args, **kwargs)
            #如果authorization不一致，jwt_decode方法将会执行报错，然后执行except的代码
            except Exception as e:
                return JsonResponse({"code": 400, "errmsg": "请先登录"})
        #     如果没有
        else:

            return JsonResponse({"code": 400, "errmsg": "请先登录"})

    return wrapper