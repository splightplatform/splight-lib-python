from django.urls import path, include
from .views import asset_router
urlpatterns = [
    path('assets/', include(asset_router.urls)),
]
