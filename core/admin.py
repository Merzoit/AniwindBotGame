#################
#
# Imports
#
#################
from django.contrib import admin
from core.models import (
    FightDeck,
    Queue,
    Shop,
    FightData,
    Season,
    Cards,
    Capabilities,
    Elements,
    Universe,
    UserProfile,
    UserCards,
    AbilityStage,
    Inventory,
    Items,
    ItemTypes,
    InventorySlot,
    UserStatus,
    Equipment,
    UserStatistic,
    Quest,
    UserQuests,
    DuelRequests
)


#################
#
# Resources
#
#################
class CardsAdmin(admin.ModelAdmin):
    """
    Admin panel for cards
    """
    list_display = (
        'id', 'name', 'universe',
        'ability', 'element', 'hp_min',
        'hp_max', 'str_min', 'str_max', 'url'
    )
    list_filter = ('universe', 'element')


class CapabilitiesAdmin(admin.ModelAdmin):
    """
    Admin panel for capabilities
    """
    list_display = ('id', 'name', 'description', 'stage')
    list_filter = ('stage',)


class ElementsAdmin(admin.ModelAdmin):
    """
    Admin panel for elements
    """
    list_display = ('id', 'name')


class UniverseAdmin(admin.ModelAdmin):
    """
    Admin panel for universe
    """
    list_display = ('id', 'name')


class UserAdmin(admin.ModelAdmin):
    """
    Admin panel for user profile
    """
    list_display = (
        'id', 'statistic',
        'inventory', 'deck',
        'equipment'
    )


class UserCardsAdmin(admin.ModelAdmin):
    """
    Admin panel for user cards
    """
    list_display = ('id', 'user', 'card', 'hp', 'str')
    list_filter = ('card',)


class FightAdmin(admin.ModelAdmin):
    """
    Admin panel for fights
    """
    list_display = ('id', 'get_user_first', 'get_user_second', 'status')
    list_filter = ('status',)
    search_fields = (
        'id',
        'user_first__id', 'user_first__username',
        'user_second__id', 'user_second__username',
    )

    def get_user_first(self, obj):
        return "{}({})".format(obj.user_first.user, obj.user_first.id)

    def get_user_second(self, obj):
        return "{}({})".format(obj.user_second.user, obj.user_second.id)

    get_user_first.short_description = 'Первый пользователь'
    get_user_second.short_description = 'Второй пользователь'


class InventoryAdmin(admin.ModelAdmin):
    """
    Admin panel for inventory
    """
    list_display = ('id', 'userprofile', 'gold', 'diamond', 'scalp')
    search_fields = ('id',)


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'vault')
    search_fields = ('id', 'item__id', 'vault', 'item__name', 'item__sell_price')


class EquipAdmin(admin.ModelAdmin):
    list_display = ('id', 'amulet', 'userprofile')


class QueueAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'user', 'add_time')
    search_fields = ('id', 'user__id', 'userprofile',)

class FightDeckAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'userprofile', 'first_card', 'second_card', 'third_card')
    search_fields = ('id',)
    list_filter = ('first_card__card', 'second_card__card', 'third_card__card')

class InventorySlotAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'item', 'count')
    search_fields = ('id', 'item')
    list_filter = ('item',)

class ItemsAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'name', 'type', 'universe', 'description', 'sell_price')
    search_fields = ('id', 'name')
    list_filter = ('type', 'universe')

class ItemsTypeAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'name',)
    search_fields = ('id', 'name')

class UserStatusAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'status',)
    search_fields = ('id', 'status')

class AbilityStageAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'name',)
    search_fields = ('id', 'name')

class UserStatisticAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'username', 'reg_date', 'status', 'win', 'lose', 'daily')
    search_fields = ('id', 'username',)
    list_filter = ('status',)

class QuestAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'name', 'end_point', 'coins', 'item', 'daily', 'description')
    search_fields = ('id', 'name',)
    list_filter = ('item', 'daily')

class UserQuestAdmin(admin.ModelAdmin):
    """
    Admin panel for queue
    """
    list_display = ('id', 'quest', 'progress', 'completed',)
    search_fields = ('id',)
    list_filter = ('completed', 'quest',)

admin.site.register(Cards, CardsAdmin)
admin.site.register(Capabilities, CapabilitiesAdmin)
admin.site.register(Elements, ElementsAdmin)
admin.site.register(Universe, UniverseAdmin)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(UserCards, UserCardsAdmin)
admin.site.register(Season)
admin.site.register(AbilityStage, AbilityStageAdmin)
admin.site.register(FightData, FightAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Queue, QueueAdmin)
admin.site.register(FightDeck, FightDeckAdmin)
admin.site.register(InventorySlot, InventorySlotAdmin)
admin.site.register(Items, ItemsAdmin)
admin.site.register(ItemTypes, ItemsTypeAdmin)
admin.site.register(UserStatus, UserStatusAdmin)
admin.site.register(Equipment, EquipAdmin)
admin.site.register(UserStatistic, UserStatisticAdmin)
admin.site.register(Quest, QuestAdmin)
admin.site.register(UserQuests, UserQuestAdmin)
admin.site.register(DuelRequests)