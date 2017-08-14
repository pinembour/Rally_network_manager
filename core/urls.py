from django.conf.urls import url

from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, { 'template_name': 'core/login.html' }, name='login'),
    url(r'^logout/$', auth_views.logout, { 'next_page': 'core:login' }, name='logout'),

    url(r'^updateSwitchs/(?P<switch_id>\d+)$', views.updateSwitchs, name="updateSwitch")
]
