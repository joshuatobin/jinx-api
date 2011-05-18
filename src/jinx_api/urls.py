from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^jinx/', include('jinx_api.api.urls')),
)
