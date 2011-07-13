import clusto
import llclusto
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from host import _get_host_instance
from jinx_api.http import HttpResponseInvalidState
import traceback

def jinx_query_rack(request, rack_name):
    """List all servers, PDUs, and switches in the given rack.  
    
    Returns a list of dicts, like this:
    
    [{"hostname":        "sim12345.agni.lindenlab.com",
     "macs":            ["00:11:22:33:44:55", "00:11:22:33:44:56"],
     "rack":            "c2-02-01",
     "positions",       [10, 11, 12],
     "serial_number":   "SM123456",
     "colo":            "PHX",
     "type":            "server",
     "pdu_connections": [{"pdu":  "pdu1-c2-02-01.dfw.lindenlab.com", 
                          "port": 13},
                         {"pdu":  "pdu2-c2-02-01.dfw.lidnenlab.com",
                          "port": 23}
                        ]
    },
    ...]
     
    Arguments:
        rack_name -- The name of the rack (case insensitive).
        
    Exceptions Raised:
        JinxInvalidStateError -- The requested rack_name could not be found.
    
    """
     
    try:
        rack = clusto.get_by_name(rack_name)
    except LookupError:
        return HttpResponseInvalidState("Rack %s not found." % rack_name)
    
    contents = []

    for thing in rack:
        if isinstance(thing, llclusto.drivers.Class7Chassis):
            devices = thing.contents()
        else:
            devices = [thing]
            
        for device in devices:
            device_info = _get_device_info(request, device)
            contents.append(device_info)

    return contents

def jinx_query_hostname_mac(request, hostname_or_mac):
    """Returns information about a hostname or mac address for jinx-query
    
    Returns a dict like the following:
    
    {"hostname":        "sim12345.agni.lindenlab.com",
     "macs":            ["00:11:22:33:44:55", "00:11:22:33:44:56"],
     "rack":            "c2-02-01",
     "positions",       [10, 11, 12],
     "serial_number":   "SM123456",
     "colo":            "PHX",
     "type":            "server",
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
    host = _get_host_instance(request, hostname_or_mac)

    if isinstance(host, HttpResponse):
        return host

    return _get_device_info(request, host)

def _get_device_info(request, device):
    """
    Returns a dict of device info like the following:
    
    {"hostname":        "sim12345.agni.lindenlab.com",
     "macs":            ["00:11:22:33:44:55", "00:11:22:33:44:56"],
     "rack":            "c2-02-01",
     "positions",       [10, 11, 12],
     "serial_number":   "SM123456",
     "colo":            "PHX",
     "type":            "server",
     "pdu_connections": [{"pdu":  "pdu1-c2-02-01.dfw.lindenlab.com", 
                          "port": 13},
                         {"pdu":  "pdu2-c2-02-01.dfw.lidnenlab.com",
                          "port": 23}
                        ]
    }
    """
    info = {}
    
    # Pardon all of the try/catch blocks.  I want to be super-careful here, in case the
    # thing I'm calling 'host' isn't a host at all.  Trust the user to pick something 
    # useful to ask about and return all the info I can.
    
    try:
        info['hostname'] = device.hostname
    except AttributeError:
        info['hostname'] = None
    
    try:
        info['macs'] = []
        
        for port_num in device.port_info['nic-eth']:
            info['macs'].append(device.get_port_attr('nic-eth', port_num, 'mac'))
    except KeyError:
        info['macs'] = []
    
    try:
        port_info = device.port_info
        
        # If the host doesn't have power connections, maybe it's a class 7 in a chassis.  Try that.
        if 'pwr-nema-5' not in port_info:
            chassis = llclusto.drivers.LindenServerChassis.get_chassis(device)
            port_info = chassis.port_info
        
        info['pdu_connections'] = []

        for port_num in port_info['pwr-nema-5']:
            if port_info['pwr-nema-5'][port_num]['connection']:
                info['pdu_connections'].append({'pdu': port_info['pwr-nema-5'][port_num]['connection'].hostname,
                                                'port': port_info['pwr-nema-5'][port_num]['otherportnum']})
    except (KeyError, AttributeError, IndexError):
        info['pdu_connections'] = []
    
    try:
        info['serial_number'] = device.serial_number
    except AttributeError:
        info['serial_number'] = None
    
    try:
        info['colo'] =  device.parents(clusto_types=["datacenter"], search_parents=True)[0].name.upper()
    except IndexError:
        info['colo'] = None
        
    location = llclusto.drivers.LindenRack.get_rack_and_u(device)
    
    # Try the chassis instead
    if location is None:
        chassis = llclusto.drivers.LindenServerChassis.get_chassis(device)
        
        if chassis is not None:
            location = llclusto.drivers.LindenRack.get_rack_and_u(chassis)
    
    if location is not None:
        info['rack'] = location['rack'].name
        info['positions'] = location['RU']
    else:
        info['rack'] = None
        info['positions'] = None
    
    if isinstance(device, llclusto.drivers.LindenServer):
        info['type'] = 'server'
    elif isinstance(device, llclusto.drivers.LindenPDU):
        info['type'] = 'pdu'
    elif isinstance(device, llclusto.drivers.LindenSwitch):
        info['type'] = 'switch'

    return info

