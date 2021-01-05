from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()
from django.contrib.auth.views import LoginView
#from .views import Custom500View, error, politoloco_profile, beipackzettel_profile, openid_init, date
from juntagrico.views import home as jhome
import bioco.views
from juntagrico.config import Config
from juntagrico import views_subscription as juntagrico_subscription
from django.views.generic.base import RedirectView

#handler500 = Custom500View.as_view()

urlpatterns = [
#	url('^500$', Custom500View.as_view()),    
#	url('^500/test$',error),
    
    url('^$', jhome),
    url(r'^favicon\.ico$', RedirectView.as_view(url=Config.favicon(), permanent=True)),

#    url(r'^info/date$', date),
	
#    url(r'^politoloco/profile$', politoloco_profile),
#    url(r'^beipackzettel/profile$', beipackzettel_profile),

    url(r'^', include('juntagrico.urls')),
    url(r'^impersonate/', include('impersonate.urls')),

    url(r'^accounts/login/$', LoginView.as_view()),

#    url(r'^',include('juntagrico_billing.urls')),
#    url(r'^',include('juntagrico_pg.urls')),

    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
#    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),

#    url(r'^openidinit$', openid_init),
#    url(r'^', include('juntagrico_webdav.urls')),
	
#    url(r'^', include('juntagrico_polling.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls)),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),

    # backwards compatibility, can be deleted at some point
    url(r'^my/anmelden/', juntagrico_subscription.SignupView.as_view(), name='signup'),

    # workaround: on the fly generated PDF
    url(r'^depot_overview_html', bioco.views.depot_overview_direct, name='bioco-depot-overview-direct'),

    # workaround: all deliveries (not filtered to day or own subscription type)
    url('my/all_deliveries', bioco.views.deliveries, name='bioco-all-deliveries'),  #
]
