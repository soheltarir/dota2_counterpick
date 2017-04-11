from django.db import models

# Create your models here.
from django_extensions.db.models import TimeStampedModel

from mappings.constants import GameModes, WIN_LOSS_FIELD_MAPPING


class GameResultMeta(TimeStampedModel):
    game_mode = models.PositiveSmallIntegerField(choices=GameModes.choices, default=GameModes.ALL_PICK,
                                                 validators=[GameModes.validator])
    count = models.PositiveIntegerField(default=0, verbose_name="Total no. of wins")
    average_gpm = models.PositiveIntegerField(default=0, verbose_name="Average Gold per Min against that hero")
    average_xpm = models.PositiveIntegerField(default=0, verbose_name="Average Experience per Min against that hero")
    average_kills = models.PositiveIntegerField(default=0)
    average_deaths = models.PositiveIntegerField(default=0)
    average_assists = models.PositiveIntegerField(default=0)
    average_hero_damage = models.PositiveIntegerField(default=0)
    average_hero_healing = models.PositiveIntegerField(default=0)
    average_tower_damage = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "mappings"
        abstract = True


class Wins(GameResultMeta):
    class Meta:
        app_label = "mappings"
        db_table = "hero_wins"


class Losses(GameResultMeta):
    class Meta:
        app_label = "mappings"
        db_table = "hero_losses"


class MappingMeta(TimeStampedModel):
    hero = models.ForeignKey('heroes.DotaHero', related_name='+', on_delete=models.CASCADE)
    wins = models.OneToOneField('mappings.Wins', related_name='+', on_delete=models.CASCADE, null=True)
    losses = models.OneToOneField('mappings.Losses', related_name='+', on_delete=models.CASCADE, null=True)

    class Meta:
        app_label = "mappings"
        abstract = True

    def add_a_win(self, game_mode, **kwargs):
        # Change the kwargs according to the Model's field names
        data = {}
        for key, value in kwargs.items():
            data[WIN_LOSS_FIELD_MAPPING[key]] = value
        if not self.wins:
            wins = Wins.objects.create(count=1, game_mode=game_mode, **data)
            self.wins = wins
            self.save()
        else:
            wins = self.wins
        fields = [x.name for x in Wins._meta.get_fields() if x.name.startswith("average_")]
        for field in fields:
            prev_total = getattr(wins, field, 0) * wins.count
            new_value = (prev_total + data.get(field, 0))/(wins.count + 1)
            setattr(wins, field, new_value)
        wins.count += 1
        wins.save()

    def add_a_loss(self, game_mode, **kwargs):
        # Change the kwargs according to the Model's field names
        data = {}
        for key, value in kwargs.items():
            data[WIN_LOSS_FIELD_MAPPING[key]] = value
        if not self.losses:
            losses = Losses.objects.create(count=1, game_mode=game_mode, **data)
            self.losses = losses
            self.save()
        else:
            losses = self.losses
        fields = [x.name for x in Losses._meta.get_fields() if x.name.startswith("average_")]
        for field in fields:
            prev_total = getattr(losses, field, 0) * losses.count
            new_value = (prev_total + data.get(field, 0))/(losses.count + 1)
            setattr(losses, field, new_value)
        losses.count += 1
        losses.save()


class VersusHero(MappingMeta):
    versus_hero = models.ForeignKey('heroes.DotaHero', related_name='+', on_delete=models.CASCADE)

    class Meta:
        app_label = "mappings"
        db_table = "versus_mappings"
        unique_together = ('hero', 'versus_hero')

    def __str__(self):
        return "{0} vs. {1}".format(self.hero.popular_name, self.versus_hero.popular_name)


class WithHero(MappingMeta):
    with_hero = models.ForeignKey('heroes.DotaHero', related_name='+', on_delete=models.CASCADE)

    class Meta:
        app_label = "mappings"
        db_table = "with_mappings"
        unique_together = ('hero', 'with_hero')

    def __str__(self):
        return "{0} vs. {1}".format(self.hero.popular_name, self.with_hero.popular_name)
