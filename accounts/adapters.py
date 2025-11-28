"""
Custom adapters for django-allauth to integrate with Client and Professional models
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from .models import Client, Professional


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter"""
    pass


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter to link Google OAuth with Client/Professional models"""
    
    def pre_social_login(self, request, sociallogin):
        """Called before social login completes"""
        if sociallogin.account.provider == 'google':
            # Get email from social account
            email = sociallogin.account.extra_data.get('email', '')
            google_id = sociallogin.account.uid
            name = sociallogin.account.extra_data.get('name', email.split('@')[0] if email else 'User')
            
            # Store in session for choose_user_type view
            request.session['google_email'] = email
            request.session['google_id'] = google_id
            request.session['google_name'] = name
    
    def save_user(self, request, sociallogin, form=None):
        """Called when saving user after social login"""
        # Let the default save happen first (creates User)
        user = super().save_user(request, sociallogin, form)
        
        # Store Google info in session for choose_user_type
        if sociallogin.account.provider == 'google':
            request.session['google_email'] = sociallogin.account.extra_data.get('email', '')
            request.session['google_id'] = sociallogin.account.uid
            request.session['google_name'] = sociallogin.account.extra_data.get('name', '')
            request.session['google_user_id'] = user.id
        
        return user
