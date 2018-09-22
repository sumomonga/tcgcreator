"""mysite URL Configuration

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
from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import LoginView, logout_then_login,LogoutView
from tcgcreator import views

urlpatterns = [
    url(r'^admin/tcgcreator/field/$',views.field_list_view,name='field_list_view'),
    url(r'^admin/tcgcreator/pac/(?P<pac_id>\d+)/diagram',views.pac_diagram),
    url(r'^admin/tcgcreator/trigger/(?P<trigger_id>\d+)/diagram',views.trigger_diagram),
    url(r'^admin/tcgcreator/defaultdeck/$',views.default_deck,name='defaultdeck'),
    url(r'^admin/', admin.site.urls),
    url(r'^tcgcreator/', include('tcgcreator.urls')),
    url(r'^gameuser/', include('gameuser.urls')),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

	
]
