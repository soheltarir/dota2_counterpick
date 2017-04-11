import dota2api
from django.conf import settings
from django.db import transaction

from heroes.models import DotaHero


@transaction.atomic
def run():
    api = dota2api.Initialise(settings.STEAM_API_KEY)
    response = api.get_heroes()
    if response["status"] != 200:
        print("Failed to retrieve hero list.")
        return
    for hero_data in response["heroes"]:
        try:
            DotaHero.objects.create(
                id=hero_data["id"], popular_name=hero_data["localized_name"], system_name=hero_data["name"],
                image=hero_data["url_full_portrait"]
            )
            print("Successfully created Hero \'{0}\'".format(hero_data["name"]))
        except Exception as ex:
            print("Failed to create Hero \'{0}\', reason: {1}".format(hero_data["name"], str(ex)))
            continue
