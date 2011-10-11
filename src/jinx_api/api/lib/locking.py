from jinx_api.api.models import Lock
from django.core.exceptions import ObjectDoesNotExist
from jinx_client.jinx_exceptions import JinxDataNotFoundError

def acquire_lock(lock):
    """
    Arguments:
        lock -- Name of lock

    Exceptions Raised:
        JinxDataNotFoundError -- Lock name not found.
    """

    try:
        l = Lock.objects.get(name=lock)
        l.value += 1
        l.save()
    except ObjectDoesNotExist:
        raise JinxDataNotFoundError("Error: Could not find lock: %s. Please use a lock that already exists." % lock)
        
    
    
