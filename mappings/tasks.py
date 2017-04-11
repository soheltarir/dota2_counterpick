import calendar
from datetime import datetime, timedelta

import dota2api
from celery import shared_task
from django.conf import settings

from heroes.models import DotaHero
from mappings.models import VersusHero, WithHero


class GetMatchHistory:
    limit = 50
    total_iterations = 1

    def __init__(self, from_day=2, to_day=1):
        assert from_day > to_day, "Error"

        date_max = datetime.today() - timedelta(days=to_day)
        date_min = datetime.today() - timedelta(days=from_day)
        self.date_max = calendar.timegm(date_max.utctimetuple())
        self.date_min = calendar.timegm(date_min.utctimetuple())
        self.api = dota2api.Initialise(settings.STEAM_API_KEY)

    def get_match_ids(self, hero_id):
        print("Retrieving for Hero (ID: {0})".format(hero_id))
        iterations = 0
        start_at_match_id = None
        match_ids = []
        while iterations < self.total_iterations:
            print("Executing iteration {0} with start_at_match_id {1}".format(iterations, start_at_match_id))
            api_filters = {
                "start_at_match_id": start_at_match_id,
                "date_max": self.date_max,
                "date_min": self.date_min,
                "min_players": 10,
                "matches_requested": self.limit,
                "hero_id": hero_id
            }
            res = self.api.get_match_history(**api_filters)
            if res["status"] != 1:
                print("Failed to retrieve matches history, reason: {0}".format(res["statusDetail"]))
                break
            matches = res["matches"]
            if not len(matches):
                break
            start_at_match_id = matches[-1]["match_id"] - 1
            for match in matches:
                match_ids.append(match["match_id"])
            iterations += 1
        return match_ids


class GetHeroMatches:
    def __call__(self):
        hero_matches = {}
        hero_ids = list(DotaHero.objects.values_list('id', flat=True))
        for hero_id in hero_ids:
            hero_matches[hero_id] = GetMatchHistory().get_match_ids(hero_id)
        return hero_matches


class GetMatchDetails:
    no_of_retries = 5
    player_fields = [
        "hero_id", "kills", "deaths", "assists", "hero_damage", "tower_damage", "hero_healing",
        "gold_per_min", "xp_per_min"
    ]

    def __init__(self, match_id):
        self.api = dota2api.Initialise(settings.STEAM_API_KEY)
        self.results = self.api.get_match_details(match_id=match_id)
        self.radiant_win = self.results["radiant_win"]
        self.is_valid = True
        self.players = {
            "radiant": [],
            "dire": []
        }
        self.game_mode = self.results["game_mode"]

    def get_player_details(self):
        for player in self.results["players"]:
            if player["leaver_status"] != 0:
                self.is_valid = False
                return
            player_slot = '{0:08b}'.format(player["player_slot"])
            if int(player_slot[0]) == 0:
                team = "radiant"
            else:
                team = "dire"
            data = {}
            for field in self.player_fields:
                data[field] = player.get(field)
            self.players[team].append(data)


class StoreMapping:
    @staticmethod
    def print(message, match_id=None, message_type="INFO"):
        if match_id:
            print("[StoreMapping][MatchID:{0}] {2} :: {1}".format(match_id, message, message_type))
        else:
            print("[StoreMapping] {1} :: {0}".format(message, message_type))

    def print_warn(self, message, match_id=None):
        self.print(message, match_id, "*WARN*")

    def print_error(self, message, match_id=None):
        self.print(message, match_id, "**ERROR**")

    @shared_task
    def create_versus_mapping(self, hero_data, enemies, is_win, game_mode):
        hero_id = hero_data.pop("hero_id")
        for enemy in enemies:
            if not enemy.get("hero_id"):
                continue
            versus_mapping, created = VersusHero.objects.get_or_create(hero_id=hero_id, versus_hero_id=enemy["hero_id"])
            if is_win:
                versus_mapping.add_a_win(game_mode=game_mode, **hero_data)
                print("Adding a Win mapping for {0} against {1}".format(hero_id, enemy["hero_id"]))
            else:
                versus_mapping.add_a_loss(game_mode=game_mode, **hero_data)
                print("Adding a Loss mapping for {0} against {1}".format(hero_id, enemy["hero_id"]))

    @shared_task
    def create_with_mapping(self, hero_data, allies, is_win, game_mode):
        hero_id = hero_data.pop("hero_id")
        for ally in allies:
            if not ally.get("hero_id"):
                continue
            with_mapping, created = WithHero.objects.get_or_create(hero_id=hero_id, with_hero_id=ally["hero_id"])
            if is_win:
                with_mapping.add_a_win(game_mode=game_mode, **hero_data)
                print("Adding a Win mapping for {0} with {1}".format(hero_id, ally["hero_id"]))
            else:
                with_mapping.add_a_loss(game_mode=game_mode, **hero_data)
                print("Adding a Loss mapping for {0} with {1}".format(hero_id, ally["hero_id"]))

    def create_mapping(self, player_details, radiant_win, game_mode):
        radiant_players, dire_players = player_details["radiant"], player_details["dire"]
        for radiant_player in radiant_players:
            self.create_versus_mapping.apply_async((self, radiant_player, dire_players, radiant_win, game_mode),
                                                   countdown=1)
            self.create_with_mapping.apply_async((self, radiant_player, radiant_players, radiant_win, game_mode),
                                                 countdown=1)
        for dire_player in dire_players:
            self.create_versus_mapping.apply_async((self, dire_player, radiant_players, not radiant_win, game_mode),
                                                   countdown=1)
            self.create_with_mapping.apply_async((self, dire_player, dire_players, not radiant_win, game_mode),
                                                 countdown=1)

    @shared_task(default_retry_delay=1 * 60, max_retries=5)
    def get_and_store_match_details(self, match_id):
        try:
            match_detail = GetMatchDetails(match_id=match_id)
        except ConnectionError as ex:
            self.print_error("Failed to retrieve match details, will retry after some time.")
            raise self.get_and_store_match_details.retry(args=(self, match_id), exc=ex)
        self.print("Retrieved match details", match_id=match_id)
        match_detail.get_player_details()
        if not match_detail.is_valid:
            self.print_warn("Match is not valid.", match_id=match_id)
            return
        self.create_mapping(match_detail.players, match_detail.radiant_win, match_detail.game_mode)

    def __call__(self):
        hero_matches = GetHeroMatches().__call__()
        # Only get unique match_ids
        unique_match_ids = set()
        for match_ids in hero_matches.values():
            unique_match_ids.update(match_ids)
        for match_id in unique_match_ids:
            self.get_and_store_match_details.apply_async((self, match_id), countdown=1)
