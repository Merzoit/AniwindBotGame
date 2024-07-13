from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Cards(models.Model):
    """
    The default card model contains complete information about the card.
    Contains the interval of indicators that the user may receive.
    """
    ##CARD STAT##
    element = models.ForeignKey('Elements', on_delete=models.CASCADE, verbose_name="Стихия")
    ability = models.ForeignKey('Capabilities', on_delete=models.CASCADE, verbose_name="Способность")
    universe = models.ForeignKey('Universe', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Вселенная")
    season = models.ForeignKey('Season', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Сезон")
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField('Название', max_length=255)
    url = models.CharField('Картинка', max_length=255)
    ##ROLL INTERVALS##
    hp_max = models.IntegerField('Максимальное хп', default=0)
    hp_min = models.IntegerField('Минимальное хп', default=0)
    str_max = models.IntegerField('Максимальный урон', default=0)
    str_min = models.IntegerField('Минимальный урон', default=0)

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = '1GAME: Карточки'

    def __str__(self):
        return self.name


class AbilityStage(models.Model):
    """
    Model of card ability stages.
    Determines at what point in the battle the ability should trigger.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Стадия способности'
        verbose_name_plural = '1GAME: Стадии способностей'

    def __str__(self):
        return str(self.name)


class Season(models.Model):
    """
    Season model.
    Contains information about the season.
    """
    id = models.IntegerField(primary_key=True)

    class Meta:
        verbose_name = 'Сезон'
        verbose_name_plural = '1GAME: Сезоны'

    def __str__(self):
        return str(self.id)


class Elements(models.Model):
    """
    Elements model.
    Contains information about the elements.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField('Название', max_length=255)

    class Meta:
        verbose_name = 'Стихия'
        verbose_name_plural = '1GAME: Стихии'

    def __str__(self):
        return self.name


class Capabilities(models.Model):
    """
    Capabilities model.
    Contains information about the capabilities.
    """
    stage = models.ForeignKey(
        'AbilityStage', on_delete=models.CASCADE,
        null=True, blank=True, verbose_name="Стадия боя"
    )
    id = models.IntegerField(primary_key=True)
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Способность'
        verbose_name_plural = '1GAME: Способности'

    def __str__(self):
        return self.name


class Universe(models.Model):
    """
    Universe model.
    Contains information about the universe.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField('Название', max_length=255)

    class Meta:
        verbose_name = 'Вселенная'
        verbose_name_plural = '1GAME: Вселенные'

    def __str__(self):
        return self.name


class UserStatistic(models.Model):
    """
    User statistic model
    """
    username = models.CharField('Никнейм', max_length=255, null=True, blank=True)
    first_name = models.CharField('Имя', max_length=255, null=True, blank=False)
    last_name = models.CharField('Фамилия', max_length=255, null=True, blank=False)
    reg_date = models.DateTimeField('Дата регистрации', null=True, blank=True)
    status = models.ForeignKey('UserStatus', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Статус')
    win = models.IntegerField('Победы', default=0)
    lose = models.IntegerField('Поражения', default=0)
    is_bot = models.BooleanField('Метка бота', default=False)
    daily = models.DateTimeField('Время ежедневного', null=True, blank=True)

    class Meta:
        verbose_name = 'Статистика юзера'
        verbose_name_plural = '2USER: Статистика юзера Aniwind'

    def __str__(self):
        return f'{self.username}({self.win}/{self.lose})'


class InventorySlot(models.Model):
    """
    Model for an inventory slot that holds an item and its count.
    """
    item = models.ForeignKey('Items', on_delete=models.CASCADE, verbose_name='Предмет')
    count = models.IntegerField(verbose_name='Количество', default=1)

    class Meta:
        verbose_name = 'Слот инвентаря'
        verbose_name_plural = '2USER/INVENTORY:  Слоты инвентаря'
        ordering = ['id']

    def __str__(self):
        return f"{self.item} ({self.count})"


class Inventory(models.Model):
    """
    Model for users' inventory.
    """
    gold = models.IntegerField('Золото', default=0)
    diamond = models.IntegerField('Алмазы', default=0)
    scalp = models.IntegerField('Скальпы', default=0)
    slot = models.ManyToManyField(
        InventorySlot, verbose_name='Слоты',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Инвентарь'
        verbose_name_plural = '2USER/INVENTORY: Инвентари'

    def __str__(self):
        return f"{self.gold}/{self.diamond}/{self.scalp}"


class FightDeck(models.Model):
    """
    User fight-deck model.
    """
    id = models.AutoField(primary_key=True)
    first_card = models.ForeignKey(
        'UserCards', on_delete=models.SET_NULL, verbose_name='Первая карта',
        related_name='first_card', null=True, blank=True
    )
    second_card = models.ForeignKey(
        'UserCards', on_delete=models.SET_NULL, verbose_name='Вторая карта',
        related_name='second_card', null=True, blank=True
    )
    third_card = models.ForeignKey(
        'UserCards', on_delete=models.SET_NULL, verbose_name='Третья карта',
        related_name='third_card', null=True, blank=True
    )

    class Meta:
        verbose_name = verbose_name_plural = '2USER: Боевые колоды'

    def __str__(self):
        return f'{self.first_card}/{self.second_card}/{self.third_card}'


class Equipment(models.Model):
    """
    Equipment model
    """
    id = models.AutoField(primary_key=True)
    amulet = models.ForeignKey('Items', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Слот')

    class Meta:
        verbose_name = verbose_name_plural = '2USER: Экипировка пользователей'

    def __str__(self):
        return str(self.amulet)


class UserCards(models.Model):
    """
    The model stores copies of all cards received by players.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    card = models.ForeignKey('Cards', on_delete=models.CASCADE, verbose_name='Карта')
    hp = models.IntegerField('Здоровье', default=0)
    str = models.IntegerField('Атака', default=0)

    class Meta:
        verbose_name = 'Карта пользователя'
        verbose_name_plural = '2USER: Карточки пользователей'
        ordering = ['card__name']

    def __str__(self):
        return '({}-{}){}'.format(self.hp, self.str, self.card.name)


class UserStatus(models.Model):
    """
    User status model
    """
    id = models.AutoField(primary_key=True)
    status = models.CharField('Статус', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Статус игроков'
        verbose_name_plural = '2USER/STATUS: Статусы пользователей'

    def __str__(self):
        return str(self.status)


class FightData(models.Model):
    """
    The model stores all data received by pre-fight.
    """
    id = models.AutoField(primary_key=True)
    user_first = models.ForeignKey(
        'UserProfile', on_delete=models.CASCADE, verbose_name='Первый воин',
        related_name='user_first', blank=True, null=True
    )
    user_second = models.ForeignKey(
        'UserProfile', on_delete=models.CASCADE, verbose_name='Второй воин',
        related_name='user_second', blank=True, null=True
    )
    array = models.JSONField(verbose_name='Массив памяти', null=True)
    status = models.BooleanField('Активный', default=False)

    winner = models.ForeignKey(
        'UserProfile', on_delete=models.CASCADE, verbose_name='Победитель', null=True,
        blank=True, related_name='winner'
    )
    winner_coins = models.IntegerField('Награда победителя', default=0, null=True, blank=True)
    winner_drop = models.ForeignKey(
        'Items', on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Дроп победителя', related_name='winner_drop'
    )

    loser = models.ForeignKey(
        'UserProfile', on_delete=models.CASCADE, verbose_name='Проигравший', null=True,
        blank=True, related_name='loser'
    )
    loser_coins = models.IntegerField('Награда проигравшего', default=0, null=True, blank=True)
    loser_drop = models.ForeignKey(
        'Items', on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Дроп проигравшего', related_name='loser_drop'
    )

    log = models.TextField(verbose_name='Лог боя', null=True, blank=True)

    class Meta:
        verbose_name = 'Бой'
        verbose_name_plural = '1GAME/FIGHT: Бои'
        constraints = [
            models.UniqueConstraint(
                fields=['user_first', 'status'],
                name='unique_active_match_for_first_user',
                condition=models.Q(status=True)
            ),
            models.UniqueConstraint(
                fields=['user_second', 'status'],
                name='unique_active_match_for_second_user',
                condition=models.Q(status=True)
            )
        ]

    def __str__(self):
        return str(self.id)


class ItemTypes(models.Model):
    """

    """
    id = models.AutoField(primary_key=True)
    name = models.CharField('Название', max_length=255)

    class Meta:
        verbose_name = 'Тип предмета'
        verbose_name_plural = '3DB/ITEMS/TYPES: Типы предмета'

    def __str__(self):
        return str(self.name)


class Items(models.Model):
    """

    """
    id = models.AutoField(primary_key=True)
    name = models.CharField('Название', max_length=255, unique=True)
    description = models.TextField('Описание', default='', blank=True)
    url = models.CharField('Картинка', max_length=255, default='')
    type = models.ForeignKey('ItemTypes', on_delete=models.CASCADE, verbose_name='Тип предмета')
    universe = models.ForeignKey('Universe', on_delete=models.CASCADE, verbose_name='Вселенная', null=True, blank=True)
    buy_price = models.IntegerField('Цена покупки', default=0)
    sell_price = models.IntegerField('Цена продажи', default=0)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = '3DB/ITEMS: Предметы'

    def __str__(self):
        return str(self.name)


class Quest(models.Model):
    """
    Game quest
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField('Название', max_length=255, null=True, blank=True)
    description = models.CharField('Описание', max_length=255, null=True, blank=True)
    end_point = models.IntegerField('Требование', null=True, blank=True, default=0)
    coins = models.IntegerField('Награда валютой', default=0, null=True, blank=True)
    item = models.ForeignKey('Items', on_delete=models.CASCADE, verbose_name='Предмет', null=True, blank=True)
    daily = models.BooleanField('Ежедневный', default=False)

    class Meta:
        verbose_name = verbose_name_plural = '3DB/QUEST: Квесты'

    def __str__(self):
        return str(self.name)


class UserQuests(models.Model):
    """
    User quests
    """
    id = models.AutoField(primary_key=True)
    quest = models.ForeignKey('Quest', on_delete=models.CASCADE, verbose_name='Квест', null=True, blank=True)
    progress = models.IntegerField('Прогресс', null=True, blank=True, default=0)
    completed = models.BooleanField('Выполнен', default=False)

    class Meta:
        verbose_name = verbose_name_plural = '2USER/QUEST: Квесты пользователей'

    def __str__(self):
        return str(self.quest)


class UserProfile(models.Model):
    """
    User model.
    Contains information about the user.
    """
    id = models.BigIntegerField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Django юзер'
    )
    statistic = models.OneToOneField(
        UserStatistic, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Статистика'
    )
    """cards = models.ManyToManyField(
            UserCards, verbose_name='Коллекция',
            null=True, blank=True
        )
    """
    inventory = models.OneToOneField(
        Inventory, on_delete=models.CASCADE,
        verbose_name='Инвентарь', blank=True, null=True
    )
    deck = models.OneToOneField(
        FightDeck, on_delete=models.CASCADE,
        verbose_name='Колода', blank=True, null=True
    )
    equipment = models.OneToOneField(
        Equipment, on_delete=models.CASCADE,
        verbose_name='Снаряжение', blank=True, null=True
    )
    quests = models.ManyToManyField(
        UserQuests, verbose_name='Квесты', blank=True, null=True
    )
    friends = models.ManyToManyField(
        'self', symmetrical=False, related_name='friend_set', blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = '2USER: Пользователи'

    def __str__(self):
        return str(self.user)

    def add_friend(self, friend_profile):
        if friend_profile != self and not self.friends.filter(id=friend_profile.id).exists():
            self.friends.add(friend_profile)
            friend_profile.friends.add(self)

    def remove_friend(self, friend_profile):
        if self.friends.filter(id=friend_profile.id).exists():
            self.friends.remove(friend_profile)
            friend_profile.friends.remove(self)

    def get_friends(self):
        return self.friends.all()

class Shop(models.Model):
    """
    Model for shop.
    """
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey('Items', on_delete=models.CASCADE, verbose_name='Предмет')
    vault = models.CharField('Валюта', max_length=255, default='')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = '3DB/SHOP: Магазин'

    def __str__(self):
        return str(self.item.name)


class Queue(models.Model):
    """
    Game queue.
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField('UserProfile', on_delete=models.CASCADE, verbose_name='Юзер')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='Время добавления')

    class Meta:
        verbose_name = verbose_name_plural = '1GAME/FIGHT: Очередь'

    def __str__(self):
        return str(self.user)

class DuelRequests(models.Model):
    """
    DuelRequests model
    """
    id = models.AutoField(primary_key=True)
    user_to = models.ForeignKey(
        'UserProfile', on_delete=models.CASCADE, verbose_name='Отправитель',
        related_name='duel_requests_received'
    )
    user_from = models.ForeignKey(
        'UserProfile', on_delete=models.CASCADE, verbose_name='Получатель',
        related_name='duel_requests_sent'
    )

    class Meta:
        verbose_name = verbose_name_plural = '2USER/REQUEST: Запросы на дуель'
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return f'{self.user_from} -> {self.user_to}'

