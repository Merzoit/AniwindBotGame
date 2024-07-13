from rest_framework import serializers
from core.models import (
    FightData,
    UserProfile,
    Cards,
    Elements,
    Capabilities,
    Universe,
    AbilityStage,
    UserCards,
    FightDeck,
    Items,
    Equipment,
    UserStatistic,
)

class ElementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elements
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']

class AbilityStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbilityStage
        fields = ['id', 'name']
        read_only_fields = fields

class CapabilitiesSerializer(serializers.ModelSerializer):
    stage = AbilityStageSerializer(read_only=True)

    class Meta:
        model = Capabilities
        fields = ['id', 'stage', 'name']
        read_only_fields = ['id', 'stage', 'name']

class UniverseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universe
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']

class CardsSerializer(serializers.ModelSerializer):
    element = ElementsSerializer(read_only=True)
    ability = CapabilitiesSerializer(read_only=True)
    universe = UniverseSerializer(read_only=True)

    class Meta:
        model = Cards
        fields = ['id', 'name', 'element', 'ability', 'universe']
        read_only_fields = ['id', 'name', 'element', 'ability', 'universe']

class UserCardsSerializer(serializers.ModelSerializer):
    card = CardsSerializer(read_only=True)

    class Meta:
        model = UserCards
        fields = ['card', 'hp', 'str']
        read_only_fields = ['card']

class FightDeckSerializer(serializers.ModelSerializer):
    first_card = UserCardsSerializer(read_only=True)
    second_card = UserCardsSerializer(read_only=True)
    third_card = UserCardsSerializer(read_only=True)

    class Meta:
        model = FightDeck
        fields = ['first_card', 'second_card', 'third_card']
        read_only_fields = ['first_card', 'second_card', 'third_card']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class EquipmentSerializer(serializers.ModelSerializer):
    amulet = ItemSerializer(read_only=True)

    class Meta:
        model = Equipment
        fields = ['id', 'amulet']
        read_only_fields = ['id', 'amulet']


class UserStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatistic
        fields = ['username']


class UserSerializer(serializers.ModelSerializer):
    deck = FightDeckSerializer(read_only=True)
    equipment = EquipmentSerializer(read_only=True)
    statistic = UserStatisticSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'deck', 'equipment', 'statistic']
        read_only_fields = ['id', 'deck', 'equipment', 'statistic']

class FightSerializer(serializers.ModelSerializer):
    user_first = UserSerializer(read_only=True)
    user_second = UserSerializer(read_only=True)

    class Meta:
        model = FightData
        fields = '__all__'
        read_only_fields = ['id', 'user_first', 'user_second', 'array']
