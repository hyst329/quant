from django.conf.urls import url


from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^userprofile/$', views.userprofile, name='userprofile'),
    url(r'^tempeditor/$', views.tempeditor, name='tempeditor'),
    url(r'^temprender/$', views.temprender, name='temprender'),
    url(r'^tempsave/$', views.tempsave, name='tempsave'),
    url(r'^pages/(?P<user_id>[0-9]+)-(?P<user_name>\w+)/(?P<page_id>[0-9]+)-(?P<page_name>\w+)$',
            views.pagerender, name='pagerender')
]
