import clusto
import llclusto

def get_linden_pdus(request):
    """Returns a list of hostnames for all hosts with a driver of LindenPDU.
    """

    pdus = clusto.get_entities(clusto_drivers=[llclusto.drivers.LindenPDU])
    
    return [pdu.hostname for pdu in pdus if pdu.hostname.lower() != 'missing']

    
