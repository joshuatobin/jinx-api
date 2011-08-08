import clusto
import llclusto
from llclusto.drivers.dns import DNSRecord, DNSService
from clusto.exceptions import *
from exceptions import *
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from host import _get_host_instance, _get_device_info
from jinx_api.http import HttpResponseInvalidState

def _get_dns_service_group_instance(response, service_group):
    """ Returns a service group instance """
    try:
        service_group = clusto.get_by_name(service_group)
    except LookupError:
        return HttpResponseInvalidState("DNS service group: %s not found." % service_group)
    else:
        return service_group

def _get_dns_hostname_instance(response, dns_hostname):
    """ Returns a dns hostname instance """
    try:
        dns_hostname = clusto.get_by_name(dns_hostname)
    except LookupError:
        return HttpResponseInvalidState("DNS hostname: %s not found." % dns_hostname)
    else:
        return dns_hostname

def add_dns_record_comment(response, dns_hostname, comment):
    """ Adds a comment to a dns record. If the dns record dose not exist we create one.

    Arguments:
        dns_hostname -- The dns hostname of a record.
        comment      -- Comment

    """
    try:
        dns_record = clusto.get_by_name(dns_hostname)
    except LookupError:
        dns_record = DNSRecord(dns_hostname)
        dns_record.comment = comment
        return 'DNS record and comment added: %s: %s.' % (dns_hostname, comment)
    else:
        dns_record.comment = comment        
        return 'DNS comment added: %s.' % comment

def get_dns_hostname_record_comment(response, dns_hostname):
    """ Get the comment from a dns hostname record.

    Arguments:
        dns_hostname -- The dns hostname of a record.
    """
    host = _get_dns_hostname_instance(response, dns_hostname)
    
    if isinstance(host, HttpResponse):
        return host

    comment = str(host.comment)

    return comment
        
def create_dns_service_group(response, service_group, comment):
    """Create a dns service group to logically group dns records.

    Arguments:
         service_group -- The service group name.
         comment       -- A comment about the service group.

    Exceptions Raised:
         JinxInvalidStateError -- The requested service_group name already exists.
    """

    try:
        pool = clusto.get_by_name(service_group)
    except LookupError:
        pool = DNSService(service_group)
        pool.comment = comment
        return 'DNS service and comment added: %s: %s.' % (service_group, comment)
    else:
        pool.comment = comment
        return 'DNS service added: %s.' % comment

def delete_dns_service_group(response, service_group):
    """ Deletes a DNS service group. The service group must not contain any records.

    Arguments:
         service_group -- The service group name.

    Exceptions Raised:
         JinxInvalidStateError -- The requested service_group contains records.
    """

    pool = _get_dns_service_group_instance(response, service_group)
    
    if isinstance(pool, HttpResponse):
        return pool

    if len(pool.contents()) != 0:
        return HttpResponseInvalidState("Error: DNS Service group: %s contains %d dns records.\
                                        Remove dns records before deleting the service group." % \
                                        (service_group, len(pool.contents())))
    else:
        clusto.delete_entity(pool.entity)
        return "Successfully deleted service group: %s." % service_group

def add_dns_service_group(response, dns_hostname, service_group):
    """Adds a dns host record to a dns service group.

    Arguments:
         dns_hostname -- The dns hostname of a record.
         service_group -- The service group name.

    Exceptions Raised:
         JinxInvalidStateError -- The dns_hostname already exists in service_group.
    """

    pool = _get_dns_service_group_instance(response, service_group)
        
    if isinstance(pool, HttpResponse):
        return pool

    try:
        dns_record = clusto.get_by_name(dns_hostname)
    except LookupError:
        dns_record = DNSRecord(dns_hostname)

    try:
        pool.insert(dns_record)
    except PoolException:
        return HttpResponseInvalidState("DNS host record: %s already exists in service group: %s."\
                                        % (dns_record.name, service_group))
    else:
        return "DNS host record: %s successfully added to: %s service group." % (dns_record.name, service_group)
    
def remove_dns_service_group(response, dns_hostname, service_group):
    """Removes a dns host record from service group.

    Arguments:
         dns_hostname -- The dns hostname of a record.
         service_group -- The service group name.

    Exceptions Raised:
         JinxInvalidStateError -- The dns_hostname was unsuccessfully removed from the pool.
    """
    dns_record = _get_dns_hostname_instance(response, dns_hostname)
    
    pool = _get_dns_service_group_instance(response, service_group)

    if isinstance(dns_record, HttpResponse):
        return dns_record

    if isinstance(pool, HttpResponse):
        return pool

    if dns_record in pool:
        pool.remove(dns_record)
        if not dns_record in pool:
            return "Successfully removed: %s from dns service group: %s." % (dns_record.name, pool.name)
        else: # We shouldn't ever get here.
            return HttpResponseInvalidState("Error: DNS record: %s unsuccessfully removed from pool: %s."\
                                            % (dns_record.name, pool.name))
    else:
        return HttpResponseInvalidState("%s not found in dns service group: %s." % (dns_record.name, pool.name))

def get_dns_record_service_groups(response, dns_hostname):
    """ Returns a list of service groups a dns hostname belongs to.

    Arguments:
         dns_hostname -- The dns_hostname of a record.
    """

    dns_record = _get_dns_hostname_instance(response, dns_hostname)

    if isinstance(dns_record, HttpResponse):
        return dns_record

    groups = dns_record.parents(clusto_types=['pool'], clusto_drivers=['dnsservice'])

    return [x.name for x in groups]
    
def get_all_dns_service_groups(response):
    """ Returns a list of all DNS services groups.    
    """

    groups = clusto.get_entities(clusto_types=['pool'], clusto_drivers=['dnsservice'])

    return [x.name for x in groups]

def get_dns_service_group_info(response, service_group):
    """Returns a list of all memebers in a DNS Service group.

    Arguments:
         service_group -- The service group name.
    """

    pool = _get_dns_service_group_instance(response, service_group)

    if isinstance(pool, HttpResponse):
        return pool

    info = {}

    members = [x.name for x in pool.contents()]

    info['description'] = str(pool.comment)
    info['members'] = members
    
    return info
