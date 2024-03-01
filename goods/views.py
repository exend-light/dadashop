from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import F
import json
# Create your views here.

from .models import Catalog
from .models import SKU, SPU
from .models import SPUSaleAttr, SaleAttrValue
from django.core.paginator import Paginator


def index(request):
    data = []
    catalogs = Catalog.objects.all()
    # 遍历所有的分类
    for catalog_object in catalogs:
        # 获取当前分类下的3个正常上架的商品
        sku_objects = SKU.objects.values('name', 'caption', 'price', skuid=F('id'),
                                         image=F('default_image_url')).filter(spu__in=catalog_object.spu_set.all(),
                                                                              is_launched=True)[:3]
        data.append({
            'catalog_id': catalog_object.id,
            'catalog_name': catalog_object.name,
            'sku': list(sku_objects)
        })
    context = {
        "code": 200,
        "base_url": "http://127.0.0.1:8000/media/",
        "data": data
    }
    return JsonResponse(context)


def catalogs(request, id):
    try:
        catalog_object = Catalog.objects.get(pk=id)
    except Exception as e:
        context = {
            'code': 20001,
            'error': '对不起，商品分类不存在'
        }
        return JsonResponse(context)
    # 获取当前这个分类下的正常上架所有商品
    sku_objects = SKU.objects.values('name', 'price', skuid=F('id'), image=F('default_image_url')).filter(
        spu__in=catalog_object.spu_set.all(), is_launched=True).order_by('id')
    # 每页显示的记录数
    pagesize = 1
    # 分页操作
    pagiator = Paginator(sku_objects, pagesize)
    # 取地址栏传递的页码
    page = request.GET.get('page')
    # 获取该页中的数据
    page_data = pagiator.get_page(page)

    context = {
        "code": 200,
        # 获取当前页的数据
        "data": list(page_data.object_list),
        "paginator": {
            # 每页显示的记录数
            "pagesize": pagesize,
            # 总记录数
            "total": sku_objects.count()
        },
        "base_url": "http://127.0.0.1:8000/media/"
    }
    return JsonResponse(context)


def detail(request, id):
    try:
        sku_object = SKU.objects.get(pk=id, is_launched=True)
    except Exception as e:
        context = {
            'code': 20002,
            'error': '对不起，指定商品不存在'
        }
        return JsonResponse(context)
    # ////////////////////////////////////////////////////
    # ***************************
    catalog_id = sku_object.spu.catalog.id
    catalog_name = sku_object.spu.catalog.name
    # ***************************
    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    name = sku_object.name
    caption = sku_object.caption
    price = sku_object.price
    # ImageField返回django.db.models.fields.files.ImageFieldFile
    image = sku_object.default_image_url.name
    # 正向关系
    spu_id = sku_object.spu.id
    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # sku_sale_attrs1 = sku_object.spu.spusaleattr_set.all()
    # sku_sale_attrs2 = SPUSaleAttr.objects.filter(spu_id = spu_id)
    # print(sku_sale_attrs1.query)
    # print(sku_sale_attrs2.query)
    sku_sale_attr_id = sku_object.spu.spusaleattr_set.values_list('id', flat=True)
    sku_sale_attr_names = sku_object.spu.spusaleattr_set.values_list('name', flat=True)
    # print(sku_sale_attr_id)
    # print(sku_sale_attr_names)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    sku_sale_attr_val = SaleAttrValue.objects.values('id', 'name', 'spu_sale_attr_id').filter(
        spu_sale_attr_id__in=list(sku_sale_attr_id))

    # print(sku_sale_attr_val)
    sku_sale_attr_val_id = sku_sale_attr_val.values_list('id', flat=True)
    sku_sale_attr_val_names = sku_sale_attr_val.values_list('name', flat=True)

    # print(sku_sale_attr_val_id)
    # print(sku_sale_attr_val_names)
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    sku_all_sale_attr_vals_id = {id: [item.get('id') for item in list(sku_sale_attr_val.filter(spu_sale_attr_id=id))]
                                 for id in list(sku_sale_attr_id)}
    sku_all_sale_attr_vals_name = {
        id: [item.get('name') for item in list(sku_sale_attr_val.filter(spu_sale_attr_id=id))] for id in
        list(sku_sale_attr_id)}

    print(sku_all_sale_attr_vals_id)
    print(sku_all_sale_attr_vals_name)
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    context = {
        "code": 200,
        "data": {
            # 类1:类别id 类别name
            "catalog_id": catalog_id,
            "catalog_name": catalog_name,

            # 类2：SKU
            "name": name,
            "caption": caption,
            "price": price,
            "image": image,
            "spu": spu_id,

            # 类3：详情图片
            "detail_image": "v2-1.jpg",

            # 类4：SPU属性名称
            "sku_sale_attr_id": list(sku_sale_attr_id),
            "sku_sale_attr_names": list(sku_sale_attr_names),

            # 类5：SPU属性值
            "sku_sale_attr_val_id": list(sku_sale_attr_val_id),
            "sku_sale_attr_val_names": list(sku_sale_attr_val_names),

            # SPU属性名称和属性值的对应关系 -- id
            "sku_all_sale_attr_vals_id": sku_all_sale_attr_vals_id,
            # SPU属性名称和属性值的对应关系 -- name
            "sku_all_sale_attr_vals_name": sku_all_sale_attr_vals_name,

            # 类6和类7：规格属性名和规格属性值
            "spec": {
                "批次": "2000",
                "数量": "2000",
                "年份": "2000"
            },
            # 商品的图片列表
            "images": ["1.jpg", "2.jpg", "3.jpg", "4.jpg"]
        },
        "base_url": "http://127.0.0.1:8000/media/"
    }
    # ////////////////////////////////////////////////////
    return JsonResponse(context)


def sku(request):
    # {'1': 1, '2': 4,'6':3, 'spuid': 1}
    # { SPU属性名称ID:SPU属性值ID }
    data = json.loads(request.body)
    spuid = data.get('spuid')
    # 获取SPU对象
    spu_object = SPU.objects.get(id=spuid)
    # 获取到了当前这个SPU下所有的商品
    sku_objects = spu_object.sku_set.all()
    # 现在要遍历获取到的属性值ID，而spuid原来存在于data中
    data.pop('spuid')
    for key, val in data.items():
        sku_objects = sku_objects.filter(sale_attr_value=val)
    if sku_objects:
        context = {
            'code': 200,
            'data': sku_objects.first().pk
        }
        return JsonResponse(context)
    context = {
        'code': 30001,
        'error': '对不起，商品不存在'
    }
    return JsonResponse(context)


def search(request):
    q = request.POST.get('q')
    if len(q) == 0:
        context = {
            'code': 30001,
            'msg': '对不起，关键字不能为空'
        }
        return JsonResponse(context)
    sku_objects = SKU.objects.filter(name__contains=q).values('name','price',skuid=F('id'),image=F('default_image_url'))
    pagesize = 1
    paginator = Paginator(sku_objects,pagesize)
    page = request.GET.get('page',1)
    page_data = paginator.get_page(page)
    context = {
        'code': 200,
        "baseurl": "http://127.0.0.1:8000/media/",
        'paginator': {
            'total': sku_objects.count(),
            'pagesize': pagesize
        },
        'data': list(page_data.object_list)
    }
    return JsonResponse(context)
