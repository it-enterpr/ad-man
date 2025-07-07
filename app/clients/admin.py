from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'internal_name', 'domain', 'created_at')
    search_fields = ('company_name', 'internal_name', 'domain')
    list_filter = ('has_odoo', 'has_nextcloud', 'has_duplicati')
    ordering = ('-created_at',)