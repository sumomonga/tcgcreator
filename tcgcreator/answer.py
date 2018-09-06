from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.views.generic import View
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Duel,Phase,UserDeck,UserDeckGroup,Config,GlobalVariable,MonsterEffect,MonsterEffectWrapper,DuelGrave,DuelHand,CostWrapper,Cost,Trigger,Pac
from .forms import EditMonsterVariablesForm,EditMonsterForm,EditMonsterItemForm
from .forms import EditMonsterVariablesKindForm,forms
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck
from pprint import pprint
from django.db.models import Prefetch,Max
from .battle_det import battle_det
import json
from .duel import DuelObj
check_array = []
def answer_cost(duelobj,duel,request):
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))
    answer =json.loads(request.POST["answer"])
    ask_org = duel.ask

    config = Config.objects.first()
    phases = Phase.objects.order_by('-priority').filter(show =1)
    variables = GlobalVariable.objects.order_by('-priority').filter(show =1)
    fields = Field.objects.all()
    field_size = FieldSize.objects.first()
    x = range(field_size.field_x)
    y = range(field_size.field_y)
    if duel.user_1 == request.user:
        if duel.cost_user == 1:
            if(duel.ask == 1 or duel.ask== 3):
                duel.ask-=1
                return answer_det_cost(duelobj,duel,1,answer,request,ask_org)
        else:
            if(duel.ask == 2 or duel.ask== 3):
                duel.ask-=2;
                return answer_det_cost(duelobj,duel,1,answer,request,ask_org)
    elif duel.user_2 == request.user:
        if duel.cost_user == 2:
            if(duel.ask == 1 or duel.ask== 3):
                duel.ask-=1;
                return answer_det_cost(duelobj,duel,2,answer,request,ask_org)
        else:
            if(duel.ask == 2 or duel.ask== 3):
                duel.ask-=2;
                return answer_det_cost(duelobj,duel,2,answer,request,ask_org)
    return HttpResponse("error")
def cancel(request):
    room_number =int(request.POST["room_number"])
    duel = Duel.objects.filter(id=room_number).get()
    duelobj = DuelObj(room_number)
    duelobj.duel = duel;
    duelobj.room_number = room_number;
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    if(duel.user_1 == request.user):
        user = 1
        duelobj.user = 1
        other_user =2
    else:
        duelobj.user = 2
        user = 2
        other_user = 1
    if duel.in_cost ==False:
        return HttpResponse("error")
    duel.in_cost = 0
    duel.in_pac = "[]"
    duel.in_pac_cost = "[]"
    duel.cost_log = ""
    duel.cost_result = json.dumps({})
    duel.ask = 0
    duel.save()
    return HttpResponse("OK")
def none(request):
    room_number =int(request.POST["room_number"])
    duel = Duel.objects.filter(id=room_number).get()
    if duel.ask>0:
        return HttpResponse("Ng")
    duelobj = DuelObj(room_number)
    duelobj.duel = duel;
    duelobj.room_number = room_number;
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    if(duel.user_1 == request.user):
        user = 1
        duelobj.user = 1
        other_user =2
    else:
        duelobj.user = 2
        user = 2
        other_user = 1
    duelobj.init_all(user,other_user,room_number)
    duelobj.check_eternal_effect(duelobj.decks,duelobj.graves,duelobj.hands,duel.phase,duel.user_turn,user,other_user)
    if duel.in_cost == True:
        return HttpResponse("error")
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))
    if duel.user_1 == request.user:
        user = 1
        other_user = 2
        if duel.appoint != 1:
            return HttpResponse("error")
        duel.appoint = 2
        duel.save()
        if duel.appoint != duel.user_turn:
            return HttpResponse("OK")
    if duel.user_2 == request.user:
        user = 2
        other_user = 1
        if duel.appoint != 2:
            return HttpResponse("error")
        duel.appoint = 1
        duel.save()
        if duel.appoint != duel.user_turn:
            return HttpResponse("OK")
    triggers = Trigger.objects.filter(Q(phase__isnull=True) | Q(phase = duel.phase))
    triggers = triggers.filter(Q(chain__isnull = True) | Q(chain__contains=str(duel.chain)))
    if duel.timing != 0:
        triggers = triggers.filter(Q(timing=duel.timing))
    else:
        triggers = triggers.filter(Q(none_timing = True))
    triggers = triggers.filter(priority__lt = duel.current_priority)
    triggers = triggers.order_by('-priority').all();
    trigger_first = triggers.first()
    decks = duelobj.deck_structure
    graves = duelobj.grave_structure
    hands = duelobj.hand_structure

    if trigger_first == None:
        if duel.chain > 0:
            duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
            duelobj.retrieve_chain(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
        if duel.timing is not None:
            duel.timing = duel.timing.next_timing
        duel.current_priority = 10000
        duel.appoint = duel.user_turn
        duel.save();
        return HttpResponse("OK")
    else:
        priority = trigger_first.priority
        none_triggers = triggers.filter(priority = trigger_first.priority,trigger_none_monster = True)
        for trigger in none_triggers:
            if duelobj.check_trigger_condition(trigger,user):
                duel.current_priority = priority
                duel.save()
                return HttpResponse("OK")
        trigger_num = duelobj.check_monster_trigger(decks,graves,hands,user,other_user,priority)
        if trigger_num == True:
            duel.current_priority = priority
            duel.save()
            return HttpResponse("OK")
    duel.current_priority = 0
    duel.save()
    return HttpResponse("OK")
def answer(request):
    global check_array
    room_number =int(request.POST["room_number"])
    duelobj = DuelObj(room_number)
    check_array =[]
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    duel = Duel.objects.filter(id=room_number).get()
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))
    duelobj.duel = duel
    duelobj.room_number = room_number
    if(duel.user_1 == request.user):
        user = 1
        other_user =2
        duelobj.user = 1
    else:
        duelobj.user = 2
        user = 2
        other_user = 1
    duelobj.init_all(user,other_user,room_number)
    decks = Deck.objects.all()
    graves = Grave.objects.all()
    hands = Hand.objects.all()
    duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
    if duel.in_cost:
        return answer_cost(duelobj,duel,request)
    answer =request.POST["answer"]
    ask_org = duel.ask

    config = Config.objects.first()
    phases = Phase.objects.order_by('-priority').filter(show =1)
    variables = GlobalVariable.objects.order_by('-priority').filter(show =1)
    fields = Field.objects.all()
    field_size = FieldSize.objects.first()
    x = range(field_size.field_x)
    y = range(field_size.field_y)
    if duel.user_1 == request.user:
        if duel.user_turn == 1:
            if(duel.ask == 1 or duel.ask== 3):
                duel.ask-=1;
                return_value= answer_det(duelobj,duel,1,answer,request,ask_org)
                return return_value
        else:
            if(duel.ask == 2 or duel.ask== 3):
                duel.ask-=2;
                return_value= answer_det(duelobj,duel,1,answer,request,ask_org)
                return return_value
    elif duel.user_2 == request.user:
        if duel.user_turn == 2:
            if(duel.ask == 1 or duel.ask== 3):
                duel.ask-=1;
                return_value= answer_det(duelobj,duel,2,answer,request,ask_org)
                return return_value
        else:
            if(duel.ask == 2 or duel.ask== 3):
                duel.ask-=2;
                return_value= answer_det(duelobj,duel,2,answer,request,ask_org)
                return return_value
    return HttpResponse("error")
def yes_or_no(request):
    room_number =int(request.POST["room_number"])
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    duel = Duel.objects.filter(id=room_number).get()
    duelobj = DuelObj(room_number)
    duelobj.duel = duel
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))
    monster_effect = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)])).monster_effect
    monster_effect_val = monster_effect.monster_effect_val
    if(monster_effect_val != 15):
        return HttpResponse("error")
    answer =request.POST["answer"]
    if request.user == duel.user_1:
        if duel.user_turn == 1:
            if duel.ask != 1:
                return HttpResponse("error")
        else:
            if duel.ask != 2:
                return HttpResponse("error")

    if request.user == duel.user_2:
        if duel.user_turn == 1:
            if duel.ask != 1:
                return HttpResponse("error")
        return HttpResponse("error")
    if request.user == duel.user_2 and duel.ask != 2:
        return HttpResponse("error")
    if(answer == "yes"):
        duel.ask=0;
        chain_det = json.loads(duel.chain_det)
        current_chain = chain_det[str(duel.chain-1)]
        effect = MonsterEffectWrapper.objects.get(id = current_chain)
        next_effect = effect.monster_effect_next
        if effect.pac :
            next_effect =  duelobj.push_pac(effect.pac)
        else:
            next_effect = effect.monster_effect_next
        if(next_effect != 0):
            chain_det[str(duel.chain-1)] = next_effect.id
        else:
            pac = json.loads(duel.in_pac)
            if pac != []:
                pac_id = pac.pop()
                pac = Pac.objects.get(id=pac_id)
                effect_next =  pac.monster_effect_next
                chain_det[str(duel.chain-1)] = next_effect.id
            else:
                duel.chain-=1
        duel.chain_det = json.dumps(chain_det)
    else:
        duel.ask=0;
        chain_det = json.loads(duel.chain_det)
        current_chain = chain_det[str(duel.chain-1)]
        effect = MonsterEffectWrapper.objects.get(id = current_chain)
        next_effect = effect.monster_effect_next2
        if effect.pac2 :
            next_effect = duelobj.push_pac(effect.pac2)
        else:
            next_effect = effect.monster_effect_next
        if(next_effect != 0):
            chain_det[str(duel.chain-1)] = next_effect.id
        else:
            pac = json.loads(duel.in_pac)
            if pac != []:
                pac_id = pac.pop()
                pac = Pac.objects.get(id=pac_id)
                effect_next =  pac.monster_effect_next
                chain_det[str(duel.chain-1)] = next_effect.id
            else:
                duel.chain-=1
        duel.chain_det = json.dumps(chain_det)
    duel.save()
    return HttpResponse("OK")
def answer_field_det(duelobj,duel,user,x,y,exclude,whether_monster,monster_effect_text,monster_effect_val,request,cost_flag=0):
    global check_array
    room_number =int(request.POST["room_number"])
    x = int(x)
    y = int(y)
    if user == 1:
        other_user = 2
    else:
        other_user = 1
    chain_det = json.loads(duel.chain_det)
    chain_user = json.loads(duel.chain_user)
    if cost_flag == 0:
        chain_user = int(chain_user[str(duel.chain-1)])
    else:
        chain_user = int(chain_user[str(duel.chain)])
    tmp_count = 0
    mess = duelobj.mess
    cost = duelobj.cost
    for monster_effect_det in monster_effect_text:
        as_monster_effect = monster_effect_det["as_monster_condition"]
        tmp_count+=1
        if( user == 1 and chain_user == 1 )or (user == 2 and chain_user == 2):
            if (monster_effect_val == 3) or ( monster_effect_val == 5 and tmp_count == 1) :
                monster_effect_det_monster = monster_effect_det["monster"]
                for place in monster_effect_det_monster["place"]:
                    place_tmp = place["det"].split("_")
                    if(place_tmp[2] == "1" ):
                        mine_or_other = user
                    elif(place_tmp[2] == "2" ):
                        mine_or_other = other_user
                    else:
                        mine_or_other = 0

                    if(place_tmp[0] == "field"):
                            fields = duelobj.field
                    field = fields[x][y]
                    if field["kind"].find(place_tmp[1]) == -1:
                        continue
                    if field["mine_or_other"] != mine_or_other:
                        continue

                    if(whether_monster == 0):
                        if(field["det"] is not None):
                            return HttpResponse("error")
                        else:
                            if cost_flag == 0:
                                if not str(duel.chain-1)  in mess:
                                    mess[str(duel.chain-1)] = {}
                                if not "choose" in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["user"] = user
                                tmp2["place"] = "field"
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                if not as_monster_effect in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)][as_monster_effect] = []
                                mess[str(duel.chain-1)][as_monster_effect].append(tmp2)
                            else:
                                if not str(duel.chain)  in cost:
                                    cost[str(duel.chain)] = {}
                                if not "choose" in cost[str(duel.chain)]:
                                    cost[str(duel.chain)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["user"] = user
                                tmp2["place"] = "field"
                                if not as_monster_effect[1:] in cost[str(duel.chain)]:
                                    cost[str(duel.chain)][as_monster_effect[1:]] = []
                                cost[str(duel.chain)][as_monster_effect[1:]].append(tmp2)
                    else:
                        if(field["det"] is None):
                            return HttpResponse("error")
                        else:
                            if( not validate_answer(duelobj,field["det"],monster_effect_det_monster,exclude,duel)):
                                return HttpResponse("error")
                            check_array.append(field["det"]);
                            if cost_flag == 0:
                                if not str(duel.chain-1)  in mess:
                                    mess[str(duel.chain-1)] = {}
                                if not "choose" in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["place_id"] = field["det"]["place_unique_id"]
                                tmp2["user"] = user
                                tmp2["place"] = "field"
                                if not as_monster_effect in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)][as_monster_effect] = []
                                mess[str(duel.chain-1)][as_monster_effect].append(tmp2)
                            else:
                                if not str(duel.chain)  in cost:
                                    cost[str(duel.chain)] = {}
                                if not "choose" in cost[str(duel.chain)]:
                                    cost[str(duel.chain)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["place_id"] = field["det"]["place_unique_id"]
                                tmp2["user"] = user
                                tmp2["place"] = "field"
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                if not as_monster_effect[1:] in cost[str(duel.chain)]:
                                    cost[str(duel.chain)][as_monster_effect[1:]] = []
                                cost[str(duel.chain)][as_monster_effect[1:]].append(tmp2)

        elif( user == 2 and chain_user == 1 )or (user == 1 and chain_user == 2):
            if (monster_effect_val == 4) or ( monster_effect_val == 5 and tmp_count == 2) :
                monster_effect_det_monster = monster_effect_det["monster"]
                for place in monster_effect_det_monster["place"]:
                    place_tmp = place["det"].split("_")
                    if(place_tmp[2] == "1" ):
                        mine_or_other = user
                    elif(place_tmp[2] == "2" ):
                        mine_or_other = other_user
                    else:
                        mine_or_other = 0
                    if(place_tmp[0] == "field"):
                            fields = duelobj.field
                    field = fields[x][y]
                    if field["kind"].find(place_tmp[1]) == -1:
                        continue
                    if field["mine_or_other"] != mine_or_other:
                        continue
                    if(whether_monster == 0):
                        if(field["det"] is not None):
                            return HttpResponse("error")
                        else:
                            if cost_flag == 0:
                                if not str(duel.chain-1)  in mess:
                                    mess[str(duel.chain-1)] = {}
                                if not "choose" in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["user"] = other_user
                                tmp2["place"] = "field"
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                if not as_monster_effect in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)][as_monster_effect] = []
                                mess[str(duel.chain-1)][as_monster_effect].append(tmp2)
                            else:
                                if not str(duel.chain)  in cost:
                                    cost[str(duel.chain)] = {}
                                if not "choose" in cost[str(duel.chain)]:
                                    cost[str(duel.chain)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["user"] = other_user
                                tmp2["place"] = "field"
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                if not as_monster_effect[1:] in cost[str(duel.chain)]:
                                    cost[str(duel.chain)][as_monster_effect[1:]] = []
                                cost[str(duel.chain)][as_monster_effect[1:]].append(tmp2)
                    else:
                        if(field["det"] is None):
                            return HttpResponse("error")
                        else:
                            if( not validate_answer(duelobj,field["det"],monster_effect_det_monster,exclude,duel)):
                                return HttpResponse("error")
                            check_array.append(field["det"]);
                            if cost_flag == 0:
                                if not str(duel.chain-1)  in mess:
                                    mess[str(duel.chain-1)] = {}
                                if not "choose" in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["place_id"] = field["det"]["place_unique_id"]
                                tmp2["user"] = other_user
                                tmp2["place"] = "field"
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                if not as_monster_effect in mess[str(duel.chain-1)]:
                                    mess[str(duel.chain-1)][as_monster_effect] = []
                                mess[str(duel.chain-1)][as_monster_effect].append(tmp2)
                            else:
                                if not str(duel.chain)  in cost:
                                    cost[str(duel.chain)] = {}
                                if not "choose" in cost[str(duel.chain)]:
                                    cost[str(duel.chain)]["choose"] = []
                                tmp2 = {}
                                tmp2["det"] = field["det"]
                                tmp2["hide"] = field["hide"] if ("hide" in field) else False
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["deck_id"] = 0
                                tmp2["place_id"] = field["det"]["place_unique_id"]
                                tmp2["user"] = other_user
                                tmp2["place"] = "field"
                                tmp2["mine_or_other"] = field["mine_or_other"]
                                if not as_monster_effect[1:] in cost[str(duel.chain)]:
                                    cost[str(duel.chain)][as_monster_effect[1:]] = []
                                cost[str(duel.chain)][as_monster_effect[1:]].append(tmp2)
        else:
            for place in monster_effect_det_monster["place"]:
                place_tmp = place["det"].split("_")
                if(place_tmp[0] == "field"):
                    fields = duelobj.field
                field = fields[x][y]
                if field["kind"].find(place_tmp[1]) == -1:
                    continue
                if int(field["mine_or_other"]) != 0:
                    continue

                if(whether_monster == 0):
                    if(field["det"] is not None):
                        return HttpResponse("error")
                    else:
                        if cost_flag == 0:
                            if not str(duel.chain-1)  in mess:
                                mess[str(duel.chain-1)] = {}
                            if not "choose" in mess[str(duel.chain-1)]:
                                mess[str(duel.chain-1)]["choose"] = []
                            tmp2 = {}
                            tmp2["mine_or_other"] = field["mine_or_other"]
                            tmp2["det"] = field["det"]
                            tmp2["hide"] = field["hide"] if ("hide" in field) else False
                            tmp2["x"] = x
                            tmp2["y"] = y
                            tmp2["deck_id"] = 0
                            tmp2["user"] = user
                            tmp2["place"] = "field"
                            if not as_monster_effect in mess[str(duel.chain-1)]:
                                mess[str(duel.chain-1)][as_monster_effect] = []
                            mess[str(duel.chain-1)][as_monster_effect].append(tmp2)
                        else:
                            if not str(duel.chain)  in cost:
                                cost[str(duel.chain)] = {}
                            if not "choose" in cost[str(duel.chain)]:
                                cost[str(duel.chain)]["choose"] = []
                            tmp2 = {}
                            tmp2["det"] = field["det"]
                            tmp2["hide"] = field["hide"] if ("hide" in field) else False
                            tmp2["x"] = x
                            tmp2["y"] = y
                            tmp2["deck_id"] = 0
                            tmp2["user"] = user
                            tmp2["place"] = "field"
                            tmp2["mine_or_other"] = field["mine_or_other"]
                            if not as_monster_effect[1:] in cost[str(duel.chain)]:
                                cost[str(duel.chain)][as_monster_effect[1:]] = []
                            cost[str(duel.chain)][as_monster_effect[1:]].append(tmp2)
                else:
                    if(field["det"] is None):
                        return HttpResponse("error")
                    else:
                        if( not validate_answer(duelobj,field["det"],monster_effect_det_monster,exclude,duel)):
                            return HttpResponse("error")
                        check_array.append(field["det"]);
                        if cost_flag == 0:
                            if not str(duel.chain-1)  in mess:
                                mess[str(duel.chain-1)] = {}
                            if not "choose" in mess[str(duel.chain-1)]:
                                mess[str(duel.chain-1)]["choose"] = []
                            tmp2 = {}
                            tmp2["det"] = field["det"]
                            tmp2["hide"] = field["hide"] if ("hide" in field) else False
                            tmp2["x"] = x
                            tmp2["y"] = y
                            tmp2["deck_id"] = 0
                            tmp2["place_id"] = field["det"]["place_unique_id"]
                            tmp2["user"] = user
                            tmp2["place"] = "field"
                            tmp2["mine_or_other"] = field["mine_or_other"]
                            if not as_monster_effect in mess[str(duel.chain)]:
                                mess[str(duel.chain-1)][as_monster_effect] = []
                            mess[str(duel.chain-1)][as_monster_effect].append(tmp2)
                        else:
                            if not str(duel.chain)  in cost:
                                cost[str(duel.chain)] = {}
                            if not "choose" in cost[str(duel.chain)]:
                                cost[str(duel.chain)]["choose"] = []
                            tmp2 = {}
                            tmp2["det"] = field["det"]
                            tmp2["hide"] = field["hide"] if ("hide" in field) else False
                            tmp2["x"] = x
                            tmp2["y"] = y
                            tmp2["deck_id"] = 0
                            tmp2["place_id"] = field["det"]["place_unique_id"]
                            tmp2["user"] = user
                            tmp2["place"] = "field"
                            tmp2["mine_or_other"] = field["mine_or_other"]
                            if not as_monster_effect[1:] in cost[str(duel.chain)]:
                                cost[str(duel.chain)][as_monster_effect[1:]] = []
                            cost[str(duel.chain)][as_monster_effect[1:]].append(tmp2)
    duelobj.mess = mess
    duelobj.cost = cost
    return

def answer_det(duelobj,duel,user,answer_json,request,ask_org):
    global check_array

    answer = json.loads(answer_json)
    room_number =int(request.POST["room_number"])
    chain_det = json.loads(duel.chain_det)
    chain_user = json.loads(duel.chain_user)
    chain_user = int(chain_user[str(duel.chain-1)])
    if(chain_user == 0):
        if(request.user == duel.user_1):
            chain_user = 1
        else:
            chain_user = 2
    if user == 1:
        other_user = 2
    else:
        other_user = 1
    monster_effect = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)])).monster_effect
    monster_effect_text = json.loads(monster_effect.monster_effect)
    monster_effect_val = monster_effect.monster_effect_val
    exclude = monster_effect_text["exclude"]
    if "whether_monster" in monster_effect_text:
        whether_monster = monster_effect_text["whether_monster"]
    else:
        whether_monster = 0
    monster_effect_text = monster_effect_text["monster"]
    if(len(answer) < duelobj.calculate_boland(monster_effect_text[0]["min_equation_number"]) or len(answer) > duelobj.calculate_boland(monster_effect_text[0]["max_equation_number"])):
        return HttpResponse("error")
    return_val = []
    for answer_val in answer:
        place_for_answer = answer_val["place"]
        if(place_for_answer == "field"):
            if duel.user_1 == request.user:
                if duel.user_turn == 1:
                    if(ask_org == 1 or ask_org== 3):
                        answer_field_det(duelobj,duel,1,answer_val["x"],answer_val["y"],exclude,whether_monster,monster_effect_text,monster_effect_val,request)
                else:
                    if(ask_org == 2 or ask_org== 3):
                        answer_field_det(duelobj,duel,1,answer_val["x"],answer_val["y"],exclude,whether_monster,monster_effect_text,monster_effect_val,request)
            elif duel.user_2 == request.user:
                if duel.user_turn == 2:
                    if(ask_org == 1 or ask_org== 3):
                        answer_field_det(duelobj,duel,2,answer_val["x"],answer_val["y"],exclude,whether_monster,monster_effect_text,monster_effect_val,request)
                else:
                    if(ask_org == 2 or ask_org== 3):
                        answer_field_det(duelobj,duel,2,answer_val["x"],answer_val["y"],exclude,whether_monster,monster_effect_text,monster_effect_val,request)
        else:
            tmp_count = 0
            place_id = answer_val["place_unique_id"]
            mine_or_other = answer_val["mine_or_other"]
            if user == 1:
                if mine_or_other == '1':
                    mine_or_other = 1
                    mine_or_other_org = 1
                elif mine_or_other == '2':
                    mine_or_other = 2
                    mine_or_other_org =2
                else:
                    mine_or_other = 3
                    mine_or_other_org =3
            else:
                if mine_or_other == '1':
                    mine_or_other = 2
                    mine_or_other_org =1
                elif mine_or_other == '2':
                    mine_or_other = 1
                    mine_or_other_org =2
                else:
                    mine_or_other = 3
                    mine_or_other_org =3
            for monster_effect_det in monster_effect_text:
                tmp_count+=1
                as_monster_effect = monster_effect_det["as_monster_condition"]
                if( user == 1 and chain_user == 1 )or (user == 2 and chain_user == 2):
                    if (monster_effect_val == 3) or ( monster_effect_val == 5 and tmp_count == 1) :
                        monster_effect_det_monster = monster_effect_det["monster"]
                        for place in monster_effect_det_monster["place"]:
                            current_place_and_or = place["and_or"]
                            place_tmp = place["det"].split("_")
                            if(place_tmp[0] == "deck"):
                                deck_id = answer_val["deck_id"]
                            elif(place_tmp[0] == "grave"):
                                deck_id = answer_val["grave_id"]
                            elif(place_tmp[0] == "hand"):
                                deck_id = answer_val["hand_id"]

                            if(place_tmp[0] == place_for_answer ):
                                if(place_tmp[0] == "deck" and deck_id == int(place_tmp[1])):
                                    if mine_or_other_org ==1:
                                        tmp = duelobj.decks[deck_id]["mydeck"]
                                    elif mine_or_other_org == 2:
                                        tmp = duelobj.decks[deck_id]["otherdeck"]
                                    else:
                                        tmp = duelobj.decks[deck_id]["commondeck"]
                                    user_decks =  tmp
                                    for user_deck in user_decks:
                                        if place_id== user_deck["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_deck,monster_effect_det_monster,exclude,duel)):
                                                return HttpResponse("error")

                                            check_array.append(user_deck);
                                            tmp = duelobj.mess
                                            if not str(duel.chain-1)  in tmp:
                                                tmp[str(duel.chain-1)] = {}
                                            if not "choose" in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)]["choose"] = []
                                            tmp2 = {}
                                            tmp2["det"] = user_deck
                                            tmp2["mine_or_other"] =mine_or_other
                                            tmp2["user"] = user
                                            tmp2["place"] = "deck"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["place_id"] = place_id
                                            if not as_monster_effect in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)][as_monster_effect] = []
                                            tmp[str(duel.chain-1)][as_monster_effect].append(tmp2)
                                            duelobj.mess= tmp

                                if(place_tmp[0] == "grave" and deck_id == int(place_tmp[1])):
                                    if mine_or_other_org == 1:
                                        tmp = duelobj.graves[deck_id]["mygrave"]
                                    elif mine_or_other_org == 2:
                                        tmp = duelobj.graves[deck_id]["othergrave"]
                                    else:
                                        tmp = duelobj.graves[deck_id]["commongrave"]
                                    user_graves =  tmp
                                    for user_grave in user_graves:
                                        if place_id== user_grave["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_grave,monster_effect_det_monster,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_grave);
                                            tmp = duelobj.mess
                                            if not str(duel.chain-1) in tmp:
                                                tmp[str(duel.chain-1)] = {}
                                            if not "choose" in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)]["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_grave
                                            tmp2["mine_or_other"] =mine_or_other
                                            tmp2["user"] = user
                                            tmp2["place"] = "grave"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_monster_effect in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)][as_monster_effect] = []
                                            tmp[str(duel.chain-1)][as_monster_effect].append(tmp2)
                                            duelobj.mess= tmp

                                if(place_tmp[0] == "hand" and deck_id == int(place_tmp[1])):
                                    deck_id = answer_val["hand_id"]
                                    if mine_or_other_org == 1:
                                        tmp = duelobj.hands[deck_id]["myhand"]
                                    elif mine_or_other_org == 2:
                                        tmp = duelobj.hands[deck_id]["otherhand"]
                                    else:
                                        tmp = duelobj.hands[deck_id]["commonhand"]
                                    user_hands = tmp
                                    for user_hand in user_hands:
                                        if place_id== user_hand["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_hand,monster_effect_det_monster,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_hand);
                                            tmp = duelobj.mess
                                            if not str(duel.chain-1)  in tmp:
                                                tmp[str(duel.chain-1)] = {}
                                            if not "choose" in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)]["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_hand
                                            tmp2["mine_or_other"] =mine_or_other
                                            tmp2["user"] = user
                                            tmp2["place"] = "hand"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_monster_effect in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)][as_monster_effect] = []
                                            tmp[str(duel.chain-1)][as_monster_effect].append(tmp2)
                                            duelobj.mess= tmp

                if( user == 2 and chain_user == 1 )or (user == 1 and chain_user == 2):
                    if (monster_effect_val == 4) or ( monster_effect_val == 5 and tmp_count == 2) :
                        monster_effect_det_monster = monster_effect_det["monster"]
                        for place in monster_effect_det_monster["place"]:
                            current_place_and_or = place["and_or"]
                            place_tmp = place["det"].split("_")

                            if(place_tmp[0] == "deck"):
                                deck_id = answer_val["deck_id"]
                            elif(place_tmp[0] == "grave"):
                                deck_id = answer_val["grave_id"]
                            elif(place_tmp[0] == "hand"):
                                deck_id = answer_val["hand_id"]

                            if(place_tmp[0] == place_for_answer ):
                                if(place_tmp[0] == "deck" and int(place_tmp[1])==deck_id):
                                    if mine_or_other_org == 1:
                                        tmp = duelobj.decks[deck_id]["mydeck"]
                                    elif mine_or_other_org == 2:
                                        tmp = duelobj.decks[deck_id]["otherdeck"]
                                    else:
                                        tmp = duelobj.decks[deck_id]["commondeck"]
                                    user_decks =  tmp
                                    tmp_flag = False
                                    for user_deck in user_decks:
                                        if place_id== user_deck["place_unique_id"]:
                                            tmp_flag = True
                                            if( not validate_answer(duelobj,user_deck,monster_effect_det_monster,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_deck);
                                            tmp = duelobj.mess
                                            if  not str(duel.chain-1)  in tmp:
                                                tmp[str(duel.chain-1)] = {}
                                            if not "choose"  in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)]["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_deck
                                            tmp2["mine_or_other"] =mine_or_other
                                            tmp2["user"] = user
                                            tmp2["place"] = "deck"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_monster_effect in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)][as_monster_effect] = []
                                            tmp[str(duel.chain-1)][as_monster_effect].append(tmp2)
                                            duelobj.mess= tmp
                                    if(tmp_flag==False):
                                        return HttpResponse("error")

                                if(place_tmp[0] == "grave" and int(place_tmp[1])==deck_id):

                                    if mine_or_other_org == 1:
                                        tmp = duelobj.graves[deck_id]["mygrave"]
                                    elif mine_or_other_org == 2:
                                        tmp = duelobj.graves[deck_id]["othergrave"]
                                    else:
                                        tmp = duelobj.graves[deck_id]["commongrave"]
                                    user_graves =  tmp
                                    tmp_flag = False

                                    for user_grave in user_graves:
                                        if place_id== user_grave["place_unique_id"]:
                                            tmp_flag = True
                                            if( not validate_answer(duelobj,user_grave,monster_effect_det_monster,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_grave);
                                            tmp = duelobj.mess
                                            if not str(duel.chain-1)  in tmp:
                                                tmp[str(duel.chain-1)] = {}
                                            if not "choose" in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)]["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_grave
                                            tmp2["mine_or_other"] =mine_or_other
                                            tmp2["user"] = user
                                            tmp2["place"] = "grave"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_monster_effect in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)][as_monster_effect] = []
                                            tmp[str(duel.chain-1)][as_monster_effect].append(tmp2)
                                            duelobj.mess= tmp
                                    if tmp_flag == False:
                                        return HttpResponse("error")
                                if(place_tmp[0] == "hand" and int(place_tmp[1])==deck_id):
                                    deck_id = answer_val["hand_id"]
                                    if mine_or_other_org == 1:
                                        tmp = duelobj.hands[deck_id]["myhand"]
                                    elif mine_or_other_org == 2:
                                        tmp = duelobj.hands[deck_id]["otherhand"]
                                    else:
                                        tmp = duelobj.hands[deck_id]["commonhand"]
                                    user_hands = tmp
                                    tmp_flag = False
                                    for user_hand in user_hands:
                                        if place_id== user_hand["place_unique_id"]:
                                            tmp_flag = True
                                            if( not validate_answer(duelobj,user_hand,monster_effect_det_monster,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_hand);
                                            tmp = duelobj.mess
                                            if not str(duel.chain-1)  in tmp:
                                                tmp[str(duel.chain-1)] = {}
                                            if not "choose" in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)]["choose"] = []
                                            tmp2 = {}
                                            tmp2["det"] = user_hand
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["mine_or_other"] =mine_or_other
                                            tmp2["user"] = user
                                            tmp2["place"] = "hand"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_monster_effect in tmp[str(duel.chain-1)]:
                                                tmp[str(duel.chain-1)][as_monster_effect] = []
                                            tmp[str(duel.chain-1)][as_monster_effect].append(tmp2)
                                            duelobj.mess= tmp
                                    if tmp_flag == False:
                                        return HttpResponse("error")
    choices = None
    if duel.ask== 0:
        chain_det = json.loads(duel.chain_det)
        current_chain = chain_det[str(duel.chain-1)]
        effect = MonsterEffectWrapper.objects.get(id = current_chain)
        if effect.pac :
            next_effect= duelobj.push_pac(effect.pac)
        else:
            next_effect = effect.monster_effect_next
        if(next_effect != 0):
            chain_det[str(duel.chain-1)] = next_effect.id
        else:
            pac = json.loads(duel.in_pac)
            if pac != []:
                pac_id = pac.pop()
                pac = Pac.objects.get(id=pac_id)
                effect_next =  pac.monster_effect_next
                chain_det[str(duel.chain-1)] = next_effect.id
            else:
                duel.chain-=1
        duel.chain_det = json.dumps(chain_det)
        decks = Deck.objects.all()
        graves = Grave.objects.all()
        hands = Hand.objects.all()
        duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
        duelobj.retrieve_chain(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
        if duel.chain == 0:
            duel.appoint = duel.user_turn
            if duel.timing is not None:
                if duel.timing.timing_auto == True:
                    duel.timing = duel.timing.next_timing
                    if duel.timing is None:
                        duel.timing_mess = "{}"
            tmp ={}
            duel.mess = json.dumps(tmp)
            duel.cost_result = json.dumps(tmp)
            duel.cost = json.dumps(tmp)
            duelobj.invoke_trigger_waiting(duel.trigger_waiting)
            duel.current_priority = 10000
            choices = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
    #if monster_effect.monster_condition != "":
    #    if not check_condition(duel,monster_effect.monster_condition):
    #        return HttpResponse("error")
    duelobj.save_all(user,other_user,room_number)

    return battle_det(request,duelobj,choices)

def answer_field_det_cost(duelobj,duel,user,x,y,exclude,whether_monster,cost_text,cost_effect_val,request):
    answer_field_det(duelobj,duel,user,x,y,exclude,whether_monster,cost_text,cost_effect_val,request,1)
    duelobj.save_all(user,other_user,room_number)

    return battle_det(request,duelobj,choices)

def answer_field_det_cost(duelobj,duel,user,x,y,exclude,whether_monster,cost_text,cost_effect_val,request):
    answer_field_det(duelobj,duel,user,x,y,exclude,whether_monster,cost_text,cost_effect_val,request,1)
def answer_det_cost(duelobj,duel,user,answer,request,ask_org):
    global check_array
    room_number =int(request.POST["room_number"])

    cost_det = duel.cost_det
    cost_user = duel.cost_user
    if(cost_user == 0):
        if(request.user == duel.user_1):
            cost_user = 1
        else:
            cost_user = 2
    cost = CostWrapper.objects.get(id = cost_det).cost
    cost_text = json.loads(cost.cost)
    cost_effect_val = cost.cost_val
    exclude = cost_text["exclude"]
    if "whether_monster" in cost_text:
        whether_monster = cost_text["whether_monster"]
    else:
        whether_monster = 0
    cost_text = cost_text["monster"]
    return_val = []
    if(len(answer) < duelobj.calculate_boland(cost_text[0]["min_equation_number"]) or len(answer) > duelobj.calculate_boland(cost_text[0]["max_equation_number"])):
        return HttpResponse("error")
    for answer_val in answer:
        place_for_answer = answer_val["place"]
        if(place_for_answer == "field"):
            if duel.user_1 == request.user:
                if duel.user_turn == 1:
                    if(ask_org == 1 or ask_org== 3):
                        answer_field_det_cost(duelobj,duel,1,answer_val["x"],answer_val["y"],exclude,whether_monster,cost_text,cost_effect_val,request)

                else:
                    if(ask_org == 2 or ask_org== 3):
                        answer_field_det_cost(duelobj,duel,1,answer_val["x"],answer_val["y"],exclude,whether_monster,cost_text,cost_effect_val,request)
            elif duel.user_2 == request.user:
                if duel.user_turn == 2:
                    if(ask_org == 1 or ask_org== 3):
                        answer_field_det_cost(duelobj,duel,2,answer_val["x"],answer_val["y"],exclude,whether_monster,cost_text,cost_effect_val,request)
                else:
                    if(ask_org == 2 or ask_org== 3):
                        answer_field_det_cost(duelobj,duel,2,answer_val["x"],answer_val["y"],exclude,whether_monster,cost_text,cost_effect_val,request)
        else:
            place_id = answer_val["place_unique_id"]
            mine_or_other = int(answer_val["mine_or_other"])
            if user == 2:
                if mine_or_other == 1:
                    mine_or_other_absolute = 2
                elif mine_or_other == 2:
                    mine_or_other_absolute = 1

            for cost_det in cost_text:
                as_cost = cost_det["as_cost_from"]
                if( user == 1 and cost_user == 1 )or (user == 2 and cost_user == 2):
                    if int(cost_det["who_choose"]) == 0 :
                        for place in cost_det["place"].values():
                            place_tmp = place["det"].split("_")

                            if(place_tmp[0] == place_for_answer ):
                                if(place_tmp[0] == "deck"):
                                    deck_id = answer_val["deck_id"]
                                    if mine_or_other ==1:
                                        tmp = duelobj.decks[deck_id]["mydeck"]
                                    elif mine_or_other == 2:
                                        tmp = duelobj.decks[deck_id]["otherdeck"]
                                    else:
                                        tmp = duelobj.decks[deck_id]["commondeck"]
                                    user_decks =  tmp
                                    for user_deck in user_decks:
                                        if place_id== user_deck["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_deck,cost_det,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_deck);
                                            tmp3 = duelobj.cost
                                            tmp = tmp3[str(duel.chain)]
                                            if not "choose" in tmp:
                                                tmp["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_deck
                                            tmp2["mine_or_other"] =mine_or_other_absolute
                                            tmp2["user"] = user
                                            tmp2["place"] = "deck"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_cost in tmp:
                                                tmp[as_cost] = []
                                            tmp[as_cost].append(tmp2)
                                            tmp3[duel.chain] = tmp
                                            duelobj.cost= tmp3

                                if(place_tmp[0] == "grave"):
                                    deck_id = answer_val["grave_id"]
                                    if mine_or_other == 1:
                                        tmp = duelobj.graves[deck_id]["mygrave"]
                                    elif mine_or_other == 2:
                                        tmp = duelobj.graves[deck_id]["othergrave"]
                                    else:
                                        tmp = duelobj.graves[deck_id]["commongrave"]
                                    user_graves =  tmp
                                    for user_grave in user_graves:
                                        if place_id== user_grave["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_grave,cost_det,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_grave);
                                            tmp3 = duelobj.cost
                                            tmp = tmp3[str(duel.chain)]
                                            if not "choose" in tmp:
                                                tmp["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_grave
                                            tmp2["mine_or_other"] =mine_or_other_absolute
                                            tmp2["user"] = user
                                            tmp2["place"] = "grave"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_cost in tmp:
                                                tmp[as_cost] = []
                                            tmp[as_cost].append(tmp2)
                                            tmp3[duel.chain] = tmp
                                            duelobj.cost= tmp3

                                if(place_tmp[0] == "hand"):
                                    deck_id = answer_val["hand_id"]
                                    if mine_or_other == 1:
                                        tmp = duelobj.hands[deck_id]["myhand"]
                                    elif mine_or_other == 2:
                                        tmp = duelobj.hands[deck_id]["otherhand"]
                                    else:
                                        tmp = duelobj.hands[deck_id]["commonhand"]
                                    user_hands = tmp
                                    for user_hand in user_hands:
                                        if place_id== user_hand["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_hand,cost_det,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_hand);
                                            tmp3 = duelobj.cost
                                            tmp = tmp3[str(duel.chain)]
                                            if not "choose" in tmp:
                                                tmp["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_hand
                                            tmp2["mine_or_other"] =mine_or_other_absolute
                                            tmp2["user"] = user
                                            tmp2["place"] = "hand"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_cost in tmp:
                                                tmp[as_cost] = []
                                            tmp[as_cost].append(tmp2)
                                            tmp3[duel.chain] = tmp
                                            duelobj.cost= tmp3

                if( user == 2 and cost_user == 1 )or (user == 1 and cost_user == 2):
                    if int(cost_det["who_choose"]) == 1:
                        for place in cost_det["place"].values():
                            place_tmp = place["det"].split("_")

                            if(place_tmp[0] == place_for_answer ):
                                if(place_tmp[0] == "deck"):
                                    deck_id = answer_val["deck_id"]
                                    if mine_or_other ==1:
                                        tmp = duelobj.decks[deck_id]["mydeck"]
                                    elif mine_or_other == 2:
                                        tmp = duelobj.decks[deck_id]["otherdeck"]
                                    else:
                                        tmp = duelobj.decks[deck_id]["commondeck"]
                                    user_decks =  tmp
                                    for user_deck in user_decks:
                                        if place_id== user_deck["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_deck,cost_det,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_deck);
                                            tmp3 = duelobj.cost
                                            tmp = tmp3[str(duel.chain)]
                                            if not "choose" in tmp:
                                                tmp["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_deck
                                            tmp2["mine_or_other"] =mine_or_other_absolute
                                            tmp2["user"] = user
                                            tmp2["place"] = "deck"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_cost in tmp:
                                                tmp[as_cost] = []
                                            tmp[as_cost].append(tmp2)
                                            tmp3[duel.chain] = tmp
                                            duelobj.cost= tmp3

                                if(place_tmp[0] == "grave"):
                                    deck_id = answer_val["grave_id"]
                                    if mine_or_other == 1:
                                        tmp = duelobj.graves[deck_id]["mygrave"]
                                    elif mine_or_other == 2:
                                        tmp = duelobj.graves[deck_id]["othergrave"]
                                    else:
                                        tmp = duelobj.graves[deck_id]["commongrave"]
                                    user_graves =  tmp
                                    for user_grave in user_graves:
                                        if place_id== user_grave["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_grave,cost_det,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_grave);
                                            tmp3 = duelobj.cost
                                            tmp = tmp3[str(duel.chain)]
                                            if not "choose" in tmp:
                                                tmp["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_grave
                                            tmp2["mine_or_other"] =mine_or_other_absolute
                                            tmp2["user"] = user
                                            tmp2["place"] = "grave"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_cost in tmp:
                                                tmp[as_cost] = []
                                            tmp[as_cost].append(tmp2)
                                            tmp3[duel.chain] = tmp
                                            duelobj.cost= tmp3
                                if(place_tmp[0] == "hand"):
                                    deck_id = answer_val["hand_id"]
                                    if mine_or_other == 1:
                                        tmp = duelobj.hands[deck_id]["myhand"]
                                    elif mine_or_other == 2:
                                        tmp = duelobj.hands[deck_id]["otherhand"]
                                    else:
                                        tmp = duelobj.hands[deck_id]["commonhand"]
                                    user_hands = tmp
                                    for user_hand in user_hands:
                                        if place_id== user_hand["place_unique_id"]:
                                            if( not validate_answer(duelobj,user_hand,cost_det,exclude,duel)):
                                                return HttpResponse("error")
                                            check_array.append(user_hand);
                                            tmp3 = duelobj.cost
                                            tmp = tmp3[str(duel.chain)]
                                            if not "choose" in tmp:
                                                tmp["choose"] = []
                                            tmp2 = {}
                                            tmp2["x"] = 0
                                            tmp2["y"] = 0
                                            tmp2["det"] = user_hand
                                            tmp2["mine_or_other"] =mine_or_other_absolute
                                            tmp2["user"] = user
                                            tmp2["place"] = "hand"
                                            tmp2["deck_id"] = deck_id
                                            tmp2["place_id"] = place_id
                                            if not as_cost in tmp:
                                                tmp[as_cost] = []
                                            tmp[as_cost].append(tmp2)
                                            tmp3[duel.chain] = tmp
                                            duelobj.cost= tmp3
    if cost.cost_condition != "":
        if not check_condition(cost.cost_condition):
            return HttpResponse("error")
    if duel.ask== 0:
        cost_det = duel.cost_det
        effect = CostWrapper.objects.get(id = cost_det)
        next_effect = effect.cost_next
        duel.cost_det = next_effect.id
        tmp = duelobj.pay_cost(next_effect,user)
        if(next_effect == 0 or tmp == True):
            duelobj.end_cost(duel.cost_user)
            duel.save()
    return battle_det(request,duelobj)

def validate_answer(duelobj,monster,effect_det,exclude,duel):
    cost =duelobj.cost
    mess =duelobj.mess
    if duel.in_cost == True:
        if str(duel.chain) in cost:
            cost = cost[str(duel.chain)]
        else:
            cost = []
    else:
        if str(duel.chain-1) in cost:
            cost = cost[str(duel.chain-1)]
        else:
            cost = []
    if str(duel.chain-1) in mess:
        mess = mess[str(duel.chain-1)]
    else:
        mess= []
    timing_mess = duel.timing_mess
    if(exclude !=""):
        excludes = exclude.split(",")
        for exclude_det in excludes:

            if exclude_det[0]=="~":
                if exclude_det[1:] in cost:
                    for cost_det in cost[exclude_det[1:]]:
                        if(monster["place_unique_id"] == cost_det["place_id"]):
                            return False
            if exclude_det[0]=="%":
                if exclude_det[1:] in timing_mess:
                    for timing_det in timing_mess[exclude_det[1:]]:
                        if(monster["place_unique_id"] == timing_det["place_id"]):
                            return False
            elif exclude_det in mess:
                for mess_det in mess[exclude_det]:
                    if(monster["place_unique_id"] == mess_det["place_id"]):
                        return False

    if "flag" in effect_det:
        flag = effect_det["flag"]
        if flag != "":
            if(flag["operator"] == "="):
                if(monster["flag"] != int(flag["flag_det"])):
                    return False
    monster_name_kind = effect_det["monster_name_kind"]
    name_flag = True
    current_and_or = "and"
    for name_kind in monster_name_kind:
        if name_kind != "":
            if(name_kind["operator"] == "="):
                if(monster["monster_name"] != duelobj.get_name(name_kind["monster_name"])):
                    if(current_and_or == "and"):
                        name_flag = False
                else:
                    if(current_and_or == "or"):
                        name_flag = True
                current_and_or = name_kind["and_or"]


            elif(name_kind["operator"] == "like"):
                if(monster["monster_name"].find(duelobj.get_name(name_kind["monster_name"])) >-1):
                    if(current_and_or == "and"):
                        name_flag = False
                else:
                    if(current_and_or == "or"):
                        name_flag = True
                current_and_or = name_kind["and_or"]
    if name_flag == False:
            return False

    monster_condition_val = effect_det["monster_condition"]
    for cond_det in monster_condition_val:
        cond_flag = True
        current_and_or = "and"
        tmp_flag = True

        for cond_val in cond_det:
            if( not  cond_val ):
                continue
            tmp = monster["variables"][cond_val["name"]]
            if cond_val["init"] == 0:
                value = tmp["value"]
            elif cond_val["init"] == 1:
                value = tmp["i_val"]
            elif cond_val["init"] == 2:
                value = tmp["i_i_val"]
            if(cond_val["operator"] == "=" or cond_val["operator"] == "" ):
                if int(value) != duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            elif(cond_val["operator"] == "<="):
                if int(value) > duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            elif(cond_val["operator"] == ">="):
                if int(value) < duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            elif(cond_val["operator"] == "!="):
                if int(value) == duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            if current_and_or == "and":
                if(cond_flag == True):
                    cond_flag = tmp_flag

            else:
                if(cond_flag == False):
                    cond_flag = tmp_flag
        if(cond_flag == False):
            return False
    custom_monster_condition = effect_det["custom_monster_condition"]
    cond_flag = True
    current_and_or = "and"
    tmp_flag = True
    for cond_det in custom_monster_condition:
        for cond_val in cond_det:
            if( not  cond_val ):
                continue
            tmp = monster["custom_variables"][cond_val["name"]]
            if cond_val["init"] == 0:
                value = tmp["value"]
            elif cond_val["init"] == 1:
                value = tmp["i_val"]
            elif cond_val["init"] == 2:
                value = tmp["i_i_val"]
            if(cond_val["operator"] == "=" or cond_val["operator"] == "" ):
                if int(value) != duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            elif(cond_val["operator"] == "<="):
                if int(value) > duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            elif(cond_val["operator"] == ">="):
                if int(value) < duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            elif(cond_val["operator"] == "!="):
                if int(value) == duelobj.calculate_boland(cond_val["num"]):
                    tmp_flag= False
            if current_and_or == "and":
                if(cond_flag == True):
                    cond_flag = tmp_flag

            else:
                if(cond_flag == False):
                    cond_flag = tmp_flag
    if cond_flag == False:
            return False
    return True

def check_condition(duel,monster_condition):
    duelobj = DuelObj(room_number)
    duelobj.duel = duel
    global check_array
    effect_det_org = json.loads(monster_condition)
    effect_det = effect_det_org["monster"][0]["monster"]

    monster_name_kind = effect_det["monster_name_kind"]
    current_and_or = "and"
    check_variable = 0
    for monster in check_array:
        name_flag = True
        for name_kind in monster_name_kind:
            if name_kind != "":
                if(name_kind["operator"] == "="):
                    if(monster["monster_name"] != duelobj.get_name(name_kind["monster_name"])):
                        if(current_and_or == "and"):
                            name_flag = False
                    else:
                        if(current_and_or == "or"):
                            name_flag = True
                    current_and_or = name_kind["and_or"]


                elif(name_kind["operator"] == "like"):
                    if(monster["monster_name"].find(duelobj.get_name(name_kind["monster_name"])) >-1):
                        if(current_and_or == "and"):
                            name_flag = False
                    else:
                        if(current_and_or == "or"):
                            name_flag = True
                    current_and_or = name_kind["and_or"]
        if name_flag == False:
           continue

        monster_condition_val = effect_det["monster_condition"]
        for cond_det in monster_condition_val:
            cond_flag = True
            current_and_or = "and"
            tmp_flag = True

            for cond_val in cond_det:
                if( len(cond_val) == 0 ):
                    continue

                tmp = monster["variables"][cond_val["name"]]
                if cond_val["init"] == 0:
                    value = tmp["value"]
                elif cond_val["init"] == 1:
                    value = tmp["i_val"]
                elif cond_val["init"] == 2:
                    value = tmp["i_i_val"]
                if(cond_val["operator"] == "=" or cond_val["operator"] == "" ):
                    if int(value) != duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "<="):
                    if int(value) > duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == ">="):
                    if int(value) < duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "!="):
                    if int(value) == duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                if current_and_or == "and":
                    if(cond_flag == True):
                        cond_flag = tmp_flag
                else:
                    if(cond_flag == False):
                        cond_flag = tmp_flag
            if(cond_flag == False):
                break
        if(cond_flag == False):
            continue
        custom_monster_condition = effect_det["custom_monster_condition"]
        for cond_det in custom_monster_condition:
            cond_flag = True
            current_and_or = "and"
            tmp_flag = True
            for cond_val in cond_det:
                if( not  cond_val ):
                    continue
                tmp = monster["custom_variables"][cond_val["name"]]
                if cond_val["init"] == 0:
                    value = tmp["value"]
                elif cond_val["init"] == 1:
                    value = tmp["i_val"]
                elif cond_val["init"] == 2:
                    value = tmp["i_i_val"]
                if(cond_val["operator"] == "=" or cond_val["operator"] == "" ):
                    if int(value) != duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "<="):
                    if int(value) > duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == ">="):
                    if int(value) < duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "!="):
                    if int(value) == duelobj.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                if current_and_or == "and":
                    if(cond_flag == True):
                        cond_flag = tmp_flag

                else:
                    if(cond_flag == False):
                        cond_flag = tmp_flag
            if cond_flag == False:
                break
        if cond_flag == False:
            continue
        check_variable+=1
    if check_variable  < int(effect_det_org["monster"][0]["min_equation_number"]) or check_variable > int(effect_det_org["monster"][0]["max_equation_number"]):
        return False
    return True
