from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import login
from django.shortcuts import redirect


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Google OAuth orqali kirgan foydalanuvchilarni to'g'ridan-to'g'ri 
    tizimga kiritish uchun custom adapter
    """
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Signup page ga yo'naltirilmasdan avtomatik signup qilish
        """
        return True
    
    def pre_social_login(self, request, sociallogin):
        """
        Social login oldidan bajariladi
        """
        # Agar foydalanuvchi allaqachon mavjud bo'lsa
        if sociallogin.is_existing:
            return
        
        # Agar email mavjud bo'lsa, shu email bilan user bormi tekshirish
        if 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data['email']
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(email=email)
                
                # Mavjud user bilan social account ni bog'lash
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Yangi user yaratish
        """
        user = super().save_user(request, sociallogin, form)
        
        # Google'dan kelgan ma'lumotlarni olish
        data = sociallogin.account.extra_data
        
        # Username ni email'dan yaratish (agar yo'q bo'lsa)
        if not user.username:
            user.username = data.get('email', '').split('@')[0]
            
        # First name va Last name ni sozlash
        if 'given_name' in data:
            user.first_name = data['given_name']
        if 'family_name' in data:
            user.last_name = data['family_name']
            
        user.save()
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """
        User ma'lumotlarini to'ldirish
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Google'dan kelgan ma'lumotlar
        extra_data = sociallogin.account.extra_data
        
        # Email
        if 'email' in extra_data:
            user.email = extra_data['email']
            
        # Username (email'dan)
        if not user.username and 'email' in extra_data:
            user.username = extra_data['email'].split('@')[0]
            
        # First name
        if 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
            
        # Last name
        if 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        return user