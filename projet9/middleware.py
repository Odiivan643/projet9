"""
Middlewares personnalisés pour la démonstration
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from django.utils import timezone

logger = logging.getLogger('projet9.middleware')


class LoggingMiddleware(MiddlewareMixin):
    """Middleware pour logger toutes les requêtes HTTP"""
    
    def process_request(self, request):
        request.start_time = timezone.now()
        user = request.user.username if request.user.is_authenticated else 'Anonyme'
        logger.info(f"➡️ {request.method} {request.path} | User: {user}")
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = (timezone.now() - request.start_time).total_seconds()
            logger.info(f"⬅️ Status {response.status_code} | Durée: {duration:.3f}s")
        return response


class SessionSecurityMiddleware(MiddlewareMixin):
    """Middleware pour la sécurité des sessions"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Mettre à jour l'heure de dernière activité
            request.session['last_activity'] = timezone.now().isoformat()
            
            # Stocker l'IP de session
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            request.session['session_ip'] = ip
        
        return None


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Middleware pour gérer les erreurs"""
    
    def process_exception(self, request, exception):
        logger.error(f"🔥 Erreur: {str(exception)} sur {request.path}")
        return None