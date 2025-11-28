"""
Management command to update Django Site for OAuth redirects
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Update Django Site domain and name for OAuth redirects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Domain name (e.g., conhecesalguem-production.up.railway.app)',
        )

    def handle(self, *args, **options):
        domain = options.get('domain')
        
        if not domain:
            # Try to get from environment
            domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN') or os.environ.get('ALLOWED_HOSTS', '').split(',')[0]
            if domain and domain.strip():
                domain = domain.strip()
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Domain not provided. Use --domain or set RAILWAY_PUBLIC_DOMAIN')
                )
                return
        
        try:
            site = Site.objects.get(id=1)
            old_domain = site.domain
            site.domain = domain
            site.name = 'Conheces Alguém?'
            site.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Site updated successfully!')
            )
            self.stdout.write(f'   Old domain: {old_domain}')
            self.stdout.write(f'   New domain: {site.domain}')
            self.stdout.write(f'   Name: {site.name}')
            self.stdout.write('')
            self.stdout.write('🔗 OAuth callback URL should be:')
            self.stdout.write(f'   https://{site.domain}/accounts/google/login/callback/')
            
        except Site.DoesNotExist:
            # Create site if it doesn't exist
            site = Site.objects.create(
                id=1,
                domain=domain,
                name='Conheces Alguém?'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Site created successfully!')
            )
            self.stdout.write(f'   Domain: {site.domain}')
            self.stdout.write(f'   Name: {site.name}')

