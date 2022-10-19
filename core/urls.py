from django.urls import re_path

from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

app_name = 'core'

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^login/$', LoginView.as_view(template_name='core/login.html'), name='login'),
    re_path(r'^logout/$', LogoutView.as_view(next_page='core:login'), name='logout'),

    re_path(r'^updateSwitch/(?P<switch_id>\d+)/(?P<force>\d)$', views.updateSwitch, name="updateSwitch"),
    re_path(r'^dismountSwitch/(?P<switch_id>\d+)$', views.dismountSwitch, name="dismountSwitch"),

]
