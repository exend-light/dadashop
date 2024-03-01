from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
import json
from goods.models import SKU
from django_redis import get_redis_connection
from dadashop.decorators import require_login

from django.utils.decorators import method_decorator

class CartsView(View):
    redis_conn = get_redis_connection('carts')

    @method_decorator(require_login)
    def post(self, request, username):
        # 获取提交数据
        data = json.loads(request.body)
        sku_id = data.get('sku_id')
        count = int(data.get('count'))
        # 数据校验
        # .....
        # 数据校验
        try:
            sku_object = SKU.objects.get(pk=sku_id)
        except Exception as e:
            context = {
                'code': 40001,
                'error': '对不起，指定商品不存在'
            }
            return JsonResponse(context)

        if sku_object.stock < count:
            context = {
                'code': 40002,
                'error': '商品数量超过库存限量'
            }
            return JsonResponse(context)
        # 要从REDIS中获取用户的购物信息
        ##1.缓存的键名
        cache_key = f'carts_{username}'
        fieldname = sku_id
        ##2.查询KEY是否存在，以证明用户是否有过购物记录
        if not self.redis_conn.exists(cache_key):
            fieldvalue = json.dumps({'number': count, 'status': True})
            self.redis_conn.hset(cache_key, fieldname, fieldvalue)
        else:
            if not self.redis_conn.hexists(cache_key, fieldname):
                fieldvalue = json.dumps({'number': count, 'status': True})
                self.redis_conn.hset(cache_key, fieldname, fieldvalue)
            else:
                fieldvalue = self.redis_conn.hget(cache_key, fieldname)
                jsonvalue = json.loads(fieldvalue)
                jsonvalue['number'] += count
                fieldvalue = json.dumps(jsonvalue)
                self.redis_conn.hset(cache_key, fieldname, fieldvalue)
        '''
        if (not self.redis_conn.exists(cache_key)) or (not self.redis_conn.hexists(cache_key,fieldname)):
            fieldvalue = {'number':count,'status':True}
        else:
            fieldvalue = self.redis_conn.hget(cache_key,fieldname)
            fieldvalue = json.loads(fieldvalue)
            fieldvalue['number'] += count
        fieldvalue = json.dumps(fieldvalue)
        self.redis_conn.hset(cache_key, fieldname, fieldvalue)
        '''
        context = {
            'code': 200,
            'data': {
                'carts_count': self.redis_conn.hlen(cache_key)
            },
            'base_url': 'http://127.0.0.1:8000/media/'
        }
        return JsonResponse(context)

    @method_decorator(require_login)
    def get(self, request, username):
        cache_key = f'carts_{username}'
        context = {
            'code': 200,
            'base_url': 'http://127.0.0.1:8000/media/',
            'data': self.generateData(username)
        }
        return JsonResponse(context)

    @method_decorator(require_login)
    def put(self, request, username):
        data = json.loads(request.body)
        state = data.get('state')
        statelist = ['add', 'del', 'select', 'unselect', 'selectall', 'unselectall']
        if state not in statelist:
            context = {
                'code': 30003,
                'error': '不支持的请求动作'
            }
            return JsonResponse(context)
        '''
        # 商品数量增加
        if state == 'add':
            sku_id = data.get('sku_id')
            fieldname = sku_id
            cache_key = f'carts_{username}'
            fieldvalue = json.loads(self.redis_conn.hget(cache_key,fieldname))
            fieldvalue['number'] += 1
            self.redis_conn.hset(cache_key,fieldname,json.dumps(fieldvalue))
        # 商品数量减少
        elif state == 'del':
            sku_id = data.get('sku_id')
            fieldname = sku_id
            cache_key = f'carts_{username}'
            fieldvalue = json.loads(self.redis_conn.hget(cache_key, fieldname))
            fieldvalue['number'] -= 1
            self.redis_conn.hset(cache_key, fieldname, json.dumps(fieldvalue))
        # 单一选定
        elif state == 'select':
            sku_id = data.get('sku_id')
            fieldname = sku_id
            cache_key = f'carts_{username}'
            fieldvalue = json.loads(self.redis_conn.hget(cache_key, fieldname))
            fieldvalue['status'] = True
            self.redis_conn.hset(cache_key, fieldname, json.dumps(fieldvalue))
        # 取消单一选定
        elif state == 'unselect':
            sku_id = data.get('sku_id')
            fieldname = sku_id
            cache_key = f'carts_{username}'
            fieldvalue = json.loads(self.redis_conn.hget(cache_key, fieldname))
            fieldvalue['status'] = False
            self.redis_conn.hset(cache_key, fieldname, json.dumps(fieldvalue))
        # 全选
        elif state == 'selectall':
            cache_key = f'carts_{username}'
            sku_id_lists = self.redis_conn.hkeys(cache_key)
            for sku_id in sku_id_lists:
                fieldvalue = json.loads(self.redis_conn.hget(cache_key,sku_id))
                fieldvalue['status'] = True
                self.redis_conn.hset(cache_key,sku_id,json.dumps(fieldvalue))
        # 取消全选
        elif state == 'unselectall':
            cache_key = f'carts_{username}'
            sku_id_lists = self.redis_conn.hkeys(cache_key)
            for sku_id in sku_id_lists:
                fieldvalue = json.loads(self.redis_conn.hget(cache_key, sku_id))
                fieldvalue['status'] = False
                self.redis_conn.hset(cache_key, sku_id, json.dumps(fieldvalue))
        '''
        # 商品数量增加和减少
        if state == 'add' or state == 'del':
            sku_id = data.get('sku_id')
            fieldname = sku_id
            cache_key = f'carts_{username}'
            fieldvalue = json.loads(self.redis_conn.hget(cache_key, fieldname))
            fieldvalue['number'] += 1 if state == 'add' else -1
            self.redis_conn.hset(cache_key, fieldname, json.dumps(fieldvalue))
            # 单一选定 和 取消单一选定
        elif state == 'select' or state == 'unselect':
            sku_id = data.get('sku_id')
            fieldname = sku_id
            cache_key = f'carts_{username}'
            fieldvalue = json.loads(self.redis_conn.hget(cache_key, fieldname))
            fieldvalue['status'] = True if state == 'select' else False
            self.redis_conn.hset(cache_key, fieldname, json.dumps(fieldvalue))
        # 全选 和 取消全选
        elif state == 'selectall' or state == 'unselectall':
            cache_key = f'carts_{username}'
            sku_id_lists = self.redis_conn.hkeys(cache_key)
            for sku_id in sku_id_lists:
                fieldvalue = json.loads(self.redis_conn.hget(cache_key, sku_id))
                fieldvalue['status'] = True if state == 'selectall' else False
                self.redis_conn.hset(cache_key, sku_id, json.dumps(fieldvalue))
        context = {
            'code': 200,
            'base_url': 'http://127.0.0.1:8000/media/',
            'data': self.generateData(username)
        }
        return JsonResponse(context)

    @method_decorator(require_login)
    def delete(self, request, username):
        data = json.loads(request.body)
        sku_id = data.get('sku_id')
        cache_key = f'carts_{username}'
        self.redis_conn.hdel(cache_key, sku_id)
        context = {
            'code': 200,
            'data':
                {
                    'carts_count': self.redis_conn.hlen(cache_key)
                },
            'base_url': 'http://127.0.0.1:8000/media/'
        }
        return JsonResponse(context)

    def generateData(self, username):
        data = []
        cache_key = f'carts_{username}'
        idlist = self.redis_conn.hkeys(cache_key)
        sku_objects = SKU.objects.filter(id__in=idlist)
        for sku_object in sku_objects:
            fieldvalue = json.loads(self.redis_conn.hget(cache_key, sku_object.pk))
            obj = {
                'id': sku_object.id,
                'name': sku_object.name,
                'price': sku_object.price,
                'default_image_url': sku_object.default_image_url.name,
                'count': fieldvalue.get('number'),
                'selected': fieldvalue.get('status'),
                "sku_sale_attr_name": ['尺寸'],
                "sku_sale_attr_val": ['15']
            }
            data.append(obj)
        return data
