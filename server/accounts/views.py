from django.shortcuts import (render,redirect)
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import (AuthenticationForm,UserCreationForm,PasswordResetForm,PasswordChangeForm)
from django.contrib.auth.models import User
from django.contrib.auth import (login,logout,update_session_auth_hash)
from django.core.mail import EmailMessage
from django.utils.http import (urlsafe_base64_encode,urlsafe_base64_decode)
from django.http import JsonResponse 
from django.template.loader import render_to_string
from django.utils.encoding import (force_bytes,force_text)
from .token import Account_Vlidation_Token


class SignupForm(UserCreationForm):
    class Meta:
        model=User
        fields=("username","email","password1","password2")

class PasswordFormRest(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        del self.fields['old_password']
    class Meta:
        model=User
        fields=("new_password1","new_password2")

def Login_Request_Handler(request):
    if request.method=="POST":
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return JsonResponse(request.POST)
        else:       
            return JsonResponse({"error":"un error ocured"})
       



def Signup_Request_Handler(request):
    
    if request.method=="POST":
        form=SignupForm(request.POST)
        if form.is_valid():
                user=form.save(commit=False)
                user.is_active=False
                user.save()
                current_site=get_current_site(request)
                subject="Aactivate your Account !"
                body=render_to_string('accounts/activate.djt',{
                    'user':user,
                    'domain':current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':Account_Vlidation_Token.make_token(user)
                })
                mail_to=EmailMessage(subject=subject,body=body,to=[form.cleaned_data.get('email')])
                mail_to.send()
                return JsonResponse(request.POST)            
        else:
        
            return JsonResponse({"error":"un error ocured"})
    



def Rest_Password_Request_Handler(request):
        
        if request.method=="POST":
            form=PasswordResetForm(request.POST)
            if form.is_valid():
                try:
                    user=User.objects.get(email=form.cleaned_data.get('email'))
                    current_site=get_current_site(request)
                    subject="Reset your Password Account !"
                    body=render_to_string('accounts/resetpass.djt',{
                        'user':user,
                        'domain':current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':Account_Vlidation_Token.make_token(user)
                        })
                    mail_to=EmailMessage(subject=subject,body=body,to=[form.cleaned_data.get('email')])
                    mail_to.send()
                    return JsonResponse(request.POST)
                except Exception as e:
                     
                     return JsonResponse({"error":"un error ocured"})
    

def Valid_Reset_Password_Hequest_Handler(request,uid,token):
    try:
        uid=force_text(urlsafe_base64_decode(uid))
        user=User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist) as e:
        user=None
    if user is not None and Account_Vlidation_Token.check_token(user,token):
        if request.method=="POST":
            form=PasswordFormRest(data=request.POST,user=user)
            if form.is_valid():
                form.save(commit=True)
                update_session_auth_hash(request,user)
                return JsonResponse()
            else:
                url=request.get_full_path().split('/')
            
                return JsonResponse(request.POST)
        else:
            url=request.get_full_path().split('/')
           
            return JsonResponse({"error":"un error ocured"})

    


def Valid_Email_Request_Handler(request,uid,token):
    try:
        uid=force_text(urlsafe_base64_decode(uid))
        user=User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None
    if user is not None and Account_Vlidation_Token.check_token(user,token):
        user.is_active=True
        user.save()
        login(request,user)
        return JsonResponse(request.POST)
    else:
        return JsonResponse({"error":"un error ocured"})
   

def Logout_Request_Hanlder(request):
    if request.method=="POST":
        logout(request)
        return JsonResponse(request.POST)
