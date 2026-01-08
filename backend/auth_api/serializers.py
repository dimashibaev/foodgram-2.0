from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from access_control.services import ensure_default_role_for_user

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=150)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=150)
    middle_name = serializers.CharField(required=True, allow_blank=False, max_length=150)
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match'})
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data.get('username') or email.split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            password=validated_data['password'],
        )
        ensure_default_role_for_user(user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'middle_name', 'last_name')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'middle_name', 'last_name')
