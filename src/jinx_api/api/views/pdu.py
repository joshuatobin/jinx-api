import clusto
import llclusto
import re
from django.contrib.auth.models import User, Group
from jinx_client.jinx_exceptions import JinxInvalidRequestError, JinxDataNotFoundError, JinxInvalidResponseError, JinxActionForbiddenError

def get_pdu_hostnames(request):
    """Returns a list of hostnames for all hosts with a driver of LindenPDU.

    Arguments:
        None

    Exceptions Raised:
        None
    """

    pdus = clusto.get_entities(clusto_drivers=[llclusto.drivers.LindenPDU])
    
    return [pdu.hostname for pdu in pdus if pdu.hostname.lower() != 'missing']

def get_host_or_mac_object(request, hostname_or_mac):
    """ Returns an object for a hostname or a mac address...

    Arguments:
        hostname_or_mac -- The hostname or mac address of an entity.

    Exceptions Raised:
        None
    """
    
    hosts = None

    if re.match(r'[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}', hostname_or_mac, re.I):
        hosts = clusto.get_by_mac(hostname_or_mac)

    if not hosts:
        hosts = llclusto.get_by_hostname(hostname_or_mac)

    return hosts

def power_cycle(request, host_or_mac):
    """ Issues a power-cycle request to a hosts PDU or IPMI controller.

    Arguments:
        hostname_or_mac -- The hostname or mac address of an entity.

    Exceptions Raised:
        JinxDataNotFoundError -- Could not find the host_or_mac in Jinx Database.
        JinxInvalidStateError -- More than one host was found matching host_or_mac.
        JinxActionForbiddenError -- Only users within the operations group may flip databases.
    """
    host = get_host_or_mac_object(request, host_or_mac)

    if not host:
        return JinxDataNotFoundError('Could not find %s in the Jinx Database.' % host_or_mac)
    elif len(host) > 1:
        return JinxInvalidStateError('More than one host was found matching %.' % host_or_mac)
    else:
        user = request.user
        host = host[0]
        hostname = host.hostname

        if not user.has_perm('api.flip_databases') and re.match(r'^db+|^ddb+', hostname, re.I):
            return JinxActionForbiddenError('Only operations may flip database hosts!!!')
    
        if host.has_ipmi():
            return host.ipmi_power_cycle()
        else:
            return host.power_cycle()

def power_off(request, host_or_mac):
    """ Issues a power-off request to a hosts PDU or IPMI controller.

    Arguments:
        hostname_or_mac -- The hostname or mac address of an entity.

    Exceptions Raised:
        JinxDataNotFoundError -- Could not find the host_or_mac in Jinx Database.
        JinxInvalidStateError -- More than one host was found matching host_or_mac.
        JinxActionForbiddenError -- Only users within the operations group may flip databases.

    """    
    host = get_host_or_mac_object(request, host_or_mac)

    if not host:
        return JinxDataNotFoundError('Could not find %s in the Jinx Database.' % host_or_mac)
    elif len(host) > 1:
        return JinxInvalidStateError('More than one host was found matching %.' % host_or_mac)
    else:
        user = request.user
        host = host[0]
        hostname = host.hostname

        if not user.has_perm('api.flip_databases') and re.match(r'^db+|^ddb+', hostname, re.I):
            return JinxActionForbiddenError('Only operations may flip database hosts!!!')

        if host.has_ipmi():
            return host.ipmi_power_off()
        else:
            return host.power_off()

def power_on(request, host_or_mac):
    """ Issues a power-on request to a hosts PDU or IPMI controller.

    Arguments:
        hostname_or_mac -- The hostname or mac address of an entity.

    Exceptions Raised:
        JinxDataNotFoundError -- Could not find the host_or_mac in Jinx Database.
        JinxInvalidStateError -- More than one host was found matching host_or_mac.
        JinxActionForbiddenError -- Only users within the operations group may flip databases.

    """
    host = get_host_or_mac_object(request, host_or_mac)

    if not host:
        return JinxDataNotFoundError('Could not find %s in the Jinx Database.' % host_or_mac)
    elif len(host) > 1:
        return JinxInvalidStateError('More than one host was found matching %.' % host_or_mac)
    else:
        user = request.user
        host = host[0]
        hostname = host.hostname

        if not user.has_perm('api.flip_databases') and re.match(r'^db+|^ddb+', hostname, re.I):
            return JinxActionForbiddenError('Only operations may flip database hosts!!!')
    
        if host.has_ipmi():
            return host.ipmi_power_on()
        else:
            return host.power_on()

def power_status(request, host_or_mac):
    """ Issues a power_status request to IPMI enabled hosts.

    Arguments:
        hostname_or_mac -- The hostname or mac address of an entity.

    Exceptions Raised:
        JinxDataNotFoundError -- Could not find the host_or_mac in Jinx Database.
        JinxInvalidStateError -- More than one host was found matching host_or_mac.
        JinxActionForbiddenError -- Only users within the operations group may flip databases.
        JinxInvalidStateError -- host_or_mac is not IPMI enabled. Power Status not available.
    """
    host = get_host_or_mac_object(request, host_or_mac)

    if not host:
        return JinxDataNotFoundError('Could not find %s in the Jinx Database.' % host_or_mac)
    elif len(host) > 1:
        return JinxInvalidStateError('More than one host was found matching %.' % host_or_mac)
    else:
        user = request.user
        host = host[0]
        hostname = host.hostname

        if not user.has_perm('api.flip_databases') and re.match(r'^db+|^ddb+', hostname, re.I):
            return JinxActionForbiddenError('Only operations may flip database hosts!!!')

        if host.has_ipmi():
            return host.ipmi_power_status()
        else:
            return JinxInvalidStateError('%s is not IPMI enabled. Power status is not available...' % hostname)

    


    
        
