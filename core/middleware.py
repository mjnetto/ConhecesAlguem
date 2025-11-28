"""
Middleware customizado para aceitar domínios Railway automaticamente
"""
from django.middleware.common import CommonMiddleware
from django.http import Http404


class RailwayCommonMiddleware(CommonMiddleware):
    """
    CommonMiddleware customizado que aceita domínios Railway automaticamente
    """
    
    def process_request(self, request):
        host = request.get_host().split(':')[0]  # Remove porta
        
        # Se é um domínio Railway, aceita automaticamente
        if host.endswith('.railway.app') or host.endswith('.up.railway.app'):
            # Valida o host manualmente, mas aceita Railway
            from django.conf import settings
            allowed_hosts = settings.ALLOWED_HOSTS
            
            # Se já está em ALLOWED_HOSTS ou é Railway, permite
            if host in allowed_hosts or '*' in allowed_hosts:
                return None
            
            # Aceita domínios Railway mesmo se não estiver em ALLOWED_HOSTS
            return None
        
        # Para outros hosts, usa validação padrão do CommonMiddleware
        return super().process_request(request)

