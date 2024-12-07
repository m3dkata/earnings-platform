from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    is_2fa_enabled = models.BooleanField(default=False, verbose_name='2FA Enabled')
    is_email_otp_enabled = models.BooleanField(default=False, verbose_name='Email OTP Enabled')
    is_face_login_enabled = models.BooleanField(default=False)
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=20, 
                                    validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
                                    unique=True, null=True, blank=True, verbose_name='Phone Number')
    profile_image = models.ImageField(upload_to='profile_images', blank=True, null=True, verbose_name='Profile Image')
    first_name = models.CharField(max_length=30, verbose_name='First Name')
    last_name = models.CharField(max_length=30, verbose_name='Last Name')
    is_employee = models.BooleanField(default=True, verbose_name='Employee')
    is_archived = models.BooleanField(default=False, verbose_name='Archived')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if self.profile_image:
            img = Image.open(self.profile_image)
            if img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')
            
            aspect_ratio = img.height / img.width
            new_width = 500
            new_height = int(new_width * aspect_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            img.save(output, format='png', quality=85)
            output.seek(0)
            
            name = os.path.splitext(self.profile_image.name)[0] + '.png'
            self.profile_image = ContentFile(output.read(), name=name)
            
        if self.profile_image and self.profile_image.size > 5*1024*1024:
            raise ValidationError("Image file too large ( > 5MB )")
        
        if self.is_archived and self.is_active:
            self.is_active = False
        super().save(*args, **kwargs)
        
    class Meta:    
        verbose_name = ('Administrator')
        verbose_name_plural = ('Administrators')

class EmployeeUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        
class PendingUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Inactive Employee'
        verbose_name_plural = 'Inactive Employees'  

class ArchivedUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Archived Employee'
        verbose_name_plural = 'Archived Employees'              
            
class EmailVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, verbose_name='OTP')
    created_at = models.DateTimeField(auto_now_add=True)    
    
class ActivityLog(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, verbose_name='User')
    action = models.CharField(max_length=50, verbose_name='Action')
    model = models.CharField(max_length=50, verbose_name='Model')
    instance_id = models.IntegerField(verbose_name='Instance ID', default=0)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')

    class Meta:
        ordering = ['-timestamp']   
        indexes = [
            models.Index(fields=['timestamp', 'user']),
        ]

class FaceDescriptor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='face_descriptor', )
    descriptor = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    class Meta:
        db_table = 'accounts_facedescriptor'
        verbose_name = 'Face ID'


        
@receiver(pre_save, sender=CustomUser)
def delete_old_profile_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CustomUser.objects.get(pk=instance.pk)
            if old_instance.profile_image and old_instance.profile_image != instance.profile_image:
                if os.path.isfile(old_instance.profile_image.path):
                    os.remove(old_instance.profile_image.path)
        except CustomUser.DoesNotExist:
            pass        

class CustomUserManager(models.Manager):
    def active(self):
        return self.filter(is_archived=False)        