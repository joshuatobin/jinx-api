import clusto
import llclusto
from clusto.exceptions import *
from exceptions import *
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from host import _get_host_instance, _get_device_info
from jinx_api.http import HttpResponseInvalidState
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from jinx_api.api.models import DNSRecord, DNSService
from jinx_client.jinx_exceptions import JinxInvalidRequestError, JinxDataNotFoundError

def _get_dns_service_group_instance(response, service_group):
    """ Returns a service group instance """
    try:
        service = DNSService.objects.get(name=service_group)
    except ObjectDoesNotExist:
        raise JinxInvalidRequestError("DNS service group: %s not found." % service_group)
    else:
        return service

def _get_dns_hostname_instance(response, dns_record):
    """ Returns a dns hostname instance """
    try:
        record = DNSRecord.objects.get(name=dns_record)
    except ObjectDoesNotExist:
        raise JinxInvalidRequestError("DNS record: %s not found." % dns_record)
    else:
        return record

def get_dns_records_comments(response, list_of_records):
    """Returns a dictionary of dns record comments.

    Arguments:
        list_of_records -- A list of dns hostname records.
    """

    if type(list_of_records) != list:
        raise JinxInvalidRequestError("Error: Please provide a list of records")
 
    comments = {}

    for record in list_of_records:
        try:
            dns_record = DNSRecord.objects.get(name=record)
        except ObjectDoesNotExist:
            continue

        if dns_record.comment:
                 comments[dns_record.name] = dns_record.comment

    return comments

def get_dns_records_service_groups(response, list_of_records):
    """Returns a dictionary containing the service groups a record belongs to
    along with the comment for the service group

    Arguments:
        list_of_records -- A list of dns hostname records.

    """

    if type(list_of_records) != list:
        raise JinxInvalidRequestError("Error: Please provide a list of records")

    info = {}

    for record in list_of_records:
        try:
            dns_record = DNSRecord.objects.get(name=record)

            if dns_record.group:
                if dns_record.group.name not in info:
                    info[dns_record.group.name] = {}
                    info[dns_record.group.name]['members'] = [x.name for x in dns_record.group.dnsrecord_set.all()]
                    info[dns_record.group.name]['description'] = dns_record.group.comment

        except ObjectDoesNotExist:
            continue

    return info

def get_dns_record_comment(response, dns_hostname):
    """ Get the comment from a dns hostname record.

    Arguments:
        dns_hostname -- The dns hostname of a record.
    """
    host = _get_dns_hostname_instance(response, dns_hostname)

    return host.comment

def set_dns_record_comment(response, dns_record, comment):
    """ Adds a comment to a dns record. If the dns record dose not exist we create one.

    Arguments:
        dns_hostname -- The dns hostname of a record.
        comment      -- Comment
    """
    try:
        DNSRecord(name=dns_record, comment=comment).save()
        return True
    except IntegrityError:
        record = DNSRecord.objects.get(name=dns_record)
        record.comment = comment
        record.save()

        return True

def create_dns_service_group(response, service_group, comment):
    """Create a dns service group to logically group dns records.

    Arguments:
         service_group -- The service group name.
         comment       -- A comment about the service group.
    """
    try:
        DNSService(name=service_group, comment=comment).save()
        return True
    except IntegrityError:
        return JinxInvalidRequestError("Error: service group %s already exists" % service_group)

def set_dns_service_group(response, dns_record, service_group):
    """Sets the service group to which a record belongs.
    If passed a group name of None, remove the record from any group it is a member of. 

    Arguments:
         dns_hostname -- The dns hostname of a record.
         service_group -- The service group name.

    """
    if service_group:
        group = _get_dns_service_group_instance(response, service_group)
    else:
        group = None

    try:
        record = DNSRecord.objects.get(name=dns_record)
    except ObjectDoesNotExist:
        record = DNSRecord(name=dns_record)

    record.group = group
    record.save()

    return True


