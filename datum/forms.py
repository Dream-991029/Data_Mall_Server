from django import forms
import datetime


class AddDataTypeForm(forms.Form):
    data_type_name = forms.CharField(max_length=50, error_messages={'required': '数据类型名称不能为空', 'max_length': '数据类型名称长度不能大于100'})
    country_name = forms.CharField(max_length=50, error_messages={'required': '国家名称不能为空', 'max_length': '国家名称长度不能大于30'})
    title = forms.CharField(max_length=150, min_length=5, error_messages={'required': '标题不能为空', 'max_length': '标题长度不能大于150', 'min_length': '标题长度不能小于5'})
    count = forms.IntegerField(error_messages={'required': '数量不能为空', 'invalid': '请检查count类型'})
    size = forms.CharField(max_length=20, error_messages={'required': '数据占用磁盘空间不能为空', 'max_length': '数据占用磁盘空间长度不能大于20'})
    is_delete = forms.CharField(required=False)
    create_time = forms.CharField(required=False)
    data_file = forms.FileField(error_messages={'required': '数据文件不能为空'})
    icon_file = forms.FileField(required=False)

    def clean_icon_name(self):
        if not self.cleaned_data.get('icon_name'):
            return ""
        return self.cleaned_data

    def clean_is_delete(self):
        if not self.cleaned_data.get('is_delete'):
            return "0"
        return self.cleaned_data

    def clean_create_time(self):
        if not self.cleaned_data.get('create_time'):
            return datetime.datetime.now()
        return self.cleaned_data

    def clean_data_file(self):
        data_file = self.cleaned_data.get('data_file', None)
        ext = data_file.name.split('.')[-1].lower()
        if ext not in ('xlsx',):
            raise forms.ValidationError("仅允许上传xlsx文件")
        return self.cleaned_data

    def clean_icon_file(self):
        icon_file = self.cleaned_data.get('icon_file', None)
        if icon_file is not None:
            ext = icon_file.name.split('.')[-1].lower()
            if ext not in ('png', 'jpg'):
                raise forms.ValidationError("支持png, jpg格式图片")
        return self.cleaned_data

    def get_errors(self):
        # 获取所有错误信息
        errors = self.errors.get_json_data()
        # 创建一个空字典,用户接受所有错误信息
        new_errors = {}
        # 遍历每个字段
        for fields in errors:
            msg_list = [message_dict['message'] for message_dict in errors[fields]]
            new_errors[fields] = msg_list
        return new_errors


class IdTypeForm(forms.Form):
    id = forms.CharField(error_messages={'required': '数据编号不能为空'})

    def clean_id(self):
        if len(self.cleaned_data.get('id')) != 24:
            raise forms.ValidationError("数据编号错误")
        return self.cleaned_data.get('id')

    def get_errors(self):
        # 获取所有错误信息
        errors = self.errors.get_json_data()
        # 创建一个空字典,用户接受所有错误信息
        new_errors = {}
        # 遍历每个字段
        for fields in errors:
            msg_list = [message_dict['message'] for message_dict in errors[fields]]
            new_errors[fields] = msg_list
        return new_errors


class CountryTypeForm(forms.Form):
    country_name = forms.CharField(error_messages={'required': '国家名称不能为空'})

    def clean_country_name(self):
        if len(self.cleaned_data.get('country_name')) != 3 or not self.cleaned_data.get('country_name').isupper():
            raise forms.ValidationError("国家名称错误")
        return self.cleaned_data.get('country_name')

    def get_errors(self):
        # 获取所有错误信息
        errors = self.errors.get_json_data()
        # 创建一个空字典,用户接受所有错误信息
        new_errors = {}
        # 遍历每个字段
        for fields in errors:
            msg_list = [message_dict['message'] for message_dict in errors[fields]]
            new_errors[fields] = msg_list
        return new_errors
