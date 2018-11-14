"""text_me_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from text_me_project.text_me_api import views
from rest_framework_jwt.views import obtain_jwt_token,refresh_jwt_token

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'kartusers', views.KartUsersViewSet)
router.register(r'bookings',views.BookingViewSet)
router.register(r'karts',views.KartViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_jwt_token), #route to be authenticated
    url(r'^api-token-auth-refresh/', refresh_jwt_token)#route to refresh our token
]

