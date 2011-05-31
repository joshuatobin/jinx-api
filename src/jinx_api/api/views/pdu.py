import clusto
import llclusto
import os
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
import netsnmp
import string
import sys
import commands
import time

IPMI_TOOL = '/usr/bin/ipmitool -I lanplus -H %s -U ADMIN -P ADMIN %s'

def run_ipmi_cmd(hostname, action):
    """ Run impitool and return the exit code and output via
    STDOUT.
    """
    cmd_out = commands.getstatusoutput(IPMI_TOOL % (hostname, action))
    return cmd_out[0], cmd_out[1]

def ipmi_power_on(hostname):
    """Attempts to turn ipmi enabled host on. It will
    then check the status, and return 0 is the power
    is on and 1 otherwise.
    """
    ret_val, result = run_ipmi_cmd(hostname, 'power on')

    if(ret_val == 0):
        #ipmi commands take a few moments to process
        time.sleep(5)
        ret_val_on, msg = ipmi_power_status(hostname)
        if (msg == "Chassis Power is on"):
            return 0, "Chassis powered on..."
        else:
            return 1, "Error: %s" % msg
    else:
        return 1, "Error: %s" % msg

def ipmi_power_off(hostname):
    """Attempts to turn ipmi enabled host on. It will
    then check the status, and return 0 if the power
    is off and 1 otherwise.
    """
    ret_val, result =  run_ipmi_cmd(hostname, 'power off')

    if(ret_val == 0):
        #ipmi commands take a few moments to process
        time.sleep(5)
        ret_val_off, msg = ipmi_power_status(hostname)
        if (msg == "Chassis Power is off"):
            return 0, "Chassis Powered off..."
        else:
            return 1, "Error: %s" % msg
    else:
        return 1, "Error: %s" % msg

def ipmi_power_cycle(hostname):
    """Performs and power cycle command via IPMI.
    This can potentially put the filesystem in a
    bad state, but since we are in the business of
    reusable hosts, power cycling fits our needs.
    After the power cycle we will wait for a
    sign of reboot(namely that the chassis is
    powered on). If after 30 seconds the chassis
    is still powered off, force a power on command.
    If that fails, give up and cry.
    """
    ret_val, result = run_ipmi_cmd(hostname, 'power cycle')

    if(ret_val == 0):
        #ipmi commands take a few moments to process
        time.sleep(5)
        if (wait_for_reboot(hostname) != 0):
            ret_val_on, msg = ipmi_power_on(hostname)
            if ret_val_on != 0:
                return 1, "Unable to power cycle host"
            return 0, "Power cycle successful"
        return 0, "Power cycle successful"
    else:
        return 1, "Error: %s:" % msg

def ipmi_power_status(hostname):
    """Checks the power status of a ipmi enabled hosts
    and returns the status as a string
    """
    ret_val, result = run_ipmi_cmd(hostname, 'power status')        
    return ret_val, result

def wait_for_reboot(hostname, wait_time=15):
    """ Waits for ipmi enabled host to be turned on. Accepts the
    ipmi hostname and the wait time in seconds(defaults to 15).
    Returns 0 if chassis is on before the wait time is up.
    Otherwise returns 1 meaning the chassis is still off.
    """
    #measured in seconds
    while (wait_time > 0):
        ret, result = ipmi_power_status(hostname)
        if (result == "Chassis Power is on"):
            wait_time = 0
            ret_val = 0
        else:
            time.sleep(5)
            wait_time -= 5
            ret_val = 1
    return ret_val

def get_pdu_hostnames(request):
    """Returns a list of hostnames for all hosts with a driver of LindenPDU.
    """

    pdus = clusto.get_entities(clusto_drivers=[llclusto.drivers.LindenPDU])
    
    return [pdu.hostname for pdu in pdus if pdu.hostname.lower() != 'missing']

def power_reboot(request, host_or_mac):
    """
    """
    power_mgmt_info = get_host_power_management_info(request, host_or_mac)

    if isinstance(power_mgmt_info, HttpResponse):
        return power_mgmt_info

    if not power_mgmt_info:
        return "Could not find power management information in Jinx for:  %s" % host_or_mac

    if len(power_mgmt_info) == 1: 
        if 'ipmi' in power_mgmt_info[0].keys():
            return ipmi_power_cycle(power_mgmt_info[0]['ipmi'])[1]
        elif 'pdu' in power_mgmt_info[0].keys():
            try:
                port_oid = '318.1.1.4.4.2.1.3.%s' % power_mgmt_info[0]['port']
                oid = netsnmp.Varbind('.1.3.6.1.4.1', port_oid, '3', 'INTEGER')
                netsnmp.snmpset(oid, Version = 1, DestHost=power_mgmt_info[0]['pdu'], Community='private')
                return "%s: power cycled..." % host_or_mac
            except KeyError, e:
                return str(e)

    elif len(power_mgmt_info) == 2: 
        try:
            for pdu_info in power_mgmt_info:
                port_oid = '318.1.1.4.4.2.1.3.%s' % pdu_info['port']
                oid = netsnmp.Varbind('.1.3.6.1.4.1', port_oid, '2', 'INTEGER')
                netsnmp.snmpset(oid, Version = 1, DestHost=pdu_info['pdu'], Community='private')
            
            time.sleep(3)
            for pdu_info in power_mgmt_info:
                port_oid = '318.1.1.4.4.2.1.3.%s' % pdu_info['port']
                oid = netsnmp.Varbind('.1.3.6.1.4.1', port_oid, '1', 'INTEGER')
                netsnmp.snmpset(oid, Version = 1, DestHost=pdu_info['pdu'], Community='private')
        except KeyError, e:
            return str(e)
        return "%s: power cycled..." % host_or_mac
    else:
        return "Power management information is malformed: %s" % power_mgmt_info

def power_off(request, host_or_mac):
    """
    """
    power_mgmt_info = get_host_power_management_info(request, host_or_mac)

    if isinstance(power_mgmt_info, HttpResponse):
        return power_mgmt_info

    if not power_mgmt_info:
        return "Could not find power management information in Jinx for:  %s" % host_or_mac

    if len(power_mgmt_info) == 1: 
        if 'ipmi' in power_mgmt_info[0].keys():
            return ipmi_power_off(power_mgmt_info[0]['ipmi'])[1]
        elif 'pdu' in power_mgmt_info[0].keys():
            try:
                port_oid = '318.1.1.4.4.2.1.3.%s' % power_mgmt_info[0]['port']
                oid = netsnmp.Varbind('.1.3.6.1.4.1', port_oid, '2', 'INTEGER')
                netsnmp.snmpset(oid, Version = 1, DestHost=power_mgmt_info[0]['pdu'], Community='private')
                return "%s: powered off..." % host_or_mac
            except KeyError, e:
                return str(e)

    elif len(power_mgmt_info) == 2: 
        for pdu_info in power_mgmt_info:
            try:
                port_oid = '318.1.1.4.4.2.1.3.%s' % pdu_info['port']
                oid = netsnmp.Varbind('.1.3.6.1.4.1', port_oid, '2', 'INTEGER')
                netsnmp.snmpset(oid, Version = 1, DestHost=pdu_info['pdu'], Community='private')
            except KeyError, e:
                return str(e)
        return "%s: powered off..." % host_or_mac
    else:
        return "Power management information is malformed: %s" % power_mgmt_info

def power_on(request, host_or_mac):
    """ Powers on a host
    """

    power_mgmt_info = get_host_power_management_info(request, host_or_mac)

    if isinstance(power_mgmt_info, HttpResponse):
        return power_mgmt_info

    if not power_mgmt_info:
        return "Could not find power management information in Jinx for:  %s" % host_or_mac

    if len(power_mgmt_info) == 1: 
        if 'ipmi' in power_mgmt_info[0].keys():
            return ipmi_power_on(power_mgmt_info[0]['ipmi'])[1]
        else:
            try:
                port_oid = '318.1.1.4.4.2.1.3.%s' % power_mgmt_info[0]['port']
                oid = netsnmp.Varbind('.1.3.6.1.4.1', port_oid, '1', 'INTEGER')
                netsnmp.snmpset(oid, Version = 1, DestHost=power_mgmt_info[0]['pdu'], Community='private')
                return "%s: powered on..." % host_or_mac
            except KeyError, e:
                return str(e)
   
    elif len(power_mgmt_info) == 2: 
        for pdu_info in power_mgmt_info:
            try:
                port_oid = '318.1.1.4.4.2.1.3.%s' % pdu_info['port']
                oid = netsnmp.Varbind('.1.3.6.1.4.1', port_oid, '1', 'INTEGER')
                netsnmp.snmpset(oid, Version = 1, DestHost=pdu_info['pdu'], Community='private')
            except KeyError, e:
                return str(e)
        return "%s: powered on..." % host_or_mac
    else:
        return "Power management information is malformed: %s" % power_mgmt_info

def power_status(request, host_or_mac):
    """
    """

    power_mgmt_info = get_host_power_management_info(request, host_or_mac)

    if isinstance(power_mgmt_info, HttpResponse):
        return power_mgmt_info

    if not power_mgmt_info:
        return "Could not find power management information in Jinx for:  %s" % host_or_mac

    if len(power_mgmt_info) == 1: 
        if 'ipmi' in power_mgmt_info[0].keys():
            return ipmi_power_status(power_mgmt_info[0]['ipmi'])[1]
        else:
            return "%s: is not IPMI Enabled." % host_or_mac
    else:
        return "%s: is not IPMI Enabled." % host_or_mac

def get_host_power_management_info(request, hostname_or_mac):
    """ Returns a hosts PDU or IPMI power management infomation.

    Arguments:
        hostname_or_mac -- The hostname or mac address of an entity to return power management information.

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
        host = hosts[0]

    pdu_connections = []
    port_info = host.port_info

    try:
        if host.attrs(subkey='ipmi_hostname'):
            pdu_connections.append({'ipmi': host.ipmi[0] })
            return pdu_connections
        elif 'pwr-nema-5' in host.port_info:
            for port_num in port_info['pwr-nema-5']:
                pdu_connections.append({'pdu': port_info['pwr-nema-5'][port_num]['connection'].hostname,
                                        'port': port_info['pwr-nema-5'][port_num]['otherportnum']})
            return pdu_connections
        else:
            return pdu_connections

    except (KeyError, AttributeError, IndexError):
        pdu_connections = []
    


    
        
