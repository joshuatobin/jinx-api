import clusto
import datetime
import llclusto
from clusto.exceptions import *
from llclusto.drivers import LogEvent, LogEventType
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from jinx_api.http import HttpResponseInvalidState


def add_log_event(request, hostname, user, event_type, description=None, **kwargs):
    """Adds a new log event.

    Returns:
        None

    Arguments:
        hostname -- the hostname associated with the log event.
        user -- the user who triggered the event.
        event_type -- the name of the event type.
        description -- a string describing what happened(optional).

    Exceptions Raised:
        JinxDataNotFoundError -- the hostname or the event_type could not be found
        JinxInvalidStateError -- more than one host was found matching the hostname

    """
    if event_type:
        try:
            event_type = clusto.get_by_name(event_type)
        except LookupError, e:
            return HttpResponseNotFound("Event type '%s' does not exist" % event_type)

    source_entity = llclusto.get_by_hostname(hostname)
    if len(source_entity) < 1:
        return HttpResponseNotFound("No entity found for '%s'" % hostname)
    elif len(source_entity) > 1:
        return HttpResponseInvalidState("Multiple entities found for  '%s'" % hostname)

    source_entity[0].add_log_event(user=user,
                                   event_type=event_type,
                                   timestamp=datetime.datetime.utcnow(),
                                   description=description,
                                   **kwargs)


def add_log_event_type(request, event_type, description=None):
    """Adds a new log event type.
    
    Returns:
        None
    
    Arguments:
    event_type -- the name of the event type.
    description -- a string describing the event type.

    Exceptions Raised:
        JinxInvalidStateError -- event_type already exists

    """
    try:
        l = LogEventType(event_type)
    except NameException:
        return HttpResponseInvalidState("Event type '%s' already exists" % event_type)
    if description:
        l.description = description


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

    Exceptions Raised:
        JinxDataNotFoundError -- the hostname or the event_type could not be found
        JinxInvalidStateError -- more than one host was found matching the hostname

    """
    log_events = []
    host = None

    if hostname:
        host = llclusto.get_by_hostname(hostname)
        if len(host) < 1:
            return HttpResponseNotFound("No entity found for '%s'" % hostname)
        elif len(host) > 1:
            return HttpResponseInvalidState("Multiple entities found for  '%s'" % hostname)
        else:
            host = host[0]

    if event_type:
        try:
            event_type = clusto.get_by_name(event_type)
        except LookupError, e:
            return HttpResponseNotFound("Event type '%s' does not exist" % event_type)

    levents = LogEvent.get_log_events(source_entity = host,
                                      user=user,
                                      event_type=event_type,
                                      start_timestamp=start_timestamp,
                                      end_timestamp=end_timestamp)
    if len(levents) < 1:
        return []

    for levent in levents:
        if not levent.source_entity:
            event_hostname = None
        else:
            event_hostname = levent.source_entity.hostname

        log_event = {"name" : levent.name,
                     "hostname" : event_hostname,
                     "event_type" : levent.event_type.name,
                     "user" : levent.user,
                     "timestamp" : levent.timestamp,
                     "description" : levent.description}

        for eattr in levent.attrs(subkey="_extra"):
            log_event[eattr.key] = eattr.value
        log_events.append(log_event)

    return log_events


def list_log_event_types(request):
    """Returns a dictionary of log event types

    Returns:
        A dictionary keyed on the log event
        type name and valued on the description.
    
    Arguments:
        None

    """
    event_types = clusto.get_entities(clusto_types=["logeventtype"])
    return dict((event_type.name,event_type.description) for event_type in event_types)
