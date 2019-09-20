from django.conf.urls import url

from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

app_name = 'core'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', LoginView.as_view(template_name='core/login.html'), name='login'),
    url(r'^logout/$', LogoutView.as_view(next_page='core:login'), name='logout'),

    url(r'^updateSwitch/(?P<switch_id>\d+)/(?P<force>\d)$', views.updateSwitch, name="updateSwitch"),
    url(r'^decableSwitch/(?P<switch_id>\d+)$', views.decableSwitch, name="decableSwitch"),

       
    url(r'^money$', views.money, name="money"),

]
