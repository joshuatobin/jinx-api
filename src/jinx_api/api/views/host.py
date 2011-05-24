import clusto
import llclusto
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound
import traceback

def get_hosts_by_regex(request, regex, flags=re.I):
    """Return a list of hostnames of all hosts matching a given regular expression.  
    
    The regular expression can occur anywhere in the hostname, so use ^ to 
    anchor to the start if that's what you want.
    
    Arguments:
    
        regex -- a regular expression
        flags -- optional; a set of flags suitable to be passed as the flags 
            argument for re.search (defaults to case-insensitive search)
                 
    Exceptions Raised:
    
        JinxInvalidRequestError -- Regular expression syntax was invalid.
            see the exception value for more details on what was wrong.
    """
    
    try:
        host_re = re.compile(regex, flags)
    except re.error, e:
        return HttpResponseBadRequest("regular expression syntax error: " + str(e))
    
    # I could start off with clusto.get_entities(attrs={'subkey': 'hostname'}),
    # but that would be slow because it would load every single host's full 
    # attribute list.  Using do_attr_query only fetches the hostname
    # attributes.
    
    hostname_attrs = clusto.drivers.Driver.do_attr_query(subkey='hostname')
    
    matching_hostnames = []
    
    for attr in hostname_attrs:
        if attr.value is not None and host_re.search(attr.value):
                matching_hostnames.append(attr.value)
    
    return matching_hostnames
    
def get_host_remote_hands_info(request, hostname_or_mac):
    """Return information that will help remote hands identify a host.
    
    Returns a dict like the following:
    
    {"hostname":        "sim12345.agni.lindenlab.com",
     "macs":            ["00:11:22:33:44:55", "00:11:22:33:44:56"],
     "rack":            "c2-02-01",
     "positions",       [10, 11, 12],
     "serial_number":   "SM123456",
     "colo":            "PHX",
     "pdu_connections": [{"pdu":  "pdu1-c2-02-01.dfw.lindenlab.com", 
                          "port": 13},
                         {"pdu":  "pdu2-c2-02-01.dfw.lidnenlab.com",
                          "port": 23}
                        ]
    }
    
    Arguments:
        hostname_or_mac -- The hostname or MAC address of the host.
        
    Exceptions Raised:
        JinxDataNotFoundError -- A host matching the specified hostname
            or MAC address could not be found.
        JinxInvalidStateError -- More than one host had the specified
            hostname or mac address.
    """
    
    hosts = None
    
    if re.match(r'[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}', hostname_or_mac, re.I):
        # Looks like it might be a mac, try mac address first
        hosts = clusto.get_by_mac(hostname_or_mac)
    
    if not hosts:
        # If I haven't found it yet, it must be a hostname:
        hosts = llclusto.get_by_hostname(hostname_or_mac)
    
    if not hosts:
        return HttpResponseNotFound('No host was found with hostname or MAC address "%s".' % hostname_or_mac)
    elif len(hosts) > 1:
        return HttpResponse('More than one host found with hostname or MAC address "%s".' % hostname_or_mac, status=409)
    else:
        host = hosts[0]
        
    info = {}
    
    # Pardon all of the try/catch blocks.  I want to be super-careful here, in case the
    # thing I'm calling 'host' isn't a host at all.  Trust the user to pick something 
    # useful to ask about and return all the info I can.
    
    try:
        info['hostname'] = host.hostname
    except AttributeError:
        info['hostname'] = None
    
    try:
        info['macs'] = []
        
        for port_num in host.port_info['nic-eth']:
            info['macs'].append(host.get_port_attr('nic-eth', port_num, 'mac'))
    except KeyError:
        info['macs'] = []
    
    try:
        port_info = host.port_info
        
        # If the host doesn't have power connections, maybe it's a class 7 in a chassis.  Try that.
        if 'pwr-nema-5' not in port_info:
            chassis = llclusto.drivers.LindenServerChassis.get_chassis(host)
            port_info = chassis.port_info
        
        info['pdu_connections'] = []
        
        for port_num in port_info['pwr-nema-5']:
            info['pdu_connections'].append({'pdu': port_info['pwr-nema-5'][port_num]['connection'].hostname,
                                            'port': port_info['pwr-nema-5'][port_num]['otherportnum']})
    except (KeyError, AttributeError, IndexError):
        info['pdu_connections'] = []
    
    try:
        info['serial_number'] = host.serial_number
    except AttributeError:
        info['serial_number'] = None
    
    try:
        info['colo'] =  host.parents(clusto_types=["datacenter"], search_parents=True)[0].name.upper()
    except IndexError:
        info['colo'] = None
        
    location = llclusto.drivers.LindenRack.get_rack_and_u(host)
    
    # Try the chassis instead
    if location is None:
        chassis = llclusto.drivers.LindenServerChassis.get_chassis(host)
        
        if chassis is not None:
            location = llclusto.drivers.LindenRack.get_rack_and_u(chassis)
    
    if location is not None:
        info['rack'] = location['rack'].name
        info['positions'] = location['RU']
    else:
        info['rack'] = None
        info['positions'] = None
    
    return info
