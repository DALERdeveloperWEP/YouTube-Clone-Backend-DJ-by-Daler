import random
import re

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import login
from django.core.mail import send_mail

from .models import EmailOTP

User = get_user_model()


def send_otp_email(request, user):
    code = str(random.randint(100000, 999999))

    otp = EmailOTP.objects.create(user=user, code=code)

    subject = "StreamTube - Tasdiqlash Code"
    message = (
        f"Assalomu alaykum, {user.username}!\n\n"
        f"Sizning StreamTube web saytingizga tashrifingiz uchun rahmat.\n\n"
        f"Tasdiqlash kodingiz: {code}\n\n"
        f"Rahmat,\nStreamTube Admini"
    )

    from_email = settings.EMAIL_HOST_USER
    to_email = [user.email]

    try:
        print('1')
        sent = send_mail(
            subject,
            message,
            from_email,
            to_email,
            fail_silently=False
        )
        print('2')

        if sent == 0:
            print('3')
            otp.delete()
            return JsonResponse({"Errors": "Email failed to send"}, status=400)
        print('4')

    except Exception as e:
        otp.delete()
        print(f'{e}')
        raise 
        return JsonResponse({"Errors": "Email failed to send"}, status=500)

    return True


class AuthUserLogin(View):
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'login-register.html', context={"view": 'login'})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)
        
        user = authenticate(request, email=email, password=password)
        
        
        if not user:
            return JsonResponse({"error": "Invalid email or password"}, status=400)
        
        if user:
            request.session["otp_user_id"] = user.id

            send_otp_email(request, user)

            return redirect("verify")
        
        return JsonResponse({"error": "Something went wrong"}, status=500)


class AuthUserRegister(View):
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'login-register.html', {"view": "register"})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not username or not email or not password:
            return JsonResponse({"error": "Username, email, and password are required"}, status=400)
        
        check_user = User.objects.filter(email=email).exists()
        
        if check_user:
            return JsonResponse({"Errors": "User with this email already exists"}, status=400)

        USERNAME_REGEX = re.compile(r'^(?=.*[a-z])[a-z0-9_-]+$')
        
        def validate_username(username: str) -> bool:
            if not username:          # kamida 1 ta belgi
                return JsonResponse({"Errors": "Username min one character"}, status=400)
            return bool(USERNAME_REGEX.fullmatch(username))
        
        if not validate_username(username):
            return JsonResponse({"Errors": "Username is not valid"}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        
        request.session["otp_user_id"] = user.id

        send_otp_email(request, user)

        return redirect("verify")
        

class AuthUserVerify(View):
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.session.get("otp_user_id"):
            return redirect("home")

        if not request.session.get("otp_user_id"):
            return redirect("login")

        return super().dispatch(request, *args, **kwargs)
    
    
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'verify.html')
    
    def post(self, request: HttpRequest) -> HttpResponse | JsonResponse:
        
        code = request.POST.get('code')
        user_id = request.session.get("otp_user_id")
        resend = request.POST.get('resend')
        
        try: 
            user = User.objects.get(id=user_id)
        except:
            return redirect('register')
        
        if resend:
            send_otp_email(request, user)
            return JsonResponse({"message": "Verification code sent successfully"})
        
        
        if not code.isdigit():
            return render(request, "verify.html", {
                "error": "Code Raqam bo'lishi kerak"
            })
        
        otp = EmailOTP.objects.filter(
            user_id=user_id,
            code=int(code),
            is_used=False
        ).first()
        
        if not otp:
            return render(request, "verify.html", {
                "error": "Code noto‘g‘ri"
            })
        
        if otp.is_expired():
            otp.delete()
            return render(request, "verify.html", {
                "error": "Code muddati tugagan"
            })
            
        otp.is_used = True
        user = User.objects.get(id=user_id)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session.pop("otp_user_id", None)
        EmailOTP.objects.filter(user=user).delete()
        otp.save()
        return redirect("home")

    
def logout_view(request: HttpRequest):
    logout(request)
    request.session.flush()
    return redirect("login")


