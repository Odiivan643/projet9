# exams/replacements.py
"""
Code qui REMPLACE les middlewares Django quand ils sont désactivés
Ce fichier montre ce que Django fait automatiquement en interne
"""

import hashlib
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin


# ========================================
# REMPLACE SessionMiddleware
# ========================================
class ManualSessionMiddleware(MiddlewareMixin):
    """
    Ce que Django fait automatiquement avec SessionMiddleware :
    - Charger la session depuis la base de données
    - Créer request.session
    - Sauvegarder automatiquement les modifications
    """
    
    def process_request(self, request):
        """AVANT que la vue soit appelée"""
        print("🔵 [MANUEL] SessionMiddleware activé")
        
        # 1. Lire le cookie 'sessionid'
        session_key = request.COOKIES.get('sessionid')
        
        # 2. Charger la session depuis la DB ou créer une nouvelle
        if session_key:
            try:
                Session.objects.get(session_key=session_key)
                request.session = SessionStore(session_key)
                print(f"   ✅ Session chargée : {session_key[:16]}...")
            except Session.DoesNotExist:
                request.session = SessionStore()
                print(f"   🆕 Session invalide, nouvelle créée")
        else:
            request.session = SessionStore()
            print(f"   🆕 Nouvelle session créée")
    
    def process_response(self, request, response):
        """APRÈS que la vue a été exécutée"""
        
        if hasattr(request, 'session'):
            # 3. Sauvegarder la session en DB
            if request.session.modified or request.session.is_empty():
                request.session.save()
                print(f"   💾 Session sauvegardée en DB")
            
            # 4. Ajouter le cookie à la réponse
            response.set_cookie(
                key='sessionid',
                value=request.session.session_key,
                max_age=3600,
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            print(f"   🍪 Cookie 'sessionid' envoyé au client")
        
        return response


# ========================================
# REMPLACE AuthenticationMiddleware
# ========================================
class ManualAuthMiddleware(MiddlewareMixin):
    """
    Ce que Django fait automatiquement avec AuthenticationMiddleware :
    - Lire '_auth_user_id' dans la session
    - Charger l'utilisateur depuis User.objects
    - Créer request.user
    """
    
    def process_request(self, request):
        """AVANT que la vue soit appelée"""
        print("🟢 [MANUEL] AuthenticationMiddleware activé")
        
        # 1. Vérifier qu'une session existe
        if not hasattr(request, 'session'):
            request.user = AnonymousUserManual()
            print("   ❌ Pas de session, utilisateur anonyme")
            return
        
        # 2. Récupérer l'ID de l'utilisateur depuis la session
        user_id = request.session.get('_auth_user_id')
        
        # 3. Charger l'utilisateur depuis la base de données
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                request.user = user
                print(f"   👤 Utilisateur chargé : {user.username} (ID: {user.id})")
            except User.DoesNotExist:
                request.user = AnonymousUserManual()
                print(f"   ⚠️  Utilisateur ID {user_id} introuvable")
                # Nettoyer la session
                del request.session['_auth_user_id']
        else:
            request.user = AnonymousUserManual()
            print(f"   🔓 Aucun utilisateur connecté")


class AnonymousUserManual:
    """Représente un utilisateur non connecté"""
    id = None
    pk = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False
    is_authenticated = False
    
    def __str__(self):
        return 'AnonymousUser'
    
    def __bool__(self):
        return False


# ========================================
# REMPLACE CsrfViewMiddleware
# ========================================
class ManualCsrfMiddleware(MiddlewareMixin):
    """
    Ce que Django fait automatiquement avec CsrfViewMiddleware :
    - Générer un token CSRF unique
    - Vérifier le token sur POST/PUT/DELETE
    - Bloquer les requêtes sans token valide
    """
    
    def process_request(self, request):
        """AVANT que la vue soit appelée"""
        print("🟡 [MANUEL] CsrfMiddleware activé")
        
        # 1. Générer un token CSRF unique
        session_key = request.session.session_key if hasattr(request, 'session') else 'no-session'
        csrf_token = hashlib.sha256(f"{session_key}-csrf-secret".encode()).hexdigest()[:32]
        
        # 2. Stocker le token dans request.META (pour les templates)
        request.META['CSRF_COOKIE'] = csrf_token
        print(f"   🔑 Token CSRF généré : {csrf_token[:16]}...")
        
        # 3. Vérifier le token sur POST/PUT/DELETE
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            
            # Exemptions (login, register, etc.)
            exempt_paths = ['/login/', '/register/']
            if any(request.path.startswith(path) for path in exempt_paths):
                print(f"   ⚪ {request.path} exempté de CSRF")
                return None
            
            # Récupérer le token soumis par le client
            submitted_token = (
                request.POST.get('csrfmiddlewaretoken') or
                request.META.get('HTTP_X_CSRFTOKEN') or
                request.COOKIES.get('csrftoken')
            )
            
            # Comparer les tokens
            if submitted_token != csrf_token:
                print(f"   ❌ CSRF INVALIDE ! Requête bloquée")
                return HttpResponseForbidden("403 Forbidden - CSRF verification failed")
            else:
                print(f"   ✅ Token CSRF valide")
    
    def process_response(self, request, response):
        """APRÈS que la vue a été exécutée"""
        
        # Ajouter le cookie CSRF à la réponse
        if hasattr(request, 'META') and 'CSRF_COOKIE' in request.META:
            response.set_cookie(
                key='csrftoken',
                value=request.META['CSRF_COOKIE'],
                max_age=31449600,  # 1 an
                httponly=False,  # JavaScript doit pouvoir y accéder
                secure=False,
                samesite='Lax'
            )
            print(f"   🍪 Cookie 'csrftoken' envoyé")
        
        return response


# ========================================
# 4️⃣ REMPLACE MessageMiddleware
# ========================================
class ManualMessageMiddleware(MiddlewareMixin):
    """
    Ce que Django fait automatiquement avec MessageMiddleware :
    - Stocker les messages dans la session
    - Fournir messages.success(), messages.error(), etc.
    """
    
    def process_request(self, request):
        """AVANT que la vue soit appelée"""
        print("🟣 [MANUEL] MessageMiddleware activé")
        
        # Charger les messages depuis la session
        if hasattr(request, 'session'):
            messages_list = request.session.get('_messages', [])
            request._messages_storage = messages_list
            print(f"   📬 {len(messages_list)} message(s) chargé(s)")
    
    def process_response(self, request, response):
        """APRÈS que la vue a été exécutée"""
        
        # Sauvegarder les messages dans la session
        if hasattr(request, '_messages_storage') and hasattr(request, 'session'):
            request.session['_messages'] = request._messages_storage
            print(f"   💾 Messages sauvegardés dans la session")
        
        return response


# ========================================
# FONCTIONS HELPER POUR LES VUES
# ========================================

def manual_login(request, user):
    """
    REMPLACE : from django.contrib.auth import login
    
    Utilisation dans vos vues :
        from exams.replacements import manual_login
        manual_login(request, user)
    """
    print(f"🔐 [MANUEL] Connexion de {user.username}")
    request.session['_auth_user_id'] = user.pk
    request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
    request.session.modified = True
    request.user = user


def manual_logout(request):
    """
    REMPLACE : from django.contrib.auth import logout
    
    Utilisation dans vos vues :
        from exams.replacements import manual_logout
        manual_logout(request)
    """
    print(f"🚪 [MANUEL] Déconnexion")
    request.session.flush()
    request.user = AnonymousUserManual()