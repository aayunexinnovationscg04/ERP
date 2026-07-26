from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Company, User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "slug", "status", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "company",
                  "first_name", "last_name"]


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login that also embeds role/company in the token and returns the user."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["company_id"] = user.company_id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class AdminUserSerializer(serializers.ModelSerializer):
    """Super-Admin view of a user: create with a password, assign role + company."""

    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), allow_null=True, required=False)
    company_name = serializers.CharField(source="company.name", read_only=True, default=None)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "company",
                  "company_name", "is_active", "password", "last_login"]
        read_only_fields = ["last_login"]

    def create(self, validated):
        pwd = validated.pop("password", None)
        user = User(**validated)
        if pwd:
            user.set_password(pwd)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated):
        pwd = validated.pop("password", None)
        for k, v in validated.items():
            setattr(instance, k, v)
        if pwd:
            instance.set_password(pwd)
        instance.save()
        return instance
