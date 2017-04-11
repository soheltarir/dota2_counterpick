from django.utils.translation import ugettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem


class GameModes(DjangoChoices):
    UNKNOWN = ChoiceItem(value=0, label=_("Unknown"))
    ALL_PICK = ChoiceItem(value=1, label=_("All Pick"))
    CAPTAINS_MODE = ChoiceItem(value=2, label=_("Captain's Mode"))
    RANDOM_DRAFT = ChoiceItem(value=3, label=_("Random Draft"))
    SINGLE_DRAFT = ChoiceItem(value=4, label=_("Single Draft"))
    ALL_RANDOM = ChoiceItem(value=5, label=_("All Random"))


WIN_LOSS_FIELD_MAPPING = {
    "gold_per_min": "average_gpm",
    "xp_per_min": "average_xpm",
    "kills": "average_kills",
    "deaths": "average_deaths",
    "assists": "average_assists",
    "hero_damage": "average_hero_damage",
    "hero_healing": "average_hero_healing",
    "tower_damage": "average_tower_damage"
}
