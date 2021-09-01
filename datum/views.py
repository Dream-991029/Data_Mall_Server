from django.views import View
from django.http import HttpResponse, JsonResponse
from .forms import AddDataTypeForm, IdTypeForm, CountryTypeForm
from django.conf import settings
from .conf import mongodb
from .utils.response import Res
from .utils.ipaddress import NetAddress
from bson.objectid import ObjectId
from django.utils.encoding import escape_uri_path
from copy import deepcopy
from io import BytesIO
import pandas as pd
import uuid
import json
import os

query = mongodb.MongoDataBase()
# Create your views here.
class DataTypeView(View):
    def get(self, request):
        """
        获取所有数据
        """
        data_type = query.coll.find({'is_delete': '0'}, {
            'is_delete': 0,
            'create_time': 0,
            'data_file_path': 0
        })
        ip_address = NetAddress(request).ip_address
        if data_type.count() != 0:
            results = []
            info_set = set()
            # 取到每一个字典
            for info in data_type:
                data_type_list = [val.get('data_type_name', '') for val in results]
                if info['data_type_name'] in data_type_list:
                    for dt in results:
                        if info['data_type_name'] == dt['data_type_name'] and info['country_name'] not in dt['country_list']:
                            dt['country_list'].append(info['country_name'])
                else:
                    obj = {
                        'data_type_name': info['data_type_name'],
                        'country_list': [info['country_name']]
                    }
                    results.append(obj)
            return Res(200, '获取数据类型成功', data=results)

        return Res(400, '获取数据类型失败', error="数据库异常")

    def post(self, request):
        """
        添加数据
        """
        # 获取数据
        req = request.POST
        # 获取文件
        req_file = request.FILES
        # 检验数据
        form = AddDataTypeForm(req, req_file)
        if form.is_valid():
            query_find = query.coll.count_documents({'title': form.cleaned_data.get('title')})
            if query_find != 0:
                return Res(400, '失败', error='该数据已存在')
            form.cleaned_data['data_file_path'] = self.uploaded_file(form.cleaned_data, req_file.get('data_file', None), type='data')
            form.cleaned_data['icon_file_path'] = self.uploaded_file(form.cleaned_data, req_file.get('icon_file', None), type='icon')
            del form.cleaned_data['data_file']
            del form.cleaned_data['icon_file']
            query_sql = query.insert(form.cleaned_data)
            if query_sql:
                form.cleaned_data['id'] = str(form.cleaned_data['_id'])
                del form.cleaned_data['_id']
                del form.cleaned_data['is_delete']
                del form.cleaned_data['data_file_path']
                del form.cleaned_data['icon_file_path']
                del form.cleaned_data['create_time']
                return Res(200, '添加数据成功!', data=form.cleaned_data)
            else:
                return Res(500, '失败', '服务器繁忙,请稍后再试!')
        else:
            return Res(400, '失败', error=form.get_errors())

    def uploaded_file(self, results, req_file, type='data'):
        if req_file is not None:
            # 获取文件后缀
            ext = req_file.name.split('.')[-1]
            # 重新命名文件
            file_name = f'{uuid.uuid4().hex[:10]}.{ext}'
            if type == 'data':
                xd_dir_path = rf'{results["data_type_name"]}/{results["country_name"]}/data'
            elif type == 'icon':
                xd_dir_path = rf'{results["data_type_name"]}/{results["country_name"]}/icon'
            # 目标文件夹路径
            dir_path = os.path.join(settings.STATICFILES_DIRS[0], xd_dir_path)
            # 判断目标文件夹是否存在,不存在则进行创建
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # 目标文件路径
            file_path = os.path.join(dir_path, file_name)
            file_df = pd.read_excel(req_file)
            file_df.to_excel(file_path, index=False)
            return xd_dir_path + '/' + file_name
        elif type == 'icon':
            return f'default/icon/default.jpg'


class DownloadView(View):
    def get(self, request):
        """
        下载文件
        """
        # 获取数据
        req = request.GET
        form = IdTypeForm(req)
        if form.is_valid():
            # 查询数据
            data = query.coll.find_one({
                '_id': ObjectId(form.cleaned_data.get('id', '')),
                'is_delete': '0'
            })
            if data:
                response = self.download_file(data)
                return response

            return Res(400, '下载文件失败', error='该数据不存在')

        return Res(400, '下载失败', error=form.get_errors())

    def download_file(self, data):
        file_path = os.path.join(settings.STATICFILES_DIRS[0], data['data_file_path'])
        file_name = escape_uri_path(data['title'] + '.xlsx')
        x_io = BytesIO()
        df = pd.read_excel(file_path)
        df.to_excel(x_io, index=False)
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        response.write(x_io.getvalue())
        return response


class CountryView(View):
    def get(self, request):
        # 获取国家
        req = request.GET
        form = CountryTypeForm(req)
        ip_address = NetAddress(request).ip_address
        if form.is_valid():
            # 查询数据
            data = query.coll.find({
                'country_name': form.cleaned_data.get('country_name'),
                'is_delete': '0'
            }, {
                'is_delete': 0,
                'create_time': 0,
                'data_file_path': 0
            })
            results = []
            if data.count() != 0:
                for info in data:
                    obj = deepcopy(info)
                    obj['id'] = str(obj['_id'])
                    obj['icon_file_path'] = ip_address + settings.STATIC_URL + obj['icon_file_path']
                    del obj['_id']
                    results.append(obj)
                return Res(200, '获取国家列表成功', data=results)

            return Res(400, '获取国家列表失败', error='该国家数据不存在')

        return Res(400, '获取国家列表失败', error=form.get_errors())


class InfoView(View):
    def get(self, request):
        # 获取数据
        req = request.GET
        form = IdTypeForm(req)
        ip_address = NetAddress(request).ip_address
        if form.is_valid():
            # 查询数据
            data = query.coll.find({
                '_id': ObjectId(form.cleaned_data.get('id')),
                'is_delete': '0'
            }, {
                'is_delete': 0,
                'create_time': 0,
                'data_file_path': 0
            })
            if data.count() != 0:
                obj = list(data)[0]
                obj['id'] = str(obj['_id'])
                obj['icon_file_path'] = ip_address + settings.STATIC_URL + obj['icon_file_path']
                del obj['_id']
                return Res(200, '获取国家详细信息成功', data=obj)

            return Res(400, '获取国家详细信息失败', error='该数据不存在')

        return Res(400, '获取国家详细信息失败', error=form.get_errors())

