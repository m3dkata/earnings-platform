from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm as BasePasswordResetForm 
from django.utils.translation import gettext_lazy as _
from apps.accounts.tasks import send_password_reset_email_task
import phonenumbers
from .models import CustomUser
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.db import models

COMMON_FIELD_CLASSES = ''
FILE_FIELD_CLASSES = 'w-full px-4 py-2 rounded-lg border border-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-[--accent] file:text-white hover:file:bg-[--accent]/80'

class BaseStyleForm:
    def apply_common_styles(self):
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': COMMON_FIELD_CLASSES,
                'placeholder': field.label,
            })
            if field.help_text:
                field.widget.attrs.update({'title': field.help_text})

class CustomLoginForm(AuthenticationForm, BaseStyleForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = CustomUser.objects.get(
                    models.Q(username=username) | models.Q(email=username)
                )
                if not user.is_active:
                    raise forms.ValidationError(_("Please try again later, your account is still not activated by Administrators!"))
                if not user.check_password(password):
                    raise forms.ValidationError(_("Please enter a correct password."))
                self.user_cache = user
            except CustomUser.DoesNotExist:
                raise forms.ValidationError(_("Please enter a correct username/email and password."))

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_styles()


class CustomUserCreationForm(UserCreationForm, BaseStyleForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_image')
        help_texts = {
            'username': _('Letters, digits and @/./+/-/_ only.'),
            'email': _('Enter a valid email address.'),
            'phone_number': _('Enter your phone number in international format.'),
            'profile_image': _('Upload a profile picture (optional).'),
        }
        error_messages = {
            'username': {
                'unique': _('This username is already taken.'),
                'invalid': _('Username may only contain letters, numbers, and @/./+/-/_'),
            },
            'email': {
                'unique': _('This email is already registered.'),
                'invalid': _('Please enter a valid email address.'),
            },
            'phone_number': {
                'unique': _('This phone number is already registered.'),
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.apply_common_styles()

        if 'profile_image' in self.fields:
            self.fields['profile_image'].widget.attrs.update({
                'class': FILE_FIELD_CLASSES,
                'accept': 'image/*'
            })
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError(("Password must be at least 8 characters long"))
        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            try:
                parsed_number = phonenumbers.parse(phone_number)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise forms.ValidationError(_('Invalid phone number'))
                if CustomUser.objects.filter(phone_number=phone_number).exists():
                    raise forms.ValidationError(_('This phone number is already registered.'))
                return phone_number
            except phonenumbers.NumberParseException:
                raise forms.ValidationError(_('Invalid phone number format'))
        return phone_number

class CustomUserChangeForm(UserChangeForm, BaseStyleForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'profile_image')
        help_texts = {
            'email': _('Enter a valid email address.'),
            'phone_number': _('Enter your phone number in international format.'),
            'profile_image': _('Upload a new profile picture.'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_styles()

class PasswordResetForm(BasePasswordResetForm, BaseStyleForm):
    def send_mail(self, subject_template_name, email_template_name,
                 context, from_email, to_email, html_email_template_name=None):
        context['uid'] = urlsafe_base64_encode(force_bytes(context['user'].pk))
        context['token'] = default_token_generator.make_token(context['user'])
        context['protocol'] = settings.PROTOCOL
        
        user_data = {
            'username': context['user'].username,
            'email': context['user'].email
        }
        
        reset_url = f"{context['protocol']}://{settings.DOMAIN}/reset/{context['uid']}/{context['token']}/"
        send_password_reset_email_task.delay(to_email, user_data, reset_url)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is not registered.'))
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_styles()