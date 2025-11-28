# Generated migration to make IBAN optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_client_google_id_professional_google_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professional',
            name='iban',
            field=models.CharField(blank=True, default='', max_length=34, verbose_name='IBAN'),
        ),
    ]

