from django.db import models

class DNSService(models.Model):
    name = models.CharField(max_length=100, unique=True)
    comment = models.CharField(max_length=255)
    # add text field
    def __unicode__(self):
        return self.name + ':' + self.comment


class DNSRecord(models.Model):
    name = models.CharField(max_length=255, unique=True)
    comment = models.CharField(max_length=255)
    group = models.ForeignKey(DNSService, null=True)

    def __unicode__(self):
        return self.name
    
