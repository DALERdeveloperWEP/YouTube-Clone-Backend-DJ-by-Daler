from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import login
from django.core.mail import send_mail


User = get_user_model()


import random
from .models import EmailOTP

def send_otp_email(request, user):
    code = str(random.randint(100000, 999999))

    # 2️⃣ OTP ni DB ga saqlash
    otp = EmailOTP.objects.create(user=user, code=code)

    # 3️⃣ Email matni (plain text)
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
            # Agar email yuborilmasa, DB dagi OTP ni o‘chirish
            otp.delete()
            return render(request, 'register.html', {
                "view": "register",
                "Errors": "Email yuborilmadi. Iltimos, emailingizni tekshiring."
            })

    except Exception as e:
        # Xatolik yuz bersa, DB dagi OTP ni o‘chirish va xabar berish
        otp.delete()
        print("Email yuborishda xato:", e)
        return render(request, 'register.html', {
            "view": "register",
            "Errors": f"Email yuborishda xato: {str(e)}"
        })

    # 4️⃣ Hammasi muvaffaqiyatli bo‘lsa, True qaytarish
    return True



class AuthUserLogin(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'login-register.html', context={"view": 'login'})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            print('ha 1')
            return render(request, 'login-register.html', context={"view": "login", "Errors": "Email yoki Parol xato kiritildi"})
        
        user = authenticate(request, email=email, password=password)
        
        
        if not user:
            print(user)
            print('ha 2')
            return render(request, 'login-register.html', context={"Errors": "Email yoki Parol xato kiritildi", "view": "login"})
        
        if user:
            request.session.flush()  # eski session tozalash
            request.session["otp_user_id"] = user.id

            send_otp_email(request, user)

            return redirect("verify")
        
        return render(request, 'login-register.html', context={
            "view": 'login',
            "Errors": "Email yoki Parol xato kiritildi" 
        })


class AuthUserRegister(View):
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
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'verify.html')
    
    def post(self, request: HttpRequest) -> HttpResponse:
        
        code = request.POST.get('code', '')
        user_id = request.session.get("otp_user_id")
        
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
        login(request, user)
        otp.save()
        return redirect("home")
    
    
    
    
    
def logout_view(request):
    logout(request)          # 🔐 session + userni tozalaydi
    request.session.flush()  # 🔥 OTP session ham o‘chadi
    return redirect("login")