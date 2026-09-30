import re

from rest_framework import serializers

from .models import Company, User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "slug", "status", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    may_write = serializers.BooleanField(read_only=True)  # true for admin or granted can_edit

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "company",
                  "first_name", "last_name", "can_edit", "may_write"]


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin view of a user: create with a password, assign role + company."""

    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), allow_null=True, required=False)
    company_name = serializers.CharField(source="company.name", read_only=True, default=None)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "company",
                  "company_name", "is_active", "can_edit", "password", "last_login"]
        read_only_fields = ["last_login"]

    # Admin console rules: new accounts are dealers or pilots and need a phone
    # number; a role is fixed once the account exists; the admin may set a new
    # password at any time (no old password needed).
    CREATABLE_ROLES = (User.Role.DEALER, User.Role.PILOT)

    def validate_phone(self, value):
        value = (value or "").strip()
        if value and not re.fullmatch(r"\+?[0-9][0-9 \-]{8,18}[0-9]", value):
            raise serializers.ValidationError("Enter a valid phone number (10–15 digits).")
        return value

    def validate(self, attrs):
        if self.instance is None:
            if attrs.get("role", User.Role.DEALER) not in self.CREATABLE_ROLES:
                raise serializers.ValidationError({"role": "New accounts must be a dealer or a pilot."})
            if not attrs.get("phone"):
                raise serializers.ValidationError({"phone": "Phone number is required."})
            if not attrs.get("password"):
                raise serializers.ValidationError({"password": "Password is required."})
        elif "role" in attrs and attrs["role"] != self.instance.role:
            raise serializers.ValidationError({"role": "A user's role can't be changed."})
        if "password" in attrs and attrs["password"] and len(attrs["password"]) < 8:
            raise serializers.ValidationError({"password": "Use at least 8 characters."})
        return attrs

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
