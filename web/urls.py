from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# Example:
	# (r'^psrc/', include('psrc.foo.urls')),
	(r'^$', 'psrc.analysis.views.analysis_router'),
	(r'^restart/$', 'psrc.analysis.views.restart'),
	(r'^region/add/$', 'psrc.analysis.views.add_region'),
	(r'^benefits_csv/$', 'psrc.analysis.views.benefits_csv'),
	(r'^accounting_csv/$', 'psrc.analysis.views.accounting_csv'),
	(r'^safety_csv/$', 'psrc.analysis.views.safety_csv'),
	(r'^emissions_csv/$', 'psrc.analysis.views.emissions_csv'),
	#(r'^analysis/$', 'psrc.analysis.views.analysis'),
	# Uncomment this for admin:
	 (r'^admin/', include('django.contrib.admin.urls')),
)
