from django.conf.urls import url

from heroes.views import get_match_history

urlpatterns = [
    url(r'^get_match_history/', get_match_history),
]
