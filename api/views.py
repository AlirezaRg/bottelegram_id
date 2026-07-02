from rest_framework import viewsets, permissions, status as http_status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404

from accounts.models import TelegramUser, VerificationRequest
from trust.models import TrustProfile, Report, TrustScoreEvent
from ads.models import Ad
from payments.models import Payment

from .serializers import (
    TelegramUserSerializer, VerificationRequestSerializer,
    PublicProfileSerializer, ReportSerializer, AdSerializer, PaymentSerializer,
)


class BotAPIKeyPermission(permissions.BasePermission):
    """
    Simple shared-secret auth for the bot service (not for public clients).
    The bot sends header: X-Bot-Api-Key: <key from settings>.
    Swap for OAuth2/JWT later if multiple services need access.
    """

    def has_permission(self, request, view):
        from django.conf import settings
        key = request.headers.get("X-Bot-Api-Key")
        return bool(key) and key == settings.BOT_API_KEY


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [BotAPIKeyPermission]
    lookup_field = "telegram_id"

    @action(detail=False, methods=["post"], url_path="get-or-create")
    def get_or_create(self, request):
        """Bot calls this on /start to register or fetch the user."""
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response({"detail": "telegram_id required"}, status=http_status.HTTP_400_BAD_REQUEST)

        user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": request.data.get("username", ""),
                "first_name": request.data.get("first_name", ""),
                "last_name": request.data.get("last_name", ""),
            },
        )
        TrustProfile.objects.get_or_create(user=user)
        serializer = self.get_serializer(user)
        return Response({"created": created, "user": serializer.data})

    @action(detail=False, methods=["get"], url_path="by-username/(?P<username>[^/.]+)")
    def by_username(self, request, username=None):
        """
        Bot calls this to resolve @username -> internal user id when filing
        a report. Only works for users who have interacted with the bot
        before (we have no way to look up Telegram users we've never seen).
        """
        username = username.lstrip("@")
        user = TelegramUser.objects.filter(username__iexact=username).first()
        if not user:
            return Response(
                {"detail": "user_not_found"},
                status=http_status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="status/(?P<telegram_id>[^/.]+)")
    def my_status(self, request, telegram_id=None):
        """Bot calls this for the 'وضعیت من / امتیاز من' button."""
        user = get_object_or_404(TelegramUser, telegram_id=telegram_id)
        latest_verification = user.verification_requests.order_by("-submitted_at").first()
        trust_profile = getattr(user, "trust_profile", None)

        return Response({
            "verification_status": latest_verification.status if latest_verification else "not_submitted",
            "trust_score": trust_profile.score if trust_profile else 0,
            "total_reports_against": trust_profile.total_reports_against if trust_profile else 0,
            "public_slug": user.public_slug,
        })


class VerificationRequestViewSet(viewsets.ModelViewSet):
    queryset = VerificationRequest.objects.all()
    serializer_class = VerificationRequestSerializer
    permission_classes = [BotAPIKeyPermission]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [BotAPIKeyPermission]

    def perform_create(self, serializer):
        report = serializer.save()
        target_profile, _ = TrustProfile.objects.get_or_create(user=report.target)
        target_profile.total_reports_against += 1
        target_profile.save(update_fields=["total_reports_against"])
        TrustScoreEvent.objects.create(
            user=report.target,
            reason=TrustScoreEvent.Reason.REPORT_RECEIVED,
            delta=0,  # no score hit until an admin confirms it
            note=f"Report filed by {report.reporter}",
        )


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [BotAPIKeyPermission]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [BotAPIKeyPermission]

    @action(detail=False, methods=["post"], url_path="create-and-get-link")
    def create_and_get_link(self, request):
        """
        Bot calls this when a user needs to pay for something. Returns a
        ready-to-send payment URL the bot can drop straight into a message
        — the actual Zarinpal redirect/verify dance happens entirely on
        the web side (see payments/views.py), the bot doesn't need to
        know any gateway details.
        """
        from django.urls import reverse

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        link = request.build_absolute_uri(
            reverse("payment-start", kwargs={"reference_code": payment.reference_code})
        )
        return Response({"payment": serializer.data, "payment_url": link})


class PublicProfileView(RetrieveAPIView):
    """
    The page/endpoint behind the shareable verification link.
    No auth needed — this is meant to be public (e.g. /p/<slug>/).
    """

    queryset = TelegramUser.objects.all()
    serializer_class = PublicProfileSerializer
    lookup_field = "public_slug"
    lookup_url_kwarg = "slug"
    permission_classes = [permissions.AllowAny]
