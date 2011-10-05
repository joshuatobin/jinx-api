from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
#    (r'^admin/', include(admin.site.urls)),
#    (r'^jinx/', include('jinx_api.api.urls')),
    (r'^power-manage', 'jinx_api.ui.views.power_manage'),
    (r'^jinx-query', 'jinx_api.ui.views.jinx_query'),
    (r'^$', 'jinx_api.ui.views.index'),

)
