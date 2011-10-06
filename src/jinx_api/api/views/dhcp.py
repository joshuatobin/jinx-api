import clusto
import llclusto
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from jinx_api.http import HttpResponseInvalidState
import traceback


def set_dhcp_association(request, hostname, mac_address):
    """
    Function that sets a hostname to a specified mac_address.

    Arguments:
                 hostname -- The hostname of an entity.
                 mac_address -- The mac_address of an entity.

    Exceptions Raised:
            JinxInvalidStateError -- More than one host had the specified
                hostname or mac address, or could not be found.
    """

    hostname = hostname.lower()
    mac_address = mac_address.lower()

    servers = clusto.get_by_mac(mac_address)
    ipmi_hosts = clusto.get_entities(attrs=[{'subkey': 'ipmi_mac', 'value': mac_address}])
    hosts = llclusto.get_by_hostname(hostname)
    
    if not servers and not ipmi_hosts:
        return HttpResponseInvalidState('Could not find any entities with MAC address: "%s".' % mac_address) 
    

    try:
        clusto.begin_transaction()

        for host in hosts:
            for (port_type, port_num, ignore, ignore) in host.port_info_tuples:
                if host.get_hostname(port_type, port_num) == hostname:
                    host.del_hostname(port_type, port_num)
        
        for server in servers:
            for (port_type, port_num, ignore, ignore) in server.port_info_tuples:
                if server.get_port_attr(port_type, port_num, "mac") == mac_address:
                    server.set_hostname(hostname, port_type, port_num)
        
        for host in ipmi_hosts:
            ipmi = host.ipmi
            if ipmi[1] == mac_address:
                host.set_ipmi_info(hostname, ipmi[1])
        
        clusto.commit()
    except:
        clusto.rollback_transaction()
        raise

def delete_dhcp_association(request, hostname, mac_address):
    """
    Function that deletes a hostname from a specified mac_address.

    Arguments:
                 hostname -- The hostname of an entity.
                 mac_address -- The mac_address of an entity.

    Exceptions Raised:
          JinxInvalidStateError -- More than one host had the specified                                                       
              hostname or mac address, or could not be found.
    """

    hostname = hostname.lower()
    mac_address = mac_address.lower()

    try:
        server = clusto.get_by_mac(mac_address)[0]
    except IndexError:
        return HttpResponseInvalidState('Could not find any entities with MAC address: "%s".' % mac_address) 

    try:
        clusto.begin_transaction()

        for (port_type, port_num, ignore, ignore) in server.port_info_tuples:
            if server.get_hostname(port_type, port_num) == hostname:
                server.del_hostname(port_type, port_num)

        clusto.commit()
    except:
        clusto.rollback_transaction()
        raise
        


    
    
        
    
