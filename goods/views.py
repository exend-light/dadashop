import json

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.http import JsonResponse
from .models import Catalog
from  django.db.models import F
from .models import SKU,SPU
from django.core.paginator import Paginator
# Create your views here.

def index(request):
    data=[]
    catalogs=Catalog.objects.all()
    for catalog_objects in catalogs:
        sku_objects=SKU.objects.values('name','caption','price',skuid=F('id'),image=F('default_image_url')).filter(spu__in=catalog_objects.spu_set.all(),is_launched=True)[0:3]
        data.append({
            'catalog_id':catalog_objects.id,
            'catalog_name':catalog_objects.name,
            'sku':list(sku_objects)
        })

    print(data)
    context={
        'code':200,
        'base_url':"http://127.0.0.1:8000/media/",
        'data':data

    }
    return JsonResponse(context)


def catalogs(request,id):
    try:
        catalog_object=Catalog.objects.get(pk=id)

    except  Exception as e:
        context={
            'code':20001,
            'error':'对不起，商品不存在'
        }
        return JsonResponse(context)

    sku_objects=SKU.objects.values('name','price',skuid=F('id'),image=F('default_image_url')).filter(spu__in=catalog_object.spu_set.all(),is_launched=True).order_by('id')
    print(sku_objects)

    pagesize=1
    pagiator=Paginator(sku_objects,pagesize)

    page=request.GET.get('page')
    print(page)

    page_data=pagiator.get_page(page)

    context={
        'code':200,
        'data':list(page_data.object_list),
        'paginator':{
            'pagesize':pagesize,
            'total':sku_objects.count()
        },
        'base_url':'http://127.0.0.1:8000/media/'

    }

    return JsonResponse(context)

def detail(request,id):
    try:
        sku_object=SKU.objects.get(pk=id,is_launched=True)
        print(sku_object)
    except Exception as e:
        context={
            'code':200,
            'error':'对不起，指定的商品不存在'

        }
        return JsonResponse(context)

    catalog_id=sku_object.spu.catalog.id
    catalog_name=sku_object.spu.catalog.name
    name=sku_object.name
    caption=sku_object.caption
    price=sku_object.price

    image=sku_object.default_image_url.name
    spu_id=sku_object.spu.id
    # spu_id = sku_object.spu_id

    sku_sale_attr_id=sku_object.sale_attr_value.all()

    sku_all_sale_attr_vals_id={id:'abc' for id in list(sku_sale_attr_id)}


    context= {
        "code": 200,
        "data": {
            # 类1:类别id 类别name
            "catalog_id":catalog_id,
            "catalog_name": catalog_name,

            # 类2：SKU
            "name": name,
            "caption": caption,
            "price": price,
            "image": image,
            "spu": spu_id,



            # 类3：详情图片
            "detail_image": "v2-1.jpg",



            # 类4：销售属性(SPU的属性名称)
            "sku_sale_attr_id": [7, 8],
            "sku_sale_attr_names": ["尺寸", "颜色"],



            # 类5：销售属性值（SPU属性值）
            "sku_sale_attr_val_id": [11, 12, 13],
            "sku_sale_attr_val_names": ["18寸", "19寸", "蓝色"],



            # 销售属性和销售属性值的对应关系
            "sku_all_sale_attr_vals_id": {
                "7": [11, 12],
                "8": [13]
            },
            "sku_all_sale_attr_vals_name": {
                "7": ["18寸", "19寸"],
                "8": ["蓝色"]
            },

            # 类6和类7：规格属性名和规格属性值
            "spec": {
                "批次": "2000",
                "数量": "2000",
                "年份": "2000"
            }
        },
        "base_url": "http://127.0.0.1:8000/media/"
    }

    return JsonResponse(context)



def sku(request):

    data=json.loads(request.body)

    spuid=data.get('spuid')
    spu_object=SPU.objects.get(pk=spuid)

    sku_objects=spu_object.sku_set.all()

    data.pop('spuid')
    # 根据sale_attr_value=val，一层层的过滤
    for key,val in data.items():

        sku_objects=sku_objects.filter(sale_attr_value=val)

    context={
        'code':200,
        'data':sku_objects

    }


    return HttpResponse(context)

def search(request):
    q=request.POST.get('q')
    print(len(q))
    if len(q)==0:
        context={
            'code':30001,
            'msg':'对不起，关键字不能为空'
        }

        return  JsonResponse(context)
    sku_objects=SKU.objects.filter(name__contains=q).values('name','price')

    context={
        'code':200,
        'baseurl':'http://127.0.0.1:8000/media/',
        'pagenator':{
            'total':20,
            'pagesize':5

        },
        'data':list(sku_objects)

    }
    return JsonResponse(context)

    


