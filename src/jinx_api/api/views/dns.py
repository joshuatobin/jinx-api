import clusto
import llclusto
#from llclusto.drivers.dns import DNSRecord, DNSService
from clusto.exceptions import *
from exceptions import *
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from host import _get_host_instance, _get_device_info
from jinx_api.http import HttpResponseInvalidState
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from jinx_api.api.models import DNSRecord, DNSService


def _get_dns_service_group_instance(response, service_group):
    """ Returns a service group instance """
    try:
        service = DNSService.objects.get(name=service_group)
    except ObjectDoesNotExist:
        return HttpResponseInvalidState("DNS service group: %s not found." % service_group)
    else:
        return service

def _get_dns_hostname_instance(response, dns_record):
    """ Returns a dns hostname instance """
    try:
        record = DNSRecord.objects.get(name=dns_record)
    except ObjectDoesNotExist:
        return HttpResponseInvalidState("DNS record: %s not found." % dns_record)
    else:
        return record

def add_dns_record_comment(response, dns_record, comment):
    """ Adds a comment to a dns record. If the dns record dose not exist we create one.

    Arguments:
        dns_hostname -- The dns hostname of a record.
        comment      -- Comment

    """
    try:
        DNSRecord(name=dns_record, comment=comment).save()
        return "DNS record and comment added: %s: %s." % (dns_record, comment)
    except IntegrityError:
        record = DNSRecord.objects.get(name=dns_record)
        record.comment = comment
        record.save()
        return "DNS comment added: %s." % comment
        
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
        service = DNSService(name=service_group, comment=comment).save()
        return 'DNS service and comment added: %s: %s.' % (service_group, comment)
    except IntegrityError:
        service = DNSService.objects.get(name=service_group)    
        service.comment = comment
        service.save()
        return 'DNS service added: %s.' % comment
    
def delete_dns_service_group(response, service_group):
    """ Deletes a DNS service group. The service group must not contain any records.

    Arguments:
         service_group -- The service group name.

    Exceptions Raised:
         JinxInvalidStateError -- The requested service_group contains records.
    """

    group  = _get_dns_service_group_instance(response, service_group)
    
    if isinstance(group, HttpResponse):
        return group

    members = [x.name for x in group.dnsrecord_set.all()]

    if members:
        return HttpResponseInvalidState("Error: remove records before attempting to delete service groups")
    else:
        group.delete()

        return "Successfully deleted service group: %s." % service_group

def add_dns_service_group(response, dns_record, service_group):
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
        record = DNSRecord.objects.get(name=dns_record)
    except ObjectDoesNotExist:
        record = DNSRecord(name=dns_record)

    record.group = pool
    record.save()

    return "DNS host record: %s successfully added to: %s service group." % (dns_record, service_group)

        
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

    if dns_record.group:
        if hasattr(dns_record.group, 'name'):
            if dns_record.group.name == pool.name:
                dns_record.group = None
                dns_record.save()
                return "Successfully removed: %s from dns service group: %s." % (dns_record.name, pool.name)
        else:
            return HttpResponseInvalidState("%s not found in dns service group: %s." % (dns_record.name, pool.name))

    return HttpResponseInvalidState("%s not found in dns service group: %s." % (dns_record.name, pool.name))
    
def get_dns_record_service_groups(response, dns_record):
    """ Returns a list of service groups a dns hostname belongs to.

    Arguments:
         dns_hostname -- The dns_hostname of a record.
    """

    record = _get_dns_hostname_instance(response, dns_record)

    if isinstance(record, HttpResponse):
        return record

    if record.group:
        return [str(record.group.name)]
    
def get_all_dns_service_groups(response):
    """ Returns a list of all DNS services groups.    
    """
    return [x.name for x in DNSService.objects.all()]

def get_dns_service_group_info(response, service_group):
    """Returns a dictionary of all memebers in a DNS Service group.

    Arguments:
         service_group -- The service group name.
    """

    pool = _get_dns_service_group_instance(response, service_group)

    if isinstance(pool, HttpResponse):
        return pool

    info = {}

    members = [x.name for x in pool.dnsrecord_set.all()]

    info['description'] = str(pool.comment)
    info['members'] = members
    
    return info

def get_dns_records_comments(response, list_of_records):
    """Returns a dictionary of dns record comments.

    Arguments:
        list_of_records -- A list of dns hostname records.

    Exceptions Raised:
        JinxInvalidRequestError - The list_of_records is not of the type list.
    """

    if type(list_of_records) != list:
        raise HttpResponseBadRequest("Error: Please provide a list of records")

    comments = {}

    for record in list_of_records:
        try:
            dns_record = DNSRecord.objects.get(name=record)
        except ObjectDoesNotExist:
            continue

        if dns_record.comment:
                 comments[dns_record.name] = dns_record.comment

    return comments
    
def get_dns_service_group_members_info(response, list_of_records):
    """Returns a dictionary containing the service groups a record belongs to
    along with the comment for the service group

    Arguments:
        list_of_records -- A list of dns hostname records.

    Exceptions Raised:
        JinxInvalidRequestError - The list_of_records is not of the type list.
    """

    if type(list_of_records) != list:
        raise HttpResponseBadRequest("Error: Please provide a list of records")

    info = {}

    for record in list_of_records:
        try:
            dns_record = DNSRecord.objects.get(name=str(record))

            if dns_record.group:

                group = DNSService.objects.get(name=dns_record.group.name)

                info[dns_record.group.name] = {}
                info[dns_record.group.name]['members'] = [x.name for x in group.dnsrecord_set.all()]
                info[dns_record.group.name]['description'] = str(group.comment)

        except ObjectDoesNotExist:
            continue
            

    return info
