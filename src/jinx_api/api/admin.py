from django.contrib import admin
from jinx_api.api.models import DNSRecord, DNSService

from django.contrib.auth.admin import User, UserAdmin
from models import UserProfile



class DNSRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment', 'group')
    search_fields =('name', 'comment', 'group')

class DNSServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    search_fields =('name', 'comment')


# This code allows us to view the extended attributes for UserProfile in the admin interface.
class ProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'
    max_num = 1

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline,]
    
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(DNSRecord, DNSRecordAdmin)
admin.site.register(DNSService, DNSServiceAdmin)


