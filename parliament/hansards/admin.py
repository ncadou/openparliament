from django.contrib import admin

from parliament.hansards.models import *

class DocumentOptions(admin.ModelAdmin):
    list_display=('id', 'number', 'date', 'session', 'document_type', 'committeemeeting', 'source_id')
    list_filter=('document_type', 'session', 'date', 'multilingual', 'public', 'senate')
    
admin.site.register(Document, DocumentOptions)
admin.site.register(Statement)