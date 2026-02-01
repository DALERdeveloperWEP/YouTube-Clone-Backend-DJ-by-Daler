import random

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
        sent = send_mail(
            subject,
            message,
            from_email,
            to_email,
            fail_silently=False
        )

        if sent == 0:
            otp.delete()
            return render(request, 'register.html', {
                "view": "register",
                "Errors": "Email yuborilmadi. Iltimos, emailingizni tekshiring."
            })

    except Exception as e:
        otp.delete()
        return render(request, 'register.html', {
            "view": "register",
            "Errors": f"Email yuborishda xato: {str(e)}"
        })

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
            return render(request, 'login-register.html', context={"view": "login", "Errors": "Email yoki Parol xato kiritildi"})
        
        user = authenticate(request, email=email, password=password)
        
        
        if not user:
            return render(request, 'login-register.html', context={"Errors": "Email yoki Parol xato kiritildi", "view": "login"})
        
        if user:
            request.session["otp_user_id"] = user.id

            send_otp_email(request, user)

            return redirect("verify")
        
        return render(request, 'login-register.html', context={
            "view": 'login',
            "Errors": "Email yoki Parol xato kiritildi" 
        })


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
            return render(request, 'register.html', {"view": "register", "Errors": "Notogri malumot kiritdingiz."})
        
        check_user = User.objects.filter(email=email).exists()
        
        if check_user:
            return render(request, 'register.html', {"view": "register", "Errors": "Bunday user mavjud"})
        
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


# def check_user_authenticate_api(request: HttpRequest) -> JsonResponse:
#     pass