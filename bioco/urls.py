from django.conf.urls import include
from django.urls import path, re_path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()
from django.contrib.auth.views import LoginView
from juntagrico.views import home as jhome
import bioco.views
from juntagrico.config import Config
from juntagrico import views_subscription as juntagrico_subscription
from django.views.generic.base import RedirectView

#handler500 = Custom500View.as_view()

urlpatterns = [
    # TODO The original view goes only to +14 days, but then we often get an empty list because everything is booked out
    path('', bioco.views.home, name='home'),   
    path('my/home', bioco.views.home, name='home'),

    re_path('^$', jhome),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url=Config.favicon(), permanent=True)),

#    re_path(r'^info/date$', date),

    re_path(r'^', include('juntagrico.urls')),
    re_path(r'^impersonate/', include('impersonate.urls')),

    re_path(r'^accounts/login/$', LoginView.as_view()),

    re_path(r'^',include('juntagrico_billing.urls')),
#    re_path(r'^',include('juntagrico_pg.urls')),

#    re_path(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
#    re_path(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),

#    re_path(r'^openidinit$', openid_init),
#    re_path(r'^', include('juntagrico_webdav.urls')),
	
#    re_path(r'^', include('juntagrico_polling.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # re_path(r'^admin/doc/', include('django.contrib.admindocs.urls)),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls),

    # backwards compatibility, can be deleted at some point
    re_path(r'^my/anmelden/', juntagrico_subscription.SignupView.as_view(), name='signup'),

    # workaround: on the fly generated PDF
    re_path(r'^depot_overview_html', bioco.views.depot_overview_direct, name='bioco-depot-overview-direct'),

    # workaround: all deliveries (not filtered to day or own subscription type)
    re_path('my/all_deliveries', bioco.views.deliveries, name='bioco-all-deliveries'),  #
]
