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

def field_trigger(request):
    room_number =int(request.POST["room_number"])
    place_id =request.POST["place_id"]
    place ="field"
    x =int(request.POST["x"])
    y =int(request.POST["y"])
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
        user =2
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
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))

    if duel.user_1 == request.user:
        if field_trigger_det(duelobj,place_id,place,mine_or_other,x,y,trigger_id,request) == True:
            return battle_det(request,duelobj)
        else:
            return HttpResponse("error")
    elif duel.user_2 == request.user:
        if field_trigger_det(duelobj,place_id,place,mine_or_other,x,y,trigger_id,request) == True:
            return battle_det(request,duelobj)
        else:
            return HttpResponse("error")
    return HttpResponse("error")
def field_trigger_det(duelobj,place_id,place_for_answer,mine_or_other,x,y,trigger_id,request):
    duel = duelobj.duel
    room_number = duelobj.room_number
    if duelobj.user == 1:
        user = 1
        other_user = 2
        if mine_or_other == "1":
            tmp_user =1
            tmp_other_user = 2
        else:
            tmp_user =2
            tmp_other_user = 1
    else:
        user = 2
        other_user = 1
        if mine_or_other == "1":
            tmp_user =2
            tmp_other_user = 1
        else:
            tmp_user =1
            tmp_other_user = 2

    field = duelobj.field
    if field[x][y]["det"]["place_unique_id"] == place_id:
        mine_or_other = field[x][y]["mine_or_other"]
        monster = Monster.objects.get(id=field[x][y]["det"]["id"])
        monster_triggers = monster.trigger.all()
        result_trigger = monster_triggers.get(id=trigger_id)
        if(result_trigger is None):
            return False
        elif duelobj.check_launch_trigger(result_trigger,duel.phase,duel.user_turn,user,other_user,mine_or_other,"field",place_id,0,x,y):
            duelobj.invoke_trigger(result_trigger,"field",field[x][y]["det"],mine_or_other,duelobj.user,0,x,y)
            return True
    return False

 
