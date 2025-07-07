from django.db import models

class Client(models.Model):
    company_name = models.CharField(max_length=200)
    internal_name = models.CharField(max_length=100, unique=True) # Název složky
    domain = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name