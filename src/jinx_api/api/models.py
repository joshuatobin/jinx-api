from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    class Meta:
         permissions = (
              ("flip_databases", "Canflip databases"),
              ("flip_simulators", "Can flip simulators"),
              ("view_power_manage", "Can view power-manage"),
              )
              
    def __unicode__(self):
         return self.user.username
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)


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




