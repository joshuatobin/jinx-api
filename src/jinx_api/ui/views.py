from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from django.template import RequestContext
from django.contrib.auth.admin import User
from django.contrib.auth.decorators import permission_required

from jinx_api.api.views.host import _get_host_instance
from jinx_api.api.views import pdu

import clusto
import llclusto
import re

POWER_STATES = (
    ('status', 'Power Status'),
    ('flip', 'Power Cycle'),
    ('off', 'Power Off'),
    ('on', 'Power On'),
)

class PowerManageForm(forms.Form):
    option = forms.ChoiceField(choices=POWER_STATES)
    hostname = forms.CharField(required=True)

    def clean_hostname(self):
        hostname = self.cleaned_data['hostname']

        return hostname

@permission_required('api.view_power_manage', login_url='/ui/')
def power_manage(request):
    if request.method == 'POST':
        form = PowerManageForm(request.POST)
        if form.is_valid():
            option = form.cleaned_data['option']
            hostname = form.cleaned_data['hostname']
            
            data = {}
            if option == 'flip':
                data['power'] = pdu.power_cycle(request, hostname)
            elif option == 'on':
                data['power'] = pdu.power_on(request, hostname)
            elif option == 'off':
                data['power'] = pdu.power_off(request, hostname)
            else:
                data['power'] = pdu.power_status(request, hostname)

            return render_to_response('power-manage-success.html', {'data':data})

        else:
            return render_to_response('power-manage.html', {'form': form})
    else:
        form = PowerManageForm()
        return render_to_response('power-manage.html', {'form': form})


def jinx_query(response):
    return HttpResponse("Jinx Query")

def index(response):
    data = {}
    data['page_title'] = 'Jinx Tools'
    return render_to_response('index.html', data)
