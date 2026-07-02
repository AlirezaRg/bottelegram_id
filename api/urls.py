from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    TelegramUserViewSet, VerificationRequestViewSet,
    ReportViewSet, AdViewSet, PaymentViewSet, PublicProfileView,
)

router = DefaultRouter()
router.register("users", TelegramUserViewSet)
router.register("verifications", VerificationRequestViewSet)
router.register("reports", ReportViewSet)
router.register("ads", AdViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("public/<str:slug>/", PublicProfileView.as_view(), name="public-profile"),
]
