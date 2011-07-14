import clusto
import llclusto
import re
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from jinx_api.http import HttpResponseInvalidState
from llclusto.drivers import PGIImage, RevertPGIImageError

def list_servable_pgi_images(request):
    """Returns a list of servable PGI images stored on the PGI systemimagers.

    Returns:
    A list of pgi image names as strings.

    Arguments:
    None

    Exceptions Raised:
    None
    """

    servable_images = []
    
    for image in clusto.get_entities(clusto_types=[llclusto.drivers.PGIImage]):
        if len(image.get_si_servers_stored_on()) > 0:
            servable_images.append(image.name)
    
    return servable_images


def get_hosts_with_image(request, image_name):
    """Returns a list of hostnames that are associated with a particular image name.

    Returns:
    A list of hostnames as strings.
    
    Arguments:
    image_name -- a string containing the image name.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching image name.
    """

    hosts = []
    try:
        image = clusto.get_by_name(image_name)
    except LookupError:
        return HttpResponseNotFound("Image '%s' not found." % image_name)
        
    for host in image.get_hosts_associated_with():
        hosts.append(host.hostname)
        
    return hosts


def list_host_image_associations(request):
    """Returns all hostnames and associated PGI image names.

    Returns:
    A dictionary keyed on hostnames and the values are the associated image name.

    Arguments:
    None
    
    Exceptions Raised:
    None
    """

    host_images = {}
    for host in clusto.get_entities(attrs=[{'key': 'pgi_image'}]):
        host_images[host.hostname] = host.pgi_image.name

    return host_images


def get_current_pgi_image(request, hostname):
    """Returns the image assoicated with the hostname passed in.

    Returns:
    A string containing the associated image name.

    Arguments:
    hostname -- the hostname formatted as a string.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching hostname.
    JinxInvalidStateError -- more than one host was found matching the hostname.
    """

    hosts = llclusto.get_by_hostname(hostname)
    if len(hosts) < 1:
        return HttpResponseNotFound("Hostname '%s' does not exist" % hostname)
    elif len(hosts) > 1:
        return HttpResponseInvalidState("Multiple hosts found matching '%s'" % hostname)
    host = hosts[0]
    
    if host.pgi_image is None:
        return None

    return host.pgi_image.name


def get_previous_pgi_image(request, hostname):
    """Returns the image that was previously assigned to the hostname.

    Returns:
    A string containing the associated image name.
    
    Arguments:
    hostname -- the hostname formatted as a string.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching hostname.
    JinxInvalidStateError -- more than one host was found matching the hostname.
    """

    hosts = llclusto.get_by_hostname(hostname)
    if len(hosts) < 1:
        return HttpResponseNotFound("Hostname '%s' does not exist" % hostname)
    elif len(hosts) > 1:
        return HttpResponseInvalidState("Multiple hosts found matching '%s'" % hostname)
    host = hosts[0]

    if host.previous_pgi_image is None:
        return None
    else:
        return host.previous_pgi_image.name


def update_host_image_association(request, hostname, image_name):
    """Associate a host with the pgi image.
    
    Returns:
    None
    
    Arguments:
    hostname -- the hostname formatted as a string.
    image_name -- the image name formatted at a string.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching hostname or image_name.
    JinxInvalidStateError -- more than one host was found matching the hostname.
    """

    hosts = llclusto.get_by_hostname(hostname)
    if len(hosts) < 1:
        return HttpResponseNotFound("Hostname '%s' does not exist" % hostname)
    elif len(hosts) > 1:
        return HttpResponseInvalidState("Multiple hosts found matching '%s'" % hostname)
    host = hosts[0]

    try:
        image = clusto.get_by_name(image_name)
    except LookupError:
        return HttpResponseNotFound("Image '%s' does not exist." % image_name)
        
    host.pgi_image = image
    
    return 


def rollback_host_image(request, hostname):
    """Rollback image association to previous pgi image.

    Returns:
    None
    
    Arguments:
    hostname -- the hostname formatted as a string.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching hostname.
    JinxInvalidStateError -- more than one host was found matching the hostname.
                          -- no image was previously associated with this host.
    """

    hosts = llclusto.get_by_hostname(hostname)
    if len(hosts) < 1:
        return HttpResponseNotFound("Hostname '%s' does not exist" % hostname)
    elif len(hosts) > 1:
        return HttpResponseInvalidState("Multiple hosts found matching '%s'" % hostname)
    host = hosts[0]
    
    try:
        host.revert_pgi_image()
    except RevertPGIImageError as e:
        return HttpResponseInvalidState(str(e))
    
    return


def get_si_images(request, si_hostname):
    """Gets a lists of all images on a systemimager.

    Returns:
    A list of image names formatted as strings.
    
    Arguments:
    si_hostname -- the hostname of the systemimager formatted as a string.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching hostname. 
    JinxInvalidStateError -- more than one host was found matching the hostname.
    """

    hosts = llclusto.get_by_hostname(si_hostname)
    if len(hosts) < 1:
        return HttpResponseNotFound("Systemimager hostname '%s' does not exist" % si_hostname)
    elif len(hosts) > 1:
        return HttpResponseInvalidState("Multiple hosts found matching '%s'" % si_hostname)
    host = hosts[0]
        
    images = []
    for image in host.get_stored_pgi_images():
        images.append(image.name)

    return images


def delete_si_image(request, si_hostname, image_name):
    """Deletes the PGI image from systemimager.
    
    Returns:
    None
    
    Arguments:
    si_hostname -- the systemimager hostname formatted as a string.
    image_name -- the image name formatted at a string.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching systemimager hostname or image_name.
                          -- unable to find image on systemimager.
    JinxInvalidStateError -- image is still associated with hosts.
                          -- more than one host was found matching the hostname.
    """

    try:
        image = clusto.get_by_name(image_name)
    except LookupError:
        return HttpResponseNotFound("Image '%s' does not exist." % image_name)
    
    hosts = llclusto.get_by_hostname(si_hostname)
    if len(hosts) < 1:
        return HttpResponseNotFound("Systemimager hostname '%s' does not exist" % si_hostname)
    elif len(hosts) > 1:
        return HttpResponseInvalidState("Multiple hosts found matching '%s'" % si_hostname)
    host = hosts[0]
    
    # First, verify no host is using this as a current image
    hosts = image.get_hosts_associated_with()
    if len(hosts) != 0:
        hostnames = [host.hostname for host in hosts]
        return HttpResponseInvalidState("Unable to delete image from SI host.  Image '%s' currently in use by hosts: '%s'" % (image_name, 
                                                                                                                              ",".join(hostnames)))
    try:
        host.delete_stored_pgi_image(image)
    except LookupError:
        return HttpResponseNotFound("Image '%s' is not marked as stored on systemimager '%s'." % (image_name, si_hostname))

    return


def add_si_image(request, si_hostname, image_name):
    """Adds image to systemimager.

    Returns:
    None

    Arguments:
    si_hostname -- the systemimager hostname formatted as a string.
    image_name -- the image name formatted at a string.

    Exceptions Raised:
    JinxDataNotFoundError -- unable to find matching systemimager hostname or image_name.
    JinxInvalidStateError -- more than one host was found matching the hostname.
    """

    hosts = llclusto.get_by_hostname(si_hostname)
    if len(hosts) < 1:
        return HttpResponseNotFound("Systemimager hostname '%s' does not exist" % si_hostname)
    elif len(hosts) > 1:
        return HttpResponseInvalidState("Multiple hosts found matching '%s'" % si_hostname)
    host = hosts[0]
    
    try:
        image = clusto.get_by_name(image_name)
    except LookupError:
        image = PGIImage(image_name)
        
    host.add_stored_pgi_image(image)
    
    return
