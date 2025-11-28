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

