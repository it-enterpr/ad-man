from django.db import models

class Client(models.Model):
    company_name = models.CharField("Název společnosti", max_length=200)
    internal_name = models.CharField("Interní název (pro složku)", max_length=100, unique=True)
    domain = models.CharField("Vlastní doména klienta", max_length=255)
    contact_person = models.CharField("Kontaktní osoba", max_length=200, blank=True)
    email = models.EmailField("Kontaktní email", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    has_odoo = models.BooleanField("Nainstalovat Odoo Community", default=True)
    has_odoo_enterprise = models.BooleanField("Nainstalovat Odoo Enterprise", default=False)
    has_nextcloud = models.BooleanField("Nainstalovat Nextcloud", default=False)
    has_duplicati = models.BooleanField("Nainstalovat Duplicati", default=False)

    def __str__(self):
        return self.company_name