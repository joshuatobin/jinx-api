from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^jinx/', include('jinx_api.api.urls')),
    (r'^power-manage/$', 'views.power_manage'),
)
