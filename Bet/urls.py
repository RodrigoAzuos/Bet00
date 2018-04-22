from django.conf.urls import include, url
#from material.frontend import urls as frontend_urls
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Examples:
    # url(r'^$', 'Bet.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
 #   url(r'', include(frontend_urls)),
    url(r'^admin/login/$', auth_views.login, {'template_name': "login.html"}, name='login'),
    url(r'^admin/logout/$', auth_views.logout, {'template_name': "login.html"}, name='logout'),


]
