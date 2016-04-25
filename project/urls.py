"""
Definition of urls for project.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

#import tests.forms
import tests.views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', tests.views.lobby, name='lobby'),
    url(r'^login/$', tests.views.login, name='login'),
    url(r'^createtest/$', tests.views.create_test, name='create_test'),
    url(r'^edittest/(?P<test_id>[0-9]+)/$', tests.views.create_test, name='edit_test'),
    url(r'^taketest/(?P<test_id>[0-9]+)/$', tests.views.take_test, name='take_test'),
    
    url(r'^updateteacher$', tests.views.update_teacher, name='update_teacher'),
    url(r'^updatestudent$', tests.views.update_student, name='update_student'),
    # Examples:
    #url(r'^$', app.views.home, name='home'),
    #url(r'^contact$', app.views.contact, name='contact'),
    #url(r'^about', app.views.about, name='about'),
    #url(r'^login/$',
    #    django.contrib.auth.views.login,
    #    {
    #        'template_name': 'app/login.html',
    #        'authentication_form': app.forms.BootstrapAuthenticationForm,
    #        'extra_context':
    #        {
    #            'title': 'Log in',
    #            'year': datetime.now().year,
    #        }
    #    },
    #    name='login'),
    #url(r'^logout$',
    #    django.contrib.auth.views.logout,
    #    {
    #        'next_page': '/',
    #    },
    #    name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]
