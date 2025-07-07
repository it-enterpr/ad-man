from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'company_name', 'internal_name', 'domain', 
            'contact_person', 'email',
            'has_odoo', 'has_odoo_enterprise', 'has_nextcloud', 'has_duplicati'
        ]