from rest_framework import serializers

from accounts.models import TelegramUser, VerificationRequest
from trust.models import TrustProfile, Report
from ads.models import Ad
from payments.models import Payment


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = [
            "id", "telegram_id", "username", "first_name", "last_name",
            "phone_number", "is_blocked", "public_slug", "created_at",
        ]
        read_only_fields = ["id", "public_slug", "created_at"]


class VerificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationRequest
        fields = [
            "id", "user", "full_name", "country", "city",
            "document_file_id", "selfie_file_id", "status",
            "admin_note", "submitted_at",
        ]
        read_only_fields = ["id", "status", "admin_note", "submitted_at"]


class TrustProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustProfile
        fields = ["score", "total_reports_against", "confirmed_reports_against", "last_recalculated"]


class PublicProfileSerializer(serializers.ModelSerializer):
    """What anyone clicking a user's shared verification link sees."""
    trust_score = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()

    class Meta:
        model = TelegramUser
        fields = ["username", "first_name", "public_slug", "trust_score", "verification_status"]

    def get_trust_score(self, obj):
        profile = getattr(obj, "trust_profile", None)
        return profile.score if profile else 0

    def get_verification_status(self, obj):
        latest = obj.verification_requests.order_by("-submitted_at").first()
        return latest.status if latest else "not_submitted"


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "reporter", "target", "reason", "evidence_file_id", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = [
            "id", "owner", "category", "title", "description",
            "origin", "destination", "travel_date", "available_weight_kg",
            "status", "created_at", "expires_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "user", "purpose", "amount_toman", "reference_code",
            "gateway", "status", "created_at", "paid_at",
        ]
        read_only_fields = ["id", "reference_code", "status", "created_at", "paid_at"]
