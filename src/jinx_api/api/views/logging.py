import clusto
import datetime
import llclusto
from clusto.exceptions import *
from llclusto.drivers import LogEvent, LogEventType
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from jinx_api.http import HttpResponseInvalidState


def add_log_event(request, hostname, user, event_type, description=None):
    """Adds a new log event.

    Returns:
        None

    Arguments:
        hostname -- the hostname associated with the log event.
        user -- the user who triggered the event.
        event_type -- the name of the event type.
        description -- a string describing what happened(optional).

    """
    try:
        event_type = clusto.get_by_name(event_type)
    except LookupError, e:
        return HttpResponseBadRequest(str(e))

    source_entity = llclusto.get_by_hostname(hostname)
    if len(source_entity) < 1:
        return HttpResponseNotFound("No entity found for %s" % hostname)
    elif len(source_entity) > 1:
        return HttpResponseInvalidState("Multiple entities found for  %s" % hostname)

    try:
        source_entity[0].add_log_event(user=user,
                                       event_type=event_type,
                                       timestamp=datetime.datetime.utcnow(),
                                       description=description)
    except TypeError, e:
        return HttpResponseBadRequest(str(e))



def add_log_event_type(request, event_type, description=None):
    """Adds a new log event type.
    
    Returns:
        None
    
    Arguments:
    event_type -- the name of the event type.
    descrption -- a string describing the event type.
    """
    try:
        l = LogEventType(event_type)
    except (TypeError, NameException), e:
        return HttpResponseBadRequest(str(e))
    if description:
        l.description = description


def get_log_events_by_user(request, user):
    """Returns a list of log events triggered by a user.

    Returns:
        A list of dictionaries, where each dictionary is a log event
        matching the user.

    Arguments:
        user -- the user who triggered the event.

    """
    return get_log_events(request, user=user)


def get_log_events_by_hostname(request, hostname):
    """Returns a list of log events associated with a hostname
    
    Returns:
        A list of dictionaries, where each dictionary is a log event
        matching the hostname.

    Arguments:
        hostname -- the hostname associated with the log event.

    """
    return get_log_events(request, hostname=hostname)


def get_log_events_by_type(request, event_type):
    """Returns a list of log events matching the log event type

    Returns:
        A list of dictionaries, where each dictionary is a log event
        matching the event type.

    Arguments:
        event_type -- the name of the event type.

    """
    return get_log_events(request, event_type=event_type)


def get_log_events_by_time(request, start_timestamp, end_timestamp):
    """Returns a list of log events the occured in a time range.

    Returns:
       A list of dictionaries, where each dictionary is a log event
       occuring between a start time and/or an end time.
    
    Arguments:
       start_timestamp -- the beginning datetime timestamp. All 
       found log events will have a timestamp after this datetime.
       end_timestamp -- the end datetime timestamp. All found log event 
       will have a timestamp before this datetime

    """
    return get_log_events(request, start_timestamp, end_timestamp)


def get_log_events(request, hostname=None, user=None,
                   event_type=None, start_timestamp=None, 
                   end_timestamp=None):
    """Returns a list of log events based on a number of parameters.

    Returns:
        A list of dictionaries, where each dictionary is a log event
        matching all of the parameters passed in.

    Arguments:
        hostname -- the hostname associated with the log event.
        user -- the user who triggered the event.
        event_type -- the name of the event type.
        start_timestamp -- the beginning datetime timestamp. All
        found log events will have a timestamp after this datetime.
        end_timestamp -- the end datetime timestamp. All found log event
        will have a timestamp before this datetime

    """
    log_events = []
    host = None

    if hostname:
        host = llclusto.get_by_hostname(hostname)
        if len(host) < 1:
            return HttpResponseNotFound("No entity found for %s" % hostname)
        elif len(host) > 1:
            return HttpResponseInvalidState("Multiple entities found for  %s" % hostname)
        else:
            host = host[0]

    if event_type:
        try:
            event_type = clusto.get_by_name(event_type)
        except LookupError, e:
            return HttpResponseBadRequest(str(e))

    levents = LogEvent.get_log_events(source_entity = host,
                                      user=user,
                                      event_type=event_type,
                                      start_timestamp=start_timestamp,
                                      end_timestamp=end_timestamp)
    if len(levents) < 1:
        return []

    for levent in levents:
        log_event = {"name" : levent.name,
                     "hostname" : hostname,
                     "event_type" : levent.event_type.name,
                     "user" : levent.user,
                     "timestamp" : str(levent.timestamp),
                     "description" : levent.description}
        for eattr in levent.attrs(subkey="_extra"):
            log_event[eattr.key] = eattr.value
        log_events.append(log_event)

    return log_events


def list_log_event_types(request):
    """Returns a list of log events as dictionaries

    Returns:
        A list of dictionaries. Each dictionary is an event type 
        with keys of 'name' and 'description'.
    
    Arguments:
        None

    """
    event_types = clusto.get_entities(clusto_types=["logeventtype"])
    return [{"name":event_type.name, "description": event_type.description} for event_type in event_types]
