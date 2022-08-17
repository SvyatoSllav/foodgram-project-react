from rest_framework import serializers

from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model, password_validation

from users.models import Follow


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class SafeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self._user(obj)
        if not user.is_anonymous:
            return Follow.objects.filter(follower=user, following=obj).exists()

    def _user(self, obj):
        request = self.context.get('request', None)
        print(self.context)
        if request:
            return request.user
        return obj


class UserPasswordChangeSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField(source='password')

    class Meta:
        model = User
        fields = (
            'new_password',
            'current_password'
        )

    def validate_current_password(self, value):
        if not User.objects.filter(password=value).exists():
            raise ValidationError('Пароль неверный')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def _user(self, obj):
        request = self.context.get('request', None)
        if request:
            return request.user
        return obj


class GetTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'password',
            'email',
        )
