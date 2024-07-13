#################
#
# Imports
#
#################
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from core.models import Queue, FightData, UserProfile, FightDeck, UserCards
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random
import json
from core.models import UserStatus
#################
#
# Tasks
#
#################
nicks = [
    "Only you",
    "~Planokyp~",
    "ALekcangp-",
    "Anen",
    "Beabandis",
    "Bonkers",
    "Turg",
    "GoMeR",
    "hOmE.cFg",
    "Триша",
    "KoJlyM6uuckuu_6apoH",
    "Это Был Не Нескафе",
    "Круглый в карты проигрался",
    "Cs-Fannat|Diamond",
    "Группа Крови",
    "VorobeJ",
    "Dairg",
    "Skillet",
    "legenda17",
    "PTPPlayMan",
    "Джафар с Востока",
    "OgblH",
    "Alsara",
    "Be4Ho_6yxou",
    "3a4ap",
    "BupKub",
    "H.u.LLl.T.9l.k",
    "Carmelo",
    "PASHA",
    "Hurin",
    "BTopIIIeHue_B_CPAkoTaH",
    "Burgas",
    "CeP6_MHe_kAk_D04b",
    "scoop",
    "Dameena",
    "d3mOS?!JokerKannibal",
    "Gangster",
    "Har/la9IMopDa",
    "XoRoIIIuu",
    "Adoranin",
    "КоТэ С NoЖом",
    "86)}I{el[t]blu",
    "ГорячаяЛегенда",
    "Starix",
    "ZM(sas)doc",
    "kiler",
    "Light Soul",
    "Lino4ka",
    "SK.Ob*eBOO:S3aBDB",
    "==AHAPXOTYPUC=="
]

@shared_task
def check_and_start_battle():
    """
    Checks that the user has entered the battle and starts the fight
    """
    with transaction.atomic():
        now = timezone.now()
        queue = Queue.objects.select_for_update().order_by('add_time')

        while queue.count() >= 2:
            player1 = queue[0].user
            player2 = queue[1].user
            array = [random.randint(0, 99) for _ in range(100)]
            FightData.objects.create(
                user_first=player1, user_second=player2,
                array=array, status=True
            )

            queue[0].delete()
            queue[0].delete()

            queue = Queue.objects.select_for_update().order_by('add_time')

        if queue.exists() and queue.count() == 1:
            player = queue[0].user
            joined_at = queue[0].add_time

            if (now - joined_at).total_seconds() > 10:
                bot = UserProfile.objects.get(id=100)
                deck2 = bot.deck
                cards = list(UserCards.objects.all())
                deck2.first_card, deck2.second_card, deck2.third_card = random.sample(cards, 3)
                deck2.save()
                nick = random.choice(nicks)
                bot.statistic.username = nick
                bot.statistic.save()

                array = [random.randint(0, 99) for _ in range(100)]
                FightData.objects.create(
                    user_first=player, user_second=bot, array=array, status=True
                )
                queue[0].delete()






