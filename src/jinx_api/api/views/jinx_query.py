import clusto
import llclusto
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from host import _get_host_instance, _get_device_info
from jinx_api.http import HttpResponseInvalidState
import traceback

def jinx_query_serial(request, serial_number):
    """ Returns information about a device by serial number. 

    Arguments:
        serial_number -- The serial number of the device.

    Exceptions Raised:
        JinxInvalidStateError -- The requested rack_name could not be found.
    """

    host = clusto.get_entities(attrs=[{'key': 'serial_number', \
                                       'subkey': 'property', \
                                       'value': serial_number }])

    if host:
        return _get_device_info(request, host[0])
    else:
        return HttpResponseInvalidState("Serial Number %s not found." % serial_number)

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


