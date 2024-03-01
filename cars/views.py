import json

from django.http import JsonResponse
from goods.models import SKU
from django.shortcuts import render,HttpResponse
from django.views import View
from django_redis import get_redis_connection
# Create your views here.
from dadashop.decorators import require_login
from django.utils.decorators import method_decorator

class CartsView(View):
    redis_conn=get_redis_connection('carts')

    @method_decorator(require_login)
    def post(self,request,username):
        data=json.loads(request.body)

        sku_id=data.get('skuid')
        count=data.get('count')

        try:
            sku_object=SKU.objects.get(pk=sku_id)
        except Exception as e:


            context={
                'code':40001,
                'error':'对不起，指定的商品不存在'

            }
            return HttpResponse(context)
        if sku_object.stock<sku_object.count:
            context={
                'code':40002,
                'error':'对不起，指定的商品超过库存限量'
            }

            return HttpResponse(context)

        cache_key=f'carts_{username}'
        fieldname = sku_id
        if not self.redis_conn.exists(cache_key):

            fieldvalue=json.dumps({'number':count,'status':True})

        else:
            if not self.redis_conn.hexists(cache_key,fieldname):
                fieldvalue=json.dumps({'number':count,'status':True})
            else:
                fieldvalue=self.redis_conn.hset(cache_key,fieldname)
                jsonvalue=json.loads(fieldvalue)
                jsonvalue['number']+=count
                fieldvalue=json.dumps(jsonvalue)
                self.redis_conn.hset(cache_key,fieldname,fieldvalue)
        self.redis_conn.hset(cache_key, fieldname, fieldvalue)

        context={
            'code':200,
            'data':{
                'cart_count':self.redis_conn.hlen(cache_key),

            },
            'base_url':'http://127.0.0.1:8000/media/'

        }
        return JsonResponse(context)
    @method_decorator(require_login)
    def get(self,request,username):
        data=[]
        cache_key=f'carts_{username}'
        idlist=self.redis_conn.hkey(cache_key)
        # idlist为字节串构成的列表
        # id__in = idlist  自动的将字节串转换为整数与id进行比较
        sku_objects=SKU.objects.filter(id__in=idlist)
        for sku_object in sku_objects:
            fieldvalue=json.loads(self.redis_conn.hget(cache_key,sku_object.id))
            obj={
                'id':sku_object.id,
                'name':sku_object.name,
                'price':sku_object.price,
                'default_image_url':sku_object.default_image_url.name,
                'count':fieldvalue.get('number'),
                'selected':fieldvalue.get('status'),
                'sku_sale_attr_name':['尺寸'],
                'sku_sale_attr_val':['15']
            }
            data.append(obj)

        context={
            'code':200,
            'base_url':'http://127.0.0.1:8000/media/',
            'data':data
        }

        return JsonResponse(context)

    @method_decorator(require_login)
    def put(self,request,username):
        data=json.loads(request.body)
        state=data.get('state')
        redis_conn=get_redis_connection('carts')
        cache_key = f'carts_{username}'
        if state=='add':
            sku_id=data.get('sku_id')
            redis_conn.hset(cache_key,sku_id,True)

        elif state=='del':
            sku_id=data.get('sku_id')


        elif state=='select':
            sku_id=data.get('sku_id')


        elif state=='unselect':
            sku_id=data.get('sku_id')

        elif state=='selectall':
            pass

        elif state == 'unselectall':
            pass

        context={
            'code':30003,
            'error':'不支持的请求'
        }
        return JsonResponse('ok')

    @method_decorator(require_login)
    def delete(self,request,username):
        data=json.loads(request.body)
        sku_id=data.get('sku_id')
        cache_key=f'carts_{username}'
        self.redis_conn.hdel(cache_key,sku_id)
        context={
            'code':200,
            'data':
                {
                    'carts_count':self.redis_conn.hlen(cache_key)
                },
            'base_url':'http://127.0.0.1:8000/media/'
        }
        
        return JsonResponse(context)













