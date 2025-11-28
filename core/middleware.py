"""
Middleware customizado para aceitar domínios Railway automaticamente
"""
from django.middleware.common import CommonMiddleware
from django.http import Http404
from django.core.exceptions import DisallowedHost


class RailwayCommonMiddleware(CommonMiddleware):
    """
    CommonMiddleware customizado que aceita domínios Railway automaticamente
    """
    
    def process_request(self, request):
        # Pega o host do header HTTP diretamente, antes da validação do Django
        host = request.META.get('HTTP_HOST', '').split(':')[0]
        
        # Se é um domínio Railway, aceita automaticamente
        if (host.endswith('.railway.app') or 
            host.endswith('.up.railway.app') or
            host == 'healthcheck.railway.app'):
            # Aceita domínios Railway - não precisa validar ALLOWED_HOSTS
            # O Django vai validar depois, mas vamos adicionar ao ALLOWED_HOSTS temporariamente
            from django.conf import settings
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
            return None
        
        # Para outros hosts, usa validação padrão do CommonMiddleware
        try:
            return super().process_request(request)
        except DisallowedHost:
            # Se o host não está permitido, tenta adicionar se for Railway
            if (host.endswith('.railway.app') or 
                host.endswith('.up.railway.app') or
                host == 'healthcheck.railway.app'):
                from django.conf import settings
                if host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(host)
                return None
            raise


class RailwayCsrfMiddleware:
    """
    Middleware para aceitar domínios Railway no CSRF automaticamente
    Django não aceita wildcards em CSRF_TRUSTED_ORIGINS, então fazemos dinamicamente
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Adiciona origem Railway ao CSRF_TRUSTED_ORIGINS dinamicamente
        origin = request.META.get('HTTP_ORIGIN', '')
        if origin:
            from django.conf import settings
            # Se é domínio Railway e ainda não está na lista, adiciona
            if (origin.startswith('https://') and 
                ('.railway.app' in origin or '.up.railway.app' in origin)):
                if origin not in settings.CSRF_TRUSTED_ORIGINS:
                    settings.CSRF_TRUSTED_ORIGINS.append(origin)
        
        return self.get_response(request)

