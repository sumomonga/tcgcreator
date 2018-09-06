from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.views.generic import View
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Duel,Phase,UserDeck,UserDeckGroup,Config,GlobalVariable,VirtualVariable
from .forms import EditMonsterVariablesForm,EditMonsterForm,EditMonsterItemForm
from .forms import EditMonsterVariablesKindForm,forms
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck
from pprint import pprint
from django.db.models import Prefetch,Max
import json

def battle1(request):
    return battle(request,1)
def battle2(request):
    return battle(request,2)
def battle3(request):
    return battle(request,3)
def battle(request,room_number):
    config = Config.objects.first()
    gray_out = config.gray_out
    limit_time = config.limit_time
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    duel = Duel.objects.filter(id=room_number).get()
    if not duel.user_2 :
        if room_number == 1:
            return HttpResponseRedirect(reverse('init_battle1'))
        if room_number == 2:
            return HttpResponseRedirect(reverse('init_battle2'))
        if room_number == 3:
            return HttpResponseRedirect(reverse('init_battle3'))

    if duel.waiting == True:
        if room_number == 1:
            return HttpResponseRedirect(reverse('watch1'))
        if room_number == 2:
            return HttpResponseRedirect(reverse('watch2'))
        if room_number == 3:
            return HttpResponseRedirect(reverse('watch3'))
    if duel.winner != 0:
        if room_number == 1:
            return HttpResponseRedirect(reverse('watch1'))
        if room_number == 2:
            return HttpResponseRedirect(reverse('watch2'))
        if room_number == 3:
            return HttpResponseRedirect(reverse('watch3'))
    phases = Phase.objects.order_by('-priority').filter(show =1)
    variables = GlobalVariable.objects.order_by('-priority').filter(show =1)
    virtual_variables = VirtualVariable.objects.order_by('-priority').filter(show =1)
    fields = Field.objects.all()
    field_size = FieldSize.objects.first()
    x = range(field_size.field_x)
    y = range(field_size.field_y)
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        if room_number == 1:
            return HttpResponseRedirect(reverse('watch1'))
        if room_number == 2:
            return HttpResponseRedirect(reverse('watch2'))
        if room_number == 3:
            return HttpResponseRedirect(reverse('watch3'))
    if duel.winner != 0:
        if room_number == 1:
            return HttpResponseRedirect(reverse('watch1'))
        if room_number == 2:
            return HttpResponseRedirect(reverse('watch2'))
        if room_number == 3:
            return HttpResponseRedirect(reverse('watch3'))
    return render(request,'tcgcreator/battle.html',{'room_number':room_number,'Duel':duel,'Fields':fields,'range_x':x,'range_y':y,'Config':config,"Phases":phases,"Variable":variables,"VirtualVariable":virtual_variables,"gray_out":gray_out})


