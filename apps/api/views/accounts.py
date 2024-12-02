from apps.accounts.models import CustomUser, EmailVerification
from apps.accounts.utils import generate_otp, send_otp_email
from apps.api.serializers.accounts import LogoutSerializer, UserLoginResponseSerializer, UserLoginSerializer, UserSignupSerializer, VerifyOTPSerializer
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from django.urls import reverse


class UserSignupAPIView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=UserSignupSerializer,
        responses={201: UserSignupSerializer}
    )
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginResponseSerializer}
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            
            user = None
            if username:
                user = CustomUser.objects.filter(username=username).first()
            elif email:
                user = CustomUser.objects.filter(email=email).first()
                
            if user and user.check_password(password):
                if user.is_2fa_enabled or user.is_email_otp_enabled:
                    if user.is_email_otp_enabled:
                        otp = generate_otp()
                        EmailVerification.objects.update_or_create(
                            user=user,
                            defaults={'otp': otp}
                        )
                        send_otp_email(user, otp)
                    
                    return Response({
                        'requires_2fa': user.is_2fa_enabled,
                        'requires_email_otp': user.is_email_otp_enabled,
                        'user_id': user.id
                    })
                    
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=VerifyOTPSerializer,
        responses={200: {'type': 'object'}}
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(CustomUser, id=serializer.validated_data['user_id'])
            otp_code = serializer.validated_data['otp_code']
            
            if user.is_2fa_enabled:
                device = TOTPDevice.objects.get(user=user)
                if not device.verify_token(otp_code):
                    return Response({'error': 'Invalid 2FA code'}, status=status.HTTP_400_BAD_REQUEST)
                    
            if user.is_email_otp_enabled:
                verification = get_object_or_404(EmailVerification, user=user)
                if verification.otp != otp_code:
                    return Response({'error': 'Invalid OTP code'}, status=status.HTTP_400_BAD_REQUEST)
                verification.delete()
                
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    @extend_schema(
        request=LogoutSerializer,
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

