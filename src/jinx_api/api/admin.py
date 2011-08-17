from django.contrib import admin

from jinx_api.api.models import DNSRecord, DNSService

class DNSRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment', 'group')
    search_fields =('name', 'comment', 'group')

class DNSServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    search_fields =('name', 'comment')

    
admin.site.register(DNSRecord, DNSRecordAdmin)
admin.site.register(DNSService, DNSServiceAdmin)


