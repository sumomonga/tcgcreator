from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.template.response import TemplateResponse
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.views.generic import View
from django.db.models import Q
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Duel,Phase,UserDeck,UserDeckGroup,Config,GlobalVariable,MonsterEffect,MonsterEffectWrapper,Trigger
from .forms import EditMonsterVariablesForm,EditMonsterForm,EditMonsterItemForm
from .forms import EditMonsterVariablesKindForm,forms
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck
from pprint import pprint
from django.db.models import Prefetch,Max
from .battle_det import battle_det
import json
from .duel import DuelObj

def choices(request):
    room_number =int(request.POST["room_number"])
    trigger_id = request.POST["trigger_id"]
    config = Config.objects.first()
    if not request.user.is_authenticated:
        return HttpResponse("Please Login")
    duel = Duel.objects.filter(id=room_number).get()
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))
    if duel.user_1 == request.user:
        user = 1
        other_user = 2
    elif duel.user_2 == request.user:
        user = 2
        other_user = 1
    duelobj =  DuelObj(room_number)
    duelobj.duel = duel;
    duelobj.user = user
    duelobj.room_number = room_number;
    decks = Deck.objects.all()
    graves = Grave.objects.all()
    hands = Hand.objects.all()
    duelobj.init_all(user,other_user,room_number)
    duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
    if duel.in_cost == True:
        return HttpResponse("error")

    phases = Phase.objects.order_by('-priority').filter(show =1)
    variables = GlobalVariable.objects.order_by('-priority').filter(show =1)
    fields = Field.objects.all()
    field_size = FieldSize.objects.first()
    x = range(field_size.field_x)
    y = range(field_size.field_y)


    if duel.user_1 == request.user:
        if(duel.appoint !=1):
            return HttpResponse("error")

        duelobj.user = 1;
        user = duel.user_1
        other_user = duel.user_2
        if choices_det(duelobj,trigger_id,request) == True:
            return battle_det(request,duelobj)
        else:
            return HttpResponse("error")
    elif duel.user_2 == request.user:
        if(duel.appoint !=2):
            return HttpResponse("error")
        duelobj.user = 2;
        user = duel.user_2
        other_user = duel.user_1
        if choices_det(duelobj,trigger_id,request) == True:
            return battle_det(request,duelobj)
        else:
            return HttpResponse("error")
    return HttpResponse("error")
def choices_det(duelobj,trigger_id,request):
    triggers = Trigger.objects.all()
    trigger = triggers.get(id = trigger_id)
    if(trigger != None):
        return duelobj.invoke_trigger(trigger,"","","",0,"")
    else:
        return False
