from django.urls import re_path
from datum.views import *

urlpatterns = [
    re_path('^datatype/$', DataTypeView.as_view()),
    re_path('^download/$', DownloadView.as_view()),
    re_path('^country/$', CountryView.as_view()),
    re_path('^info/$', InfoView.as_view())
]
