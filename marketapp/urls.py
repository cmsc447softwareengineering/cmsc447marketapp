from django.conf.urls import include, url #patterns

from views import HomePageView
from views import CreateUserView
from views import MainFeedView
from views import LoginView
from django.contrib import admin
admin.autodiscover()

urlpatterns = [ #patterns('',
    # Examples:
    # url(r'^$', 'marketapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', MainFeedView.as_view(), name='home'),
	url(r'^createuser', CreateUserView.as_view(), name='usercreate'),
	url(r'^feed', MainFeedView.as_view(), name='feed'),
	url(r'^login', LoginView.as_view(), name='login'),
]#)
