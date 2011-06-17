import clusto
import llclusto
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from jinx_api.http import HttpResponseInvalidState
import traceback

def _get_host_instance(request, hostname_or_mac):
    """
    Function that returns an instance from either a hostname or mac address.

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
        return HttpResponseInvalidState('More than one host found with hostname or MAC address "%s".' % hostname_or_mac)
    else:
        host = hosts[0]
    
    return host

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
    host = _get_host_instance(request, hostname_or_mac)

    if isinstance(host, HttpResponse):
        return host

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
            if port_info['pwr-nema-5'][port_num]['connection']:
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
    
def get_host_state(request, hostname):
    """Gets the state of a host.
    
    Returns:
        The host's state, as a string.  If the host has no state set, returns None.
        
    Arguments:
        hostname -- The name of the host whose state will be retrieved.
        
    Exceptions Raised:
        JinxDataNotFoundError -- A host with the specified hostname was not found.
    """
    
    try:
        host = llclusto.get_by_hostname(hostname)[0]
        return host.state
    except IndexError:
        return HttpResponseNotFound("Host %s not found." % hostname)
    
def set_host_state(request, hostname, state):
    """Sets the state of a host.  
    
    Returns:
        None
        
    Arguments:
        hostname -- The name of the host whose state will be retrieved.
        state -- The state to set which to set the host.  This state must already exist (see list_states()).
    
    Exceptions Raised:
        JinxDataNotFoundError -- A host with the specified hostname was not found.
        JinxInvalidStateError -- The specified state does not exist.  Please see list_states() for a list of valid states.
    """
    
    try:
        host = llclusto.get_by_hostname(hostname)[0]
        
        # Fetch the "State Change" LogEventType
        state_change = llclusto.get_by_name("State Change")
        old_state = host.state
        
        clusto.begin_transaction()
        
        if state is None:
            del host.state
        else:
            host.state = state
            
        host.add_log_event(user=???, event_type=state_change, old_state=old_state, new_state=state)
        
        clusto.commit()
    except Exception, e:
        try:
            clusto.rollback_transaction()
        except clusto.exceptions.TransactionException:
            # Just means that the exception happened before the clusto.begin_transaction() call.
            pass
    
        if isinstance(e, IndexError):
            return HttpResponseNotFound("Host %s not found." % hostname)
        else if isinstance(e, ValueError:
            return HttpResponseInvalidState("State %s does not exist." % state)
    
def get_hosts_in_state(request, state):
    """Gets a list of all hosts in the specified state.
    
    Returns:
        A list of hostnames.
        
    Arguments:
        state -- The name of the state.
    
    Exceptions Raised:
        JinxInvalidStateError -- The specified state does not exist.  Please see list_states() for a list of valid states.
    """
    try:
        state = clusto.get_entities(names=[state], clusto_drivers=[llclusto.drivers.HostState])[0]
        return [host.hostname for host in state]
    except IndexError:
        return HttpResponseInvalidState("State %s does not exist." % state)
    
def list_host_states(request):
    """Gets a list of all defined host states.
    
    Returns:
        A list of host state names as strings.
    """
    
    states = clusto.get_entities(clusto_drivers=[llclusto.drivers.HostState])
    
    return [state.name for state in states]
    
def add_host_state(request, state):
    """Adds a new host state.
    
    Returns:
        None
        
    Arguments:
        state -- The name of the new state.  Only letters, numbers, spaces, and underscores are allowed.
        
    Exceptions Raised:
        JinxBadRequestError -- The name of the state is invalid.
        JinxInvalidStateError -- The specified state already exists.
    """
    
    if not re.match(r'^[a-zA-z0-9_ ]*$', state):
        return HttpResponseBadRequest("State names may only contain letters, numbers, underscores, and spaces.")
    
    try:
        llclusto.drivers.HostState(state)
        return None
    except clusto.exceptions.NameException:
        return HttpResponseInvalidState("A state named '%s' already exists." % state)


def get_server_class_info(request, hostname_or_mac):
    """
    Returns the property information pertaining to the hardware class of a server.
    
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
    
    if not isinstance(host, llclusto.drivers.LindenServer):
         return HttpResponseInvalidState("%s is not an instance of LindenServer" % host)
    
    try:
        server_class = clusto.get_by_name(host.server_class.name)
    except LookupError:
        return HttpResponseInvalidState("ServerClass not found: %s" % host.server_class.name)

    class_info = {}

    attrs = server_class.attrs()
    
    for attr in attrs:
        class_info[attr.key] = attr.value

    return class_info

    
