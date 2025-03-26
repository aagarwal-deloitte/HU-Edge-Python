"""newproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from split_it_app.views import RegisterApi, LoginApi, UserApi, OccasionApi


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('split_it_app/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'split_it_app/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger'
    ),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('split_it_app/register/', RegisterApi.as_view(), name = 'register_users'),
    path('split_it_app/login/', LoginApi.as_view(), name = 'login_users'),
    
    path('split_it_app/users/', UserApi.as_view(), name = 'get_users'),  
    
    path('split_it_app/occasion/', OccasionApi.as_view(), name = 'occasion-view-create'),
]
