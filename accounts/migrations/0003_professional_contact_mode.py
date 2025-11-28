# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='contact_mode',
            field=models.CharField(
                choices=[
                    ('booking', 'Apenas por Agendamento (via sistema)'),
                    ('direct', 'Contato Direto (mostrar telefone/WhatsApp)'),
                ],
                default='booking',
                help_text='Como os clientes podem entrar em contato com você',
                max_length=20,
                verbose_name='Modo de Contato',
            ),
        ),
    ]

