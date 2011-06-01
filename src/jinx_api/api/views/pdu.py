import clusto
import llclusto
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse

def get_pdu_hostnames(request):
    """Returns a list of hostnames for all hosts with a driver of LindenPDU.
    """

    pdus = clusto.get_entities(clusto_drivers=[llclusto.drivers.LindenPDU])
    
    return [pdu.hostname for pdu in pdus if pdu.hostname.lower() != 'missing']

def power_reboot(request, host_or_mac):
    """
    """
    host = get_host_or_mac_object(request, host_or_mac)

    if isinstance(host, HttpResponse):
        return host
    
    if host.has_ipmi():
        return host.ipmi_power_cycle()
    else:
        return host.power_cycle()

def power_off(request, host_or_mac):
    """
    """    
    host = get_host_or_mac_object(request, host_or_mac)

    if isinstance(host, HttpResponse):
        return host
    
    if host.has_ipmi():
        return host.ipmi_power_off()
    else:
        return host.power_off()

def power_on(request, host_or_mac):
    """ Powers on a host
    """
    host = get_host_or_mac_object(request, host_or_mac)

    if isinstance(host, HttpResponse):
        return host
    
    if host.has_ipmi():
        return host.ipmi_power_on()
    else:
        return host.power_on()

def power_status(request, host_or_mac):
    """
    """
    host = get_host_or_mac_object(request, host_or_mac)

    if isinstance(host, HttpResponse):
        return host
    
    if host.has_ipmi():
        return host.ipmi_power_status()
    else:
        return HttpResponse('%s is not IPMI enabled. Power status is not available...', status=409 % host.hostname)

def get_host_mac_object(request, hostname_or_mac):
    """ Returns an object for a hostname or a mac address...

    Arguments:
        hostname_or_mac -- The hostname or mac address of an entity.

    """
    hosts = None

    if re.match(r'[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}', hostname_or_mac, re.I):
        hosts = clusto.get_by_mac(hostname_or_mac)

    if not hosts:
        hosts = llclusto.get_by_hostname(hostname_or_mac)

    if not hosts:
        return HttpResponseNotFound('No host was found with hostname or MAC address "%s".' % hostname_or_mac)
    elif len(hosts) > 1:
        return HttpResponse('More than one host found with hostname or MAC address "%s".' % hostname_or_mac, status=409)
    else:
        return hosts[0]
    


    
        
