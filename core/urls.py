from django.conf.urls import url

from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, { 'template_name': 'core/login.html' }, name='login'),
    url(r'^logout/$', auth_views.logout, { 'next_page': 'core:login' }, name='logout'),

    url(r'^updateSwitch/(?P<switch_id>\d+)/(?P<force>\d)$', views.updateSwitch, name="updateSwitch"),
    url(r'^decableSwitch/(?P<switch_id>\d+)$', views.decableSwitch, name="decableSwitch"),

       
    url(r'^money$', views.money, name="money"),

]
