from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.views.generic import View
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Duel,Phase,UserDeck,UserDeckGroup,Config,GlobalVariable,MonsterEffect,MonsterEffectWrapper,DuelDeck,DuelGrave,DuelHand
from .forms import EditMonsterVariablesForm,EditMonsterForm,EditMonsterItemForm
from .forms import EditMonsterVariablesKindForm,forms
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck
from pprint import pprint
from django.db.models import Prefetch,Max
from .battle_det import battle_det
import json
from .duel import DuelObj

def deck_trigger(request):
    room_number =int(request.POST["room_number"])
    place_id =request.POST["place_id"]
    place ="deck"
    deck_id =int(request.POST["deck_id"])
    trigger_id =int(request.POST["trigger_id"])
    mine_or_other =request.POST["mine_or_other"]

    config = Config.objects.first()
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    duel = Duel.objects.filter(id=room_number).get()
    duelobj =  DuelObj(room_number)
    duelobj.duel = duel;
    duelobj.room_number = room_number;
    if duel.user_1 == request.user:
        duelobj.user = 1;
        user = 1
        other_user = 2
    elif duel.user_2 == request.user:
        duelobj.user = 2;
        user = 2
        other_user = 1
    duelobj.init_all(user,other_user,room_number)
    decks = Deck.objects.all()
    graves = Grave.objects.all()
    hands = Hand.objects.all()
    duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
    phases = Phase.objects.order_by('-priority').filter(show =1)
    variables = GlobalVariable.objects.order_by('-priority').filter(show =1)
    fields = Field.objects.all()
    field_size = FieldSize.objects.first()
    x = range(field_size.field_x)
    y = range(field_size.field_y)
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))

    if duel.user_1 == request.user:
        if deck_trigger_det(duelobj,place_id,place,mine_or_other,deck_id,trigger_id,request) == True:
            return battle_det(request,duelobj)
        else:
            return HttpResponse("error")
    elif duel.user_2 == request.user:
        if deck_trigger_det(duelobj,place_id,place,mine_or_other,deck_id,trigger_id,request) == True:
            return battle_det(request,duelobj)
        else:
            return HttpResponse("error")
    return HttpResponse("error")
def deck_trigger_det(duelobj,place_id,place_for_answer,mine_or_other,deck_id,trigger_id,request):
    duel = duelobj.duel
    room_number = duelobj.room_number
    if duelobj.user == 1:
        user = 1
        other_user = 2
        if mine_or_other == "1":
            mine_or_other2 = 1
            tmp_user =1
            tmp_other_user = 2
        else:
            mine_or_other2 = 2
            tmp_user =2
            tmp_other_user = 1
    else:
        user = 2
        other_user = 1
        if mine_or_other == "1":
            mine_or_other2 = 2
            tmp_user =2
            tmp_other_user = 1
        else:
            mine_or_other2 = 1
            tmp_user =1
            tmp_other_user = 2

    if tmp_user == 1:
        tmp = DuelDeck.objects.get(room_number = room_number,mine_or_other = 1,deck_id = deck_id)
        decks = json.loads(tmp.deck_content)

    else:
        tmp = DuelDeck.objects.get(room_number = room_number,mine_or_other = 2,deck_id = deck_id)
        decks = json.loads(tmp.deck_content)
    for deck in decks:
        if deck["place_unique_id"] == place_id:
            monster = Monster.objects.get(id = deck["id"])
            monster_triggers = monster.trigger.all()
            result_trigger = monster_triggers.get(id=trigger_id)
            if(result_trigger is None):
                return False
            elif duelobj.check_launch_trigger(result_trigger,duel.phase,duel.user_turn,user,other_user,mine_or_other2,"deck",place_id,deck_id):
                duelobj.invoke_trigger(result_trigger,"deck",deck,mine_or_other,duelobj.user,deck_id)
                return True
    return False

 
