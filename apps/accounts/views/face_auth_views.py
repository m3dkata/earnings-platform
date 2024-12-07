from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import login
from django.contrib import messages
import numpy as np
import json
from ..models import FaceDescriptor

@login_required
def face_training(request):
    context = {
        'models_url': settings.STATIC_URL + 'models/',
        'has_existing': FaceDescriptor.objects.filter(user=request.user).exists()
    }
    return render(request, 'accounts/face_training.html', context)

@login_required
@require_POST
def save_face_descriptor(request):
    try:
        import json
        data = json.loads(request.body)
        descriptor = data.get('descriptor')
        
        FaceDescriptor.objects.update_or_create(
            user=request.user,
            defaults={'descriptor': descriptor}
        )
        request.user.is_face_login_enabled = True
        request.user.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        messages.error(f"Face descriptor save error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_protect
def verify_face_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            descriptor = np.array(data.get('descriptor'))
            
            all_face_descriptors = FaceDescriptor.objects.all()
            for face_desc in all_face_descriptors:
                stored_descriptor = np.array(face_desc.descriptor)
                distance = np.linalg.norm(descriptor - stored_descriptor)
                
                if distance < 0.6:
                    user = face_desc.user
                    login(request, user)
                    return JsonResponse({
                        'status': 'success',
                        'redirect_url': reverse('dashboard')
                    })
            
            return JsonResponse({'status': 'error', 'message': 'Face not recognized'})
                
        except Exception as e:
            messages.error(f"Face verification error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return render(request, 'accounts/verify_face_login.html')