from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'warara.mobile.main.views.main'),
)
