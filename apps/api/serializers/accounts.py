from rest_framework import serializers
from apps.accounts.models import CustomUser


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data, is_active=False)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")
        if not username and not email:
            raise serializers.ValidationError("Must provide either username or email")
        return data


class UserLoginResponseSerializer(serializers.Serializer):
    requires_2fa = serializers.BooleanField()
    requires_email_otp = serializers.BooleanField()
    user_id = serializers.IntegerField()
    tokens = serializers.DictField(required=False)


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6)
    user_id = serializers.IntegerField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token to blacklist")
