from django.contrib import admin
from django.urls import path, include

from accounts.public_views import public_profile_page
from payments.views import start_payment, payment_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('p/<str:slug>/', public_profile_page, name='public-profile-page'),
    path('pay/<uuid:reference_code>/start/', start_payment, name='payment-start'),
    path('pay/<uuid:reference_code>/callback/', payment_callback, name='payment-callback'),
]
