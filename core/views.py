#################
#
# Imports
#
#################
import random
from urllib import request

from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render
from core.models import *
from django.db.models import Q
from django.db import IntegrityError, transaction, DatabaseError
from django.views.generic import TemplateView, View
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.views import APIView
from core.serializers import CardsSerializer, FightSerializer, UserSerializer
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta


#################
#
# Display view and templates logic
#
#################
class UserProfileView(TemplateView):
    """
    View to display user profile
    """
    template_name = 'al/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        user_friends = user.get_friends()
        context['friends'] = user_friends
        context['user'] = user
        return context


class UserInventoryView(TemplateView):
    """
    View to display user inventory
    user - django user
    aw_user - aniwind user
    """
    template_name = 'al/inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        inventory_slots = user.inventory.slot.all()
        inventory_slots = list(inventory_slots)

        while len(inventory_slots) < 9:
            inventory_slots.append(None)

        context['items'] = inventory_slots
        context['user'] = user
        return context


class ShopView(TemplateView):
    """
    View to display shop details
    """
    template_name = 'al/shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        context['items'] = Shop.objects.all()
        context['user'] = user
        return context


class CollectionView(TemplateView):
    """
    View to display player collection details
    """
    template_name = 'al/collection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        cards = UserCards.objects.filter(user=user)
        universes = Universe.objects.all()

        card_name = self.request.GET.get('name', '')
        universe_id = self.request.GET.get('universe', '')

        if card_name:
            cards = cards.filter(card__name__icontains=card_name)
        if universe_id:
            cards = cards.filter(card__universe__id=universe_id)

        context['universes'] = universes
        context['cards'] = cards
        return context


class DeckView(TemplateView):
    """
    View to display player fight deck details
    """
    template_name = 'al/deck.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        user_cards = UserCards.objects.filter(user=user)

        try:
            active_amulet = user.equipment.amulet
        except:
            active_amulet = None

        try:
            amulets = user.inventory.slot.filter(item__type=1)
        except:
            amulets = None

        context['user_cards'] = user_cards
        context['amulets'] = amulets
        context['active_amulet'] = active_amulet
        context['user'] = user
        context['deck'] = {
            1: user.deck.first_card,
            2: user.deck.second_card,
            3: user.deck.third_card
        }
        return context


class ArenaView(TemplateView):
    """
    Renders Arena
    """
    template_name = 'al/arena.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile

        data = {
            "matches": user.statistic.win + user.statistic.lose,
            "wins": user.statistic.win,
            "losses": user.statistic.lose
        }
        context['data'] = data
        context['user'] = user
        return context


class RatingView(TemplateView):
    """
    Renders Rating
    """
    template_name = 'al/rating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class HelpView(TemplateView):
    """
    Renders Help
    """
    template_name = 'al/help.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NewCardView(TemplateView):
    """
    Renders New card teke
    """
    template_name = 'al/new_card.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card_id = self.kwargs.get('id')
        context['card_id'] = card_id
        if card_id:
            context['card'] = get_object_or_404(UserCards, pk=card_id)
        return context


class UpdateFightDeckSlotView(View):
    """
    Updates the fight deck slot
    """
    def post(self, request, slot_name, *args, **kwargs):
        try:
            user = self.request.user.userprofile
            card_id = request.POST.get('selected_card_id')

            selected_card = UserCards.objects.get(id=card_id)
            existing_cards = [
                user.deck.first_card.card if user.deck.first_card else None,
                user.deck.second_card.card if user.deck.second_card else None,
                user.deck.third_card.card if user.deck.third_card else None,
            ]

            if user.statistic.status.id == 1 or user.statistic.status.id == 3:
                messages.success(request, 'Вы не можете менять колоду находясь в очереди или бою..')
            else:
                if selected_card.card in existing_cards:
                    messages.error(request, 'Эта карта уже находится в одном из ваших слотов.')
                else:
                    if slot_name == '1':
                        user.deck.first_card = selected_card
                    elif slot_name == '2':
                        user.deck.second_card = selected_card
                    elif slot_name == '3':
                        user.deck.third_card = selected_card

                    user.deck.save()
                    messages.success(request, 'Карта успешно обновлена в вашей колоде.')

            return HttpResponseRedirect(reverse('user-deck'))
        except Exception as e:
            messages.error(request, f'Server error{e}')
            return HttpResponseRedirect(reverse('user-deck'))

####
class UpdateAmuletSlotView(View):
    """
    Updates the fight deck slot
    """

    def post(self, request, *args, **kwargs):
        try:
            user_profile = self.request.user.userprofile
            amulet_id = request.POST.get('selected_amulet_id')

            if not amulet_id:
                messages.error(request, 'Амулет не выбран.')
                return HttpResponseRedirect(reverse('user-deck'))

            try:
                amulet = Items.objects.get(id=amulet_id)
            except Items.DoesNotExist:
                messages.error(request, 'Амулет не найден.')
                return HttpResponseRedirect(reverse('user-deck'))

            if user_profile.statistic.status.id in [1, 3]:
                messages.error(request, 'Вы не можете менять амулет находясь в очереди или бою.')
            else:
                user_profile.equipment.amulet = amulet
                user_profile.equipment.save()
                messages.success(request, 'Амулет успешно обновлен в вашей колоде.')

            return redirect('user-deck')

        except Exception as e:
            messages.error(request, f'Server error: {e}')
            return HttpResponseRedirect(reverse('user-deck'))


class MMView(TemplateView):
    """
    Match making searching view
    """
    template_name = 'al/mm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        fight_data = FightData.objects.filter(
            (Q(user_first=user) | Q(user_second=user)) & Q(status=True)
        )

        if fight_data:
            context['fight_data'] = fight_data[0]
        else:
            context['fight_data'] = None

        duel_status = self.request.GET.get('duel_status')

        context['duel_status'] = duel_status
        context['user'] = user
        return context


class Fight(TemplateView):
    """
    Create game-link and view
    """
    template_name = 'al/fight.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        fight = FightData.objects.filter(
            Q(user_first=user) | Q(user_second=user),
            status=True
        ).first()
        game_url = f"https://aniwind.ru/static/game/index.html?{fight.id}?{user.id}"
        context['game_url'] = game_url
        return context


class DbView(TemplateView):
    """
    Database view for users
    """
    template_name = 'al/db.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        universe_id = self.request.GET.get('universe')

        if universe_id:
            cards = Cards.objects.filter(universe_id=universe_id)
        else:
            cards = Cards.objects.all()

        universes = Universe.objects.all()
        cards_by_universe = {}
        for card in cards:
            if card.universe not in cards_by_universe:
                cards_by_universe[card.universe] = []
            cards_by_universe[card.universe].append(card)
        context["cards_by_universe"] = cards_by_universe
        context["universes"] = universes
        return context


class QuestView(TemplateView):
    """
    Quest view for users
    """
    template_name = 'al/quest.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.userprofile
        try:
            user_quests = user.quests.filter(Q(completed=False) & Q(quest__daily=False))
        except:
            user_quests = None

        try:
            user_daily = user.quests.get(Q(completed=False) & Q(quest__daily=True))
        except:
            user_daily = None

        context['daily'] = user_daily
        context['quests'] = user_quests
        return context


#################
#
# Action and helpers functions
#
#################
def tg_auth(request):
    """
    User auth
    """
    user_id = request.GET.get('user_id')
    username = request.GET.get('username')
    users = len(User.objects.filter(username=username))
    if username == "None" or users > 0:
        username = user_id
    #first_name = request.GET.get('first_name')
    #last_name = request.GET.get('last_name')

    try:
        if not UserProfile.objects.filter(id=user_id).exists():
            m_status = UserStatus.objects.get(id=2)

            user, created = User.objects.get_or_create(
                username=username
                #defaults={'first_name': first_name, 'last_name': last_name}
            )

            statistic = UserStatistic.objects.create(
                username=username,
                status=m_status,
                reg_date=timezone.now(),
                daily=timezone.now() - timedelta(days=1)
            )

            inventory = Inventory.objects.create(
                gold=1500,
                diamond=10,
                scalp=0
            )

            deck = FightDeck.objects.create(
                first_card=None,
                second_card=None,
                third_card=None
            )

            equipment = Equipment.objects.create(
                amulet=None
            )
            user_profile = UserProfile.objects.create(
                id=user_id,
                user=user,
                statistic=statistic,
                inventory=inventory,
                equipment=equipment,
                deck=deck
            )

            print(f"UserProfile created for user_id {user_id}")

        else:
            # Получаем существующего пользователя
            user_profile = UserProfile.objects.get(id=user_id)
            user = user_profile.user

        # Авторизация пользователя
        login(request, user)
        return redirect('help')
    except Exception as e:
        print(f"Error during Telegram authentication: {e}")
        # При возникновении ошибки можно перенаправить на страницу ошибки или показать сообщение
        return redirect(f'{e}')

def generate_card(universe=None):
    """
    Generate new card
    """
    if universe:
        cards = Cards.objects.filter(universe=universe)
    else:
        cards = Cards.objects.all()

    if cards.exists():
        card = random.choice(cards)
        str = random.randint(card.str_min, card.str_max)
        hp = random.randint(card.hp_min, card.hp_max)

        result = {
            'card': card,
            'str': str,
            'hp': hp
        }
        return result

def open_box(request, slot_id, user_id):
    """
    Open a box
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'This operation is not allowed on this endpoint.')

    try:
        slot = get_object_or_404(InventorySlot, id=slot_id)
        box = get_object_or_404(Items, id=slot.item.id)
        user = get_object_or_404(UserProfile, id=user_id)

        if box.universe:
            card_data = generate_card(box.universe.id)
        else:
            card_data = generate_card()

        if card_data:
            card = UserCards.objects.create(
                user=user,
                card=card_data['card'],
                str=card_data['str'],
                hp=card_data['hp']
            )

            if slot.count > 1:
                slot.count -= 1
                slot.save()
            else:
                slot.delete()
            return HttpResponseRedirect(reverse('new-card', args=(card.id,)))
        else:
            print("No cards available in this universe.")
        return HttpResponseRedirect(reverse('user-inventory'))  # Ensure this redirect is correct
    except Exception as e:
        print(f"Error processing the request: {e}")
        return HttpResponseRedirect(reverse(f'{e}'))  # Redirect to an error page or similar

def purchase_item(request):
    """
    Purchase an shop item
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Shop, item=item_id)
        user_profile = request.user.userprofile
        inventory = user_profile.inventory

        if inventory.gold >= item.item.buy_price:
            inventory.gold -= item.item.buy_price
            inventory.save()

            try:
                slot = user_profile.inventory.slot.get(item=item.item)
                slot.count += 1
                slot.save()
            except:
                new_slot = InventorySlot.objects.create(item=item.item, count=1)
                inventory.slot.add(new_slot)
                inventory.save()

            messages.success(request, 'Успешная покупка!')
            return redirect('shop')  # Redirect back to the shop
        else:
            messages.error(request, 'У вас недостаточно золота!')
            return redirect('shop')
    else:
        messages.error(request, 'Ошибка сервера!')
        return redirect('shop')

def join_queue(request):
    """
    Join user for queue
    """
    user_profile = request.user.userprofile
    f_status = UserStatus.objects.get(id=3)
    q_status = UserStatus.objects.get(id=1)
    try:
        if user_profile.statistic.status == q_status or user_profile.statistic.status == f_status:
            return redirect('mm')

        fight_deck = user_profile.deck

        if not fight_deck or not fight_deck.first_card or not fight_deck.second_card or not fight_deck.third_card:
            messages.error(request, "Пожалуйста, выберите все три карты в вашу боевую колоду в разделе меню 'Колода'.")
            return redirect('arena')

        user_profile.statistic.status = q_status
        user_profile.statistic.save()
        Queue.objects.create(user=user_profile)
        return redirect('mm')
    except IntegrityError as e:
        if 'Duplicate entry' in str(e) and 'user_id' in str(e):
            messages.error(request, "Вы уже находитесь в очереди.")
        else:
            messages.error(request, "Произошла ошибка при обработке вашего запроса.")
    except Exception as e:
        messages.error(request, f"Произошла неожиданная ошибка: {str(e)}")
    return redirect('arena')

def check_fight_status(request):
    """
    Check fight active
    """
    user = request.user.userprofile
    fight = FightData.objects.filter(user_first=user).first() or FightData.objects.filter(user_second=user).first()

    if fight:
        return JsonResponse({'status': 'started', 'fight_id': fight.id})
    else:
        return JsonResponse({'status': 'waiting'})

def csrf_token(request):
    from django.middleware.csrf import get_token
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

def remove_from_queue(request):
    if request.method == 'POST':
        user = request.user.userprofile
        m_status = UserStatus.objects.get(id=2)
        try:
            user_id = user.id
            queue = get_object_or_404(Queue, user_id=user_id)
            user.statistic.status = m_status
            user.statistic.save()
            queue.delete()
            return redirect('arena')
        except Queue.DoesNotExist:
            return redirect('mm')
        except Exception as e:
            user.status = m_status
            user.save()
            return redirect('arena')
            #return JsonResponse({'success': False, 'error': str(e), 'x': 'Перезагрузите игру'})
    return redirect('arena')
    #return JsonResponse({'success': False, 'error': 'Invalid request method'})

def reset_deck(request):
    if request.method == 'POST':
        f_status = UserStatus.objects.get(id=3)
        q_status = UserStatus.objects.get(id=1)
        try:
            user = request.user.userprofile
            if user.statistic.status == q_status or user.statistic.status == f_status:
                messages.success(request, 'Нельзя сбросить колоду находясь в бою/очереди')
                return redirect('user-deck')
            deck = get_object_or_404(FightDeck, userprofile=user.id)
            deck.first_card = None
            deck.second_card = None
            deck.third_card = None
            deck.save()
            messages.success(request, 'Колода успешно сброшена!')
            return redirect('user-deck')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def reset_amulet(request):
    if request.method == 'POST':
        f_status = UserStatus.objects.get(id=3)
        q_status = UserStatus.objects.get(id=1)
        try:
            user = request.user.userprofile
            if user.statistic.status == q_status or user.statistic.status == f_status:
                messages.success(request, 'Нельзя сбросить амулет находясь в бою/очереди')
                return redirect('user-deck')
            equipment = get_object_or_404(Equipment, userprofile=user.id)
            equipment.amulet = None
            equipment.save()
            messages.success(request, 'Амулет успешно сброшен!')
            return redirect('user-deck')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def card_sell(request, red):
    """
    Card sell action
    """
    user = request.user.userprofile
    card_id = request.POST.get('card')
    deck = user.deck
    inventory = user.inventory

    try:
        card = get_object_or_404(UserCards, id=card_id)

        if card == deck.first_card or card == deck.second_card or card == deck.third_card:
            messages.error(request, 'Эта карта в вашей колоде')
            return redirect('user-collection')

        with transaction.atomic():
            card.delete()
            inventory.gold += 20
            inventory.save()
            user.save()

        messages.success(request, 'Вы продали карту за 20 аникоинов')

    except UserCards.DoesNotExist:
        messages.error(request, 'Карта не найдена')
    except DatabaseError:
        messages.error(request, 'Произошла ошибка базы данных. Пожалуйста, попробуйте позже.')
    except Exception as e:
        messages.error(request, f'Произошла ошибка: {str(e)}')

    if red == 'Коллекция':
        return redirect('user-collection')
    else:
        return redirect('user-inventory')

def item_sell(request, slot_id):
    """
    Item sell method
    """
    user = request.user.userprofile

    try:
        user_slot = user.inventory.slot.get(id=slot_id)

        with transaction.atomic():
            if user_slot.count > 1:
                user_slot.count -= 1
                user.inventory.gold += user_slot.item.sell_price
                user.inventory.save()
                user_slot.save()
            else:
                if (user_slot.item.type.name == 'Амулет') and (user_slot.item == user.equipment.amulet):
                    messages.error(request, 'Амулет экипирован, сначало снимитите его')
                    return redirect('user-inventory')

                user.inventory.gold += user_slot.item.sell_price
                user.inventory.save()
                user_slot.delete()

            messages.success(request, 'Вы успешно продали {} за {} аникоинов'.format(user_slot.item.name, user_slot.item.sell_price))
            return redirect('user-inventory')

    except Exception as e:
        messages.error(request, '{}'.format(e))
        return redirect('user-inventory')

def complete_quest(request, id):
    """
    Complete the quest for the user.
    """
    try:
        user = request.user.userprofile
        quest = get_object_or_404(user.quests, id=id)

        if quest.progress < quest.quest.end_point:
            remaining_progress = quest.quest.end_point - quest.progress
            messages.error(request, f'Условия не выполнены. Нужно еще: {remaining_progress}')
        else:
            # Mark the quest as completed
            quest.completed = True
            quest.save()

            if quest.quest.name == 'Разминка':
                user.inventory.gold += 5000
                item = quest.quest.item
                try:
                    slot = user.inventory.slot.get(item=item)
                    slot.count += 1
                    slot.save()
                except user.inventory.slot.model.DoesNotExist:
                    new_slot = user.inventory.slot.create(item=item, count=1)
                    new_slot.save()
                user.inventory.save()
                messages.success(request, 'Квест успешно выполнен. Вы получили 5000 аниконов и "Амулет победителя"')
            elif quest.quest.name == 'Фармила':
                user.inventory.gold += 1500
                user.inventory.save()
                messages.success(request, 'Квест успешно выполнен. Вы получили 1500 аниконов')
            elif quest.quest.name == 'Легче лёгкого':
                user.inventory.gold += 200
                try:
                    slot = user.inventory.slot.get(item__id=quest.quest.item.id)
                    slot.count += 1
                    slot.save()
                    messages.success(request, 'Квест успешно выполнен. Вы получили 200 аникоинов и Бокс "Судьбы"')
                except:
                    new_slot = user.inventory.slot.create(item=quest.quest.item, count=1)
                    user.inventory.slot.add(new_slot)
                    user.inventory.save()
                    messages.success(request, 'Квест успешно выполнен. Вы получили 200 аникоинов и Бокс "Судьбы"')
                user.inventory.save()
            else:
                messages.success(request, 'WTF')

        return redirect('quest')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('quest')

def take_quest(request):
    try:
        user = request.user.userprofile
        all_quests = Quest.objects.all()
        user_quests = user.quests.all()

        available_quests = all_quests.exclude(id__in=user_quests.values_list('quest', flat=True))
        available_quests = available_quests.filter(daily=False)
        if not available_quests.exists():
            messages.success(request, 'У вас нет доступных квестов')
            return redirect('quest')

        for i in available_quests:
            quest = UserQuests.objects.create(
                quest=i,
                progress=0
            )
            user.quests.add(quest)

        messages.success(request, 'Квесты успешно добавлены')
        return redirect('quest')

    except Exception as e:
        messages.error(request, f'Произошла ошибка: {e}')
        return redirect('quest')

def take_daily_quest(request):
    try:
        user = request.user.userprofile
        all_quests = Quest.objects.all()
        user_quests = user.quests.all()

        # Check for daily quests
        if not user_quests.filter(Q(quest__daily=True) & Q(completed=False)).exists():
            user_daily_time = user.statistic.daily
            time_since_last_quest = timezone.now() - user_daily_time

            # Check if it's been a day since the last daily quest
            if time_since_last_quest >= timedelta(days=1):
                available_daily_quests = all_quests.filter(daily=True)
                if available_daily_quests.exists():
                    daily_quest = random.choice(available_daily_quests)
                    quest = UserQuests.objects.create(
                        quest=daily_quest
                    )
                    user.quests.add(quest)
                    user.statistic.daily = timezone.now()  # Update the daily quest timestamp
                    user.statistic.save()
                    messages.success(request, 'Ежедневный квест успешно получен')
                else:
                    messages.success(request, 'Нет доступных ежедневных квестов')
            else:
                messages.success(request, 'Еще не прошло 24 часа с момента последнего ежедневного квеста')
        else:
            messages.success(request, 'У вас уже есть активный ежедневный квест')

        return redirect('quest')

    except Exception as e:
        messages.error(request, f'Произошла ошибка: {e}')
        return redirect('quest')

#################
#
# API v1
#
#################
def add_friend(request):
    try:
        user_id = request.POST['user_id']
        friend_profile = get_object_or_404(UserProfile, id=user_id)
        request.user.userprofile.add_friend(friend_profile)
        messages.success(request, 'Вы успешно добавили {} в список друзей'.format(friend_profile.statistic.username))
        return redirect('user-detail')
    except ValueError:
        messages.error(request, 'Неверный формат ID. ID должен быть числом.')
        return redirect('user-detail')
    except Exception as e:
        messages.error(request, f'Пользователь не найден/{e}')
        return redirect('user-detail')

def remove_friend(request):
    try:
        user_id = request.POST['user_id']
        friend_profile = get_object_or_404(UserProfile, id=user_id)
        request.user.userprofile.remove_friend(friend_profile)
        messages.success(request, 'Вы успешно удалили {} из списка друзей'.format(friend_profile.statistic.username))
        return redirect('user-detail')
    except Exception as e:
        messages.error(request, f'{e}')
        return redirect('user-detail')

def get_duel(request):
    """
    Get duel for friend method
    """
    try:
        user = request.user.userprofile
        friend_id = request.POST['friend_id']

        friend = get_object_or_404(UserProfile, id=friend_id)
        DuelRequests.objects.create(
            user_from=user,
            user_to=friend
        )
        messages.success(request, 'Запрос успешно отправлен, ожидайте ответ.')
        return redirect('mm')
    except Exception as e:
        messages.error(request, f'Произошла ошибка: {e}')
        return redirect('user-detail')


class CardsListView(ListAPIView):
    queryset = Cards.objects.all()
    serializer_class = CardsSerializer


class CardDetailView(RetrieveAPIView):
    queryset = Cards.objects.all()
    serializer_class = CardsSerializer


class UserProfileList(ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer


class UserProfileDetail(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer


class FightDetailView(RetrieveUpdateDestroyAPIView):
    queryset = FightData.objects.all()
    serializer_class = FightSerializer


class FightDataUpdate(APIView):
    def quest_magic(self, user, status):
        """
        Updates the progress of user quests based on fight status.

        Args:
            user: The user object whose quests are to be updated.
            status: The result status of the fight ('winner' or 'loser').

        Returns:
            None
        """
        if status not in ['winner', 'loser']:
            return

        quests_to_update = user.quests.filter(completed=False)

        for item in quests_to_update:

            if item.quest.name == 'Разминка':
                if status == 'winner':
                    if item.progress < item.quest.end_point:
                        item.progress += 1
                        item.save()
                else:
                    continue

            elif item.quest.name == 'Фармила':
                if item.progress < item.quest.end_point:
                    try:
                        if status == 'winner':
                            item.progress += self.request.data.get('winner_coins', 0)
                        elif status == 'loser':
                            item.progress += self.request.data.get('loser_coins', 0)
                        item.save()
                    except KeyError:
                        # Handle missing 'winner_coins' or 'loser_coins' data gracefully
                        continue
                continue

            elif item.quest.name == 'Легче лёгкого':
                if item.progress < item.quest.end_point:
                    try:
                        if status == 'winner':
                            item.progress += 1
                        elif status == 'loser':
                            continue
                        item.save()
                    except KeyError:
                        # Handle missing 'winner_coins' or 'loser_coins' data gracefully
                        continue

    def put(self, request, pk):
        try:
            fight_data = FightData.objects.get(pk=pk)
        except FightData.DoesNotExist:
            return Response({'error': 'FightData not found'}, status=status.HTTP_404_NOT_FOUND)

        if not fight_data.status:
            return Response({'status': 'duplicate', 'message': 'Match result already exists'},
                            status=status.HTTP_200_OK)

        serializer = FightSerializer(fight_data, data=request.data)
        if serializer.is_valid():
            try:
                m_status = UserStatus.objects.get(id=2)
                serializer.save()
                winner = get_object_or_404(UserProfile, id=request.data['winner'])
                loser = get_object_or_404(UserProfile, id=request.data['loser'])
                w_gold = request.data['winner_coins']
                l_gold = request.data['loser_coins']

                loser_inventory = loser.inventory
                winner_inventory = winner.inventory

                loser_inventory.gold += l_gold
                loser_inventory.save()

                winner_inventory.gold += w_gold
                winner_inventory.save()

                winner.statistic.win += 1
                winner.statistic.status = m_status
                winner.statistic.save()

                loser.statistic.lose += 1
                loser.statistic.status = m_status
                loser.statistic.save()

                self.quest_magic(winner, 'winner')
                self.quest_magic(loser, 'loser')

                if 'winner_drop' in request.data:
                    drop = get_object_or_404(Items, id=request.data['winner_drop'])
                    slot = winner.inventory.slot.filter(item__id=drop.id).first()

                    if slot:
                        slot.count += 1
                        slot.save()
                    else:
                        new_slot = InventorySlot.objects.create(
                            inventory=winner.inventory,
                            item=drop,
                            count=1
                        )
                        new_slot.save()
                        winner.inventory.slot.add(new_slot)

                return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            except Inventory.DoesNotExist:
                return Response({'error': 'Inventory not found for winner'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': f"An unexpected error occurred: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
