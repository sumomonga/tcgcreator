from time import time
from .models import FieldSize,MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,Deck,UserDeck,UserDeckGroup,UserDeckChoice,Duel,Phase,GlobalVariable,Grave,Hand,DuelDeck,DuelGrave,DuelHand
from django.http import HttpResponse,HttpResponseRedirect
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_user_deck_det
import json
import uuid
import random
from pprint import pprint
def init_duel(room_number,user):
    duel=Duel.objects.all().filter(id=room_number).first();
    duel_deck=DuelDeck.objects.all().filter(room_number=room_number);
    duel_deck.delete()
    duel_grave=DuelGrave.objects.all().filter(room_number=room_number);
    duel_grave.delete()
    duel_hand=DuelHand.objects.all().filter(room_number=room_number);
    duel_hand.delete()
    user_1 = duel.user_1
    decks = Deck.objects.all()
    graves = Grave.objects.all()
    hands = Hand.objects.all()
    deck_group = UserDeckChoice.objects.filter(user = user_1).first()
    if not deck_group:
        return "デッキを構築してください"
    user_deck_group = deck_group.user_deck
    if not user_deck_group:
        duel.user_1=None
        duel.user_2=None
        duel.winner = 0
        duel.waiting = True
        duel.save()
        return "エラーが発生しました"
    if user_deck_group.user != user_1:
        duel.user_1=None
        duel.user_2=None
        duel.waiting = True
        duel.winner = 0
        duel.save()
        return "エラーが発生しました"
    user_decks = UserDeck.objects.filter(user = user_1,deck_group = user_deck_group)
    if not user_decks:
        return False
    i=1
    for grave in graves:
        if(grave.mine_or_other == 1):
            DuelGrave(room_number = room_number,mine_or_other = 3,grave_id  = i,grave_content="[]").save()
        else:
            DuelGrave(room_number = room_number,mine_or_other = 1,grave_id  = i,grave_content="[]").save()
            DuelGrave(room_number = room_number,mine_or_other = 2,grave_id  = i,grave_content="[]").save()
        i+=1
    i=1
    for hand in hands:
        if(hand.mine_or_other == 1):
            DuelHand(room_number = room_number,mine_or_other = 3,hand_id  = i,hand_content="[]").save()
        else:
            DuelHand(room_number = room_number,mine_or_other = 1,hand_id  = i,hand_content="[]").save()
            DuelHand(room_number = room_number,mine_or_other = 2,hand_id  = i,hand_content="[]").save()
        i+=1
    i=1
    for deck in decks:
        user_deck = user_decks.filter(deck_type = deck).first()
        if not user_deck:
            duel.user_1=None
            duel.user_2=None
            duel.winner = 0
            duel.save()
            return HttpResponse("エラーが発生しました")
        user_deck_det = user_deck.deck.split("_")
        if(len(user_deck_det) < deck.min_deck_size):
            duel.user_1=None
            duel.user_2=None
            duel.winner = 0
            duel.save()
            return HttpResponse("エラーが発生しました")
        elif(len(user_deck_det) > deck.max_deck_size):
            duel.user_1=None
            duel.user_2=None
            duel.winner = 0
            duel.save()
            return HttpResponse("エラーが発生しました")
        user_deck_det= create_user_deck_det(user_deck.deck,i,1)
        if(deck.mine_or_other == 1):
            DuelDeck.objects.filter(room_number = room_number,mine_or_other = 3,deck_id  = i).delete()
            DuelDeck(room_number = room_number,mine_or_other = 3,deck_id  = i,deck_content = user_deck_det).save()
        else:
            DuelDeck.objects.filter(room_number = room_number,mine_or_other = 1,deck_id  = i).delete()
            DuelDeck(room_number = room_number,mine_or_other = 1,deck_id  = i,deck_content = user_deck_det).save()
        i+=1


    user_2 = user
    decks = Deck.objects.all()
    deck_group = UserDeckChoice.objects.filter(user = user_2).first()
    if not deck_group:
        return HttpResponse("デッキを構築してください")
    user_deck_group = deck_group.user_deck
    if not user_deck_group:
        duel.user_1=None
        duel.user_2=None
        duel.winner = 0
        duel.save()
        return HttpResponse("エラーが発生しました")
    if user_deck_group.user != user_2:
        duel.user_1=None
        duel.user_2=None
        duel.winner = 0
        duel.save()
        return HttpResponse("エラーが発生しました")
    user_decks = UserDeck.objects.filter(user = user_2,deck_group = user_deck_group)
    if not user_decks:
        duel.user_1=None
        duel.user_2=None
        duel.winner = 0
        duel.save()
        return HttpResponse("エラーが発生しました")
    i=1
    for deck in decks:
        user_deck = user_decks.filter(deck_type = deck).first()
        if not user_deck:
            duel.user_1=None
            duel.user_2=None
            duel.winner = 0
            duel.save()
            return HttpResponse("エラーが発生しました")
        user_deck_det = user_deck.deck.split("_")
        if(len(user_deck_det) < deck.min_deck_size):
            duel.user_1=None
            duel.user_2=None
            duel.winner = 0
            duel.save()
            return HttpResponse("エラーが発生しました")
        elif(len(user_deck_det) > deck.max_deck_size):
            duel.user_1=None
            duel.user_2=None
            duel.winner = 0
            duel.save()
            return HttpResponse("エラーが発生しました")
        user_deck_det= create_user_deck_det(user_deck.deck,i,2)
        if(deck.mine_or_other == 0):
            DuelDeck.objects.filter(room_number = room_number,mine_or_other = 2,deck_id  = i).delete()
            DuelDeck(room_number = room_number,mine_or_other = 2,deck_id  = i,deck_content = user_deck_det).save()
        i+=1
    start_phase = Phase.objects.order_by('-priority').first()
    duel.field = init_field()
    duel.winner = 0
    duel.duel_id = str(uuid.uuid4())
    duel.cost_log = ""
    duel.log = "デュエルID " + duel.duel_id + "\n"
    duel.log_turn = duel.log
    duel.phase = start_phase
    duel.audio = ""
    duel.chain = 0;
    duel.chain_det = "";
    duel.chain_user = "";
    duel.user_2 = user
    duel.global_variable = init_global_variable()
    duel.mess = init_mess()
    duel.timing_mess = "{}"
    duel.timing = None
    duel.time_1 = time()
    duel.time_2 = time()
    duel.cost_result = init_cost_result()
    duel.waiting = False
    tmp = {}
    t_tmp = []
    duel.in_pac = json.dumps(t_tmp)
    duel.in_pac_cost = json.dumps(t_tmp)
    duel.trigger_waiting = json.dumps(t_tmp)
    duel.eternal_det = json.dumps(t_tmp)
    duel.in_trigger_waiting = False
    duel.cost = json.dumps(tmp)
    duel.cost_det = 0
    duel.chain = 0
    duel.in_cost = False
    duel.user_turn  =random.randrange(1,3)
    if duel.user_turn == 1:
        duel.log += duel.user_1.first_name  + "のターンからスタート\n"
        duel.log_turn += duel.user_1.first_name  + "のターンからスタート\n"
    elif duel.user_turn == 2:
        duel.log += duel.user_2.first_name  + "のターンからスタート\n"
        duel.log_turn += duel.user_2.first_name  + "のターンからスタート\n"
    duel.appoint  = duel.user_turn
    duel.current_priority  = 10000
    duel.ask = 0

    duel.save()
    return False
def init_field():
    field_size = FieldSize.objects.first()
    fields = Field.objects.all()
    field_x = field_size.field_x
    field_y = field_size.field_y
    result_field = [];
    for y in range(field_y):
        tmp = []
        for x in range(field_x):
            tmp_field = {}
            field = fields.get(x=x,y=y)
            tmp_field["kind"] = field.kind
            tmp_field["mine_or_other"] = field.mine_or_other
            tmp_field["det"] = None
            tmp.append(tmp_field)
        result_field.append(tmp)
    return json.dumps(result_field)

def init_mess():
    return_value = {}
    return json.dumps(return_value)
def init_cost_result():
    return_value = {}
    return json.dumps(return_value)
def init_global_variable():
    return_value = {}
    global_variables = GlobalVariable.objects.order_by('-priority').all()
    for global_variable in global_variables:
        tmp ={}
        if(global_variable.mine_or_other == 1):
            tmp["mine_or_other"] = 1
            tmp["value"] = global_variable.initial_value
            tmp["show"] = global_variable.show
        else:
            tmp["mine_or_other"] = 0
            tmp["1_value"] = global_variable.initial_value
            tmp["1_show"] = global_variable.show
            tmp["2_value"] = global_variable.initial_value
            tmp["2_show"] = global_variable.show
        return_value[global_variable.variable_name] = (tmp)
    return json.dumps(return_value)

def check_user_deck(user):
    decks = Deck.objects.all()
    deck_group = UserDeckChoice.objects.filter(user = user).first()
    if not deck_group:
        return "デッキを構築してください"
    user_deck_group = deck_group.user_deck
    if not user_deck_group:
        return "デッキを構築してください"
    if user_deck_group.user != user:
        return "デッキを構築してください"
    user_decks = UserDeck.objects.filter(user = user,deck_group = user_deck_group)
    if not user_decks:
        return False
    for deck in decks:
        user_deck = user_decks.filter(deck_type = deck).first()
        if not user_deck:
            return "デッキを構築してください"
        user_deck_det = user_deck.deck.split("_")
        if(len(user_deck_det) < deck.min_deck_size):
            return deck.deck_name+"のデッキ枚数が足りません"
        elif(len(user_deck_det) > deck.max_deck_size):
            return deck.deck_name+"のデッキ枚数が多すぎます"
    return False
def check_in_other_room(user,room_number):
    for i in range(1,4):
        if i == room_number:
            continue
        duel = Duel.objects.filter(id=i).first();
        if duel.waiting == 0 and duel.winner == 0 and (duel.user_1 == user or duel.user_2 == user):
            return True
        elif duel.waiting == 1 and (duel.user_1 == user and duel.user_2 is None):
            return True
    return False
