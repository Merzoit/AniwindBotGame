#################
#
# Imports
#
#################
from django.contrib import admin
from django.urls import path
from core.views import *

#################
#
# PATTERNS
#
#################

urlpatterns = [
    ######################VIEWS######################
    path('', UserProfileView.as_view(), name='user-detail'),
    path('user/inventory/', UserInventoryView.as_view(), name='user-inventory'),
    path('user/collection/', CollectionView.as_view(), name='user-collection'),
    path('user/deck/', DeckView.as_view(), name='user-deck'),
    path('arena/', ArenaView.as_view(), name='arena'),
    path('rating/', RatingView.as_view(), name='rating'),
    path('help/', HelpView.as_view(), name='help'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('newcard/<int:id>/', NewCardView.as_view(), name='new-card'),
    path('arena/mm/', MMView.as_view(), name='mm'),
    path('fight/', Fight.as_view(), name='fight'),
    path('db/', DbView.as_view(), name='db'),
    path('quest/', QuestView.as_view(), name='quest'),

    ######################METHODS######################
    path('user/fd/<int:user>/<str:slot_name>/', UpdateFightDeckSlotView.as_view(), name='update-fight-deck-slot'),
    path('user/ad/<int:amulet>/', UpdateAmuletSlotView.as_view(), name='update-amulet-slot'),
    path('auth/', tg_auth, name='tg_auth'),
    path('remove_from_queue/', remove_from_queue, name='remove_from_queue'),
    path('reset_deck/', reset_deck, name='reset_deck'),
    path('reset_amulet/', reset_amulet, name='reset_amulet'),
    path('sell-card/<str:red>/', card_sell, name='card-sell'),
    path('purchase/', purchase_item, name='purchase-item'),
    path('open/<int:slot_id>/<int:user_id>/', open_box, name='open_box'),
    path('join_queue/', join_queue, name='join_queue'),
    path('completed_quest/<int:id>/', complete_quest, name='complete_quest'),
    path('take_quest', take_quest, name='take_quest'),
    path('take_daily_quest', take_daily_quest, name='take_daily_quest'),
    path('item_sell/<int:slot_id>/', item_sell, name='item_sell'),
    path('add_friend', add_friend, name='add_friend'),
    path('remove_friend', remove_friend, name='remove_friend'),
    path('get_duel', get_duel, name='get_duel'),

    ######################API######################
    path('api/cards/', CardsListView.as_view(), name='cards-list'),
    path('api/cards/<int:pk>/', CardDetailView.as_view(), name='card-detail'),
    path('api/fight/<int:pk>/', FightDetailView.as_view(), name='fight-detail'),
    path('api/fightdata/<int:pk>/', FightDataUpdate.as_view(), name='fightdata-update'),
    path('api/csrf_token/', csrf_token, name='csrf_token'),
    path('api/users/', UserProfileList.as_view(), name='user-list'),
    path('api/users/<int:pk>/', UserProfileDetail.as_view(), name='user-detail'),
]
