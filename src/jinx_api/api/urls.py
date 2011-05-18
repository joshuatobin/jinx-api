from django.conf.urls.defaults import *

api_calls = patterns('api.views',
    (r'get_rack_contents', 'rack.get_rack_contents'),
    (r'get_hosts_by_regex', 'host.get_hosts_by_regex'),
    (r'get_host_remote_hands_info', 'host.get_host_remote_hands_info'),
)

urlpatterns = patterns('api.views',
    # If we need to do anything specific in older versions of the protocol, add specific
    # rules here, like this:
    # (r'2\.0/get_rack_contents', 'rack.get_rack_contents_2_0')

    # (r'(?P<call>[^/]+)/doc', 'meta.get_documentation')
    # (r'list_calls', 'meta.list_calls')

    # otherwise, strip off the version and go to the list of API calls
    (r'[0-9.-]+/', include(api_calls))
)



