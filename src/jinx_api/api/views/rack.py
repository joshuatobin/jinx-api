import clusto
import llclusto
from django.http import HttpResponseNotFound

def get_rack_contents(request, rack_name):
    """List all servers, PDUs, and switches in the given rack.  
    
    Returns a list of dicts, like this:
    
    [{'hostname':      'sim1234.agni.lindenlab.com',
      'type':          'server',
      'serial_number': 'SM12345'},
     {'hostname':      'pdu2-c9-02-01.dfw.lindenlab.com',
      'type':          'pdu',
      'serial_number': 'CNJ29835'
     }, 
     {'hostname':      'ges-c9-02-01.dfw.lindenlab.com',
      'type':          'switch',
      'serial_number': '12345'
     }, 
     
     ...]
     
    Arguments:
        rack_name -- The name of the rack (case insensitive).
        
    Exceptions Raised:
        JinxDataNotFoundError -- The requested rack does not exist.
    
    """
     
    try:
        rack = clusto.get_by_name(rack_name)
    except LookupError:
        return HttpResponseNotFound("Rack %s not found." % rack_name)
    
    contents = []
    
    interesting_types = [llclusto.drivers.LindenServer, llclusto.drivers.LindenPDU, llclusto.drivers.LindenSwitch]
    
    for thing in rack:
        if isinstance(thing, llclusto.drivers.Class7Chassis):
            devices = thing.contents()
        else:
            devices = [thing]
            
        for device in devices:
            device_info = {
                           'hostname': device.hostname,
                           'serial_number': device.serial_number
                           }
            
            if isinstance(device, llclusto.drivers.LindenServer):
                device_info['type'] = 'server'
            elif isinstance(device, llclusto.drivers.LindenPDU):
                device_info['type'] = 'pdu'
            elif isinstance(device, llclusto.drivers.LindenSwitch):
                device_info['type'] = 'switch'
            
            contents.append(device_info)
    
    return contents

def get_server_hostnames_in_rack(request, rack_name):
    """
    Returns a list of server hostnames in a rack with a clusto_type of server.

    Arguments:
        rack_name -- The name of the rack (case insensitive).
        
    Exceptions Raised:
        JinxDataNotFoundError -- The requested rack does not exist.
    """

    try:
        rack = clusto.get_by_name(rack_name)
    except LookupError:
        return HttpResponseNotFound("Rack %s not found." % rack_name)

    return set([x.hostname for x in rack.contents(search_children=True, clusto_types=['server']) if x.hostname != None])
