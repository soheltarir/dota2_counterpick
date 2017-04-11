import dota2api
from django.conf import settings
from django.http import HttpResponse


# Create your views here.


def get_match_history(request):
    api = dota2api.Initialise(settings.STEAM_API_KEY)
    res = api.get_match_history(game_mode=1)
    return HttpResponse(content=res)
