from django.db import models

class DNSService(models.Model):
    name = models.CharField(max_length=100, unique=True)
    comment = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name

class DNSRecord(models.Model):
    name = models.CharField(max_length=255, unique=True)
    comment = models.CharField(max_length=255, blank=True)
    group = models.ForeignKey(DNSService, null=True)

    def __unicode__(self):
        return self.name

    class Admin:
        list_display = ('name', 'comment', 'group')
        
class Lock(models.Model):
    name = models.CharField(max_length=255, unique=True)
    value = models.IntegerField()

    def __unicode__(self):
        return self.name




