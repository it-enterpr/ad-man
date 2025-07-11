# Generated by Django 5.0.6 on 2025-07-07 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_alter_client_company_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='has_odoo_enterprise',
            field=models.BooleanField(default=False, verbose_name='Nainstalovat Odoo Enterprise'),
        ),
        migrations.AlterField(
            model_name='client',
            name='has_odoo',
            field=models.BooleanField(default=True, verbose_name='Nainstalovat Odoo Community'),
        ),
    ]
