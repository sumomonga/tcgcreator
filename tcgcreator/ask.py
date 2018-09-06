from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.views.generic import View
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Duel,Phase,UserDeck,UserDeckGroup,Config,GlobalVariable,MonsterEffect,MonsterEffectWrapper,DuelDeck,DuelGrave,DuelHand,CostWrapper,Cost
from .forms import EditMonsterVariablesForm,EditMonsterForm,EditMonsterItemForm
from .forms import EditMonsterVariablesKindForm,forms
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck
from pprint import pprint
from django.db.models import Prefetch,Max
import json
from .duel import DuelObj

def ask_place(request):
    decks = Deck.objects.all()
    graves = Grave.objects.all()
    hands = Hand.objects.all()
    room_number =int(request.POST["room_number"])
    config = Config.objects.first()
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    duel = Duel.objects.filter(id=room_number).get()
    phases = Phase.objects.order_by('-priority').filter(show =1)
    variables = GlobalVariable.objects.order_by('-priority').filter(show =1)
    fields = Field.objects.all()
    field_size = FieldSize.objects.first()
    x = range(field_size.field_x)
    y = range(field_size.field_y)
    if(duel.user_1 != request.user and duel.user_2 != request.user):
        return HttpResponseRedirect(reverse('watch_battle'))

    if duel.user_1 == request.user:
        if duel.user_turn == 1:
            if(duel.ask == 1 or duel.ask== 3):
                return show(duel,1,room_number,duel.ask,decks,graves,hands)
        else:
            if(duel.ask == 2 or duel.ask== 3):
                return show(duel,1,room_number,duel.ask,decks,graves,hands)
    elif duel.user_2 == request.user:
        if duel.user_turn == 2:
            if(duel.ask == 1 or duel.ask== 3):
                return show(duel,2,room_number,duel.ask,decks,graves,hands)
        else:
            if(duel.ask == 2 or duel.ask== 3):
                return show(duel,2,room_number,duel.ask,decks,graves,hands)
    return HttpResponse("error")

def show(duel,user,room_number,ask,decks,graves,hands):
    duelobj = DuelObj(room_number)
    duelobj.duel = duel
    duelobj.room_number = room_number
    if user == 1:
        other_user = 2
    elif user == 2:
        other_user = 1
    duelobj.user =user
    duelobj.other_user =other_user
    duelobj.init_all(user,other_user,room_number)
    duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
    cost =duelobj.cost
    mess =duelobj.mess
    if duel.in_cost == True:
        if str(duel.chain) in cost:
            cost_chain = cost[str(duel.chain)]
        else:
            cost_chain = []
    else:
        if str(duel.chain-1) in cost:
            cost_chain = cost[str(duel.chain-1)]
        else:
            cost_chain = []
    if str(duel.chain-1) in mess:
        mess = mess[str(duel.chain-1)]
    else:
        mess= []
    counter = 0
    effect_kind = duel.ask_kind
    if duel.in_cost == True:
        cost_det = duel.cost_det
        effect_user = duel.cost_user
        cost = CostWrapper.objects.get(id = int(cost_det))
        cost_det = cost.cost
        prompt = cost_det.prompt
        sentence = cost_det.sentence
        monster_effect_text_org = json.loads(cost_det.cost)
        if cost_det.cost_val == 3:
            ask_org = 1
        elif cost_det.cost_val == 4:
            ask_org = 2
        elif cost_det.cost_val == 5:
            ask_org = 3
        else:
            ask_org = 0

    else:
        chain_det = json.loads(duel.chain_det)
        chain_user = json.loads(duel.chain_user)
        effect_user = chain_user[str(duel.chain-1)]
        monster_effect = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        monster_effect_det2 = monster_effect.monster_effect
        prompt = monster_effect_det2.prompt
        sentence = monster_effect_det2.sentence
        monster_effect_text_org = json.loads(monster_effect_det2.monster_effect)
        if monster_effect_det2.monster_effect_val == 3:
            ask_org = 1
        elif monster_effect_det2.monster_effect_val == 4:
            ask_org = 2
        elif monster_effect_det2.monster_effect_val == 5:
            ask_org = 3
        else:
            ask_org = 0
    tmp_val = {}
    return_val = []
    if "whether_monster" in monster_effect_text_org:
        whether_monster = monster_effect_text_org["whether_monster"]
    else:
        whether_monster = 0
    monster_effect_text = monster_effect_text_org["monster"]
    exclude = monster_effect_text_org["exclude"]
    for monster_effect_det in monster_effect_text:
        monster_effect_det_monster = monster_effect_det["monster"]
        counter+=1

        if effect_user == user:
            if counter == 1 and ask_org==3 or ask_org == 1:
                place_array = []
                place_tmp = monster_effect_det_monster["place"]
                tmp_place_counter= 0
                for place_key in range(len(place_tmp)):
                    place_and_or = place_tmp[place_key]["and_or"]
                    place_det = place_tmp[place_key]["det"]
                    if place_and_or =="":
                        place_and_or = "or"
                    place_array.append([])
                    place_array[tmp_place_counter].append(place_det)
                    if place_and_or == "and":
                        place_key+=1
                        place_and_or = place_tmp[place_key]["and_or"]
                        place_det = place_tmp[place_key]["det"]
                        place_array[tmp_place_counter][1] = place_det
                        if place_and_or == "and":
                            place_key+=1
                            place_and_or = place_tmp[place_key]["and_or"]
                            place_det = place_tmp[place_key]["det"]
                            place_array[tmp_place_counter][2] = place_det
                            if place_and_or == "and":
                                place_key+=1
                                place_and_or = place_tmp[place_key]["and_or"]
                                place_det = place_tmp[place_key]["det"]
                                place_array[tmp_place_counter][3] = place_det
                                if place_and_or == "and":
                                    place_key+=1
                                    place_and_or = place_tmp[place_key]["and_or"]
                                    place_det = place_tmp[place_key]["det"]
                                    place_array[tmp_place_counter][4] = place_det
                    tmp_place_counter+=1
                for place_each in place_array:
                    place_tmp = place_each[0].split("_")
                    if(place_tmp[0] == "deck"):
                        deck =  Deck.objects.get(id = place_tmp[1])
                        if deck.mine_or_other  == 1:
                            return_val.append(return_deck(duelobj,duel,deck.id,3,place_tmp[2],deck.deck_name,room_number,exclude,monster_effect_det))
                        else:
                            return_val.append(return_deck(duelobj,duel,deck.id,effect_user,place_tmp[2],deck.deck_name,room_number,exclude,monster_effect_det))
                        break;
                    elif place_tmp[0] == "grave":
                        grave =  Grave.objects.get(id = place_tmp[1])
                        if grave.mine_or_other  == 1:
                            return_val.append(return_grave(duelobj,duel,grave.id,3,place_tmp[2],grave.grave_name,room_number,exclude,monster_effect_det))
                        else:
                            return_val.append(return_grave(duelobj,duel,grave.id,effect_user,place_tmp[2],grave.grave_name,room_number,exclude,monster_effect_det))
                    elif place_tmp[0] == "hand":
                        hand =  Hand.objects.get(id = place_tmp[1])
                        if hand.mine_or_other  == 1:
                            return_val.append(return_hand(duelobj,duel,hand.id,3,place_tmp[2],hand.hand_name,room_number,exclude,monster_effect_det))
                        else:
                            return_val.append(return_hand(duelobj,duel,hand.id,effect_user,place_tmp[2],hand.hand_name,room_number,exclude,monster_effect_det))
                    elif place_tmp[0] == "field":
                        kind = ""
                        for place_each2 in place_each:
                            place_tmp2 = place_each2.split("_")
                            if kind == "":
                                kind = place_tmp2[1]
                            else:
                                kind+= "_"+place_tmp2[1]
                        val = {}
                        val["field"] = True
                        val["kind"] = kind
                        val["mine_or_other"] = place_tmp[2]
                        val["monster_effect_det"] = monster_effect_det_monster
                        val["effect_kind"] = effect_kind
                        val["field_info"] = duelobj.field
                        val["user"] = user
                        return_val.append(val)

        else:
            if counter == 2 and ask_org==3 or ask_org == 2:
                place_array = []
                place_tmp = monster_effect_det_monster["place"]
                tmp_place_counter= 0
                for place_key in range(len(place_tmp)):
                    place_and_or = place_tmp[place_key]["and_or"]
                    place_det = place_tmp[place_key]["det"]
                    if place_and_or =="":
                        place_and_or = "or"
                    place_array.append([])
                    place_array[tmp_place_counter].append(place_det)
                    if place_and_or == "and":
                        place_key+=1
                        place_and_or = place_tmp[place_key]["and_or"]
                        place_det = place_tmp[place_key]["det"]
                        place_array[tmp_place_counter][1] = place_det
                        if place_and_or == "and":
                            place_key+=1
                            place_and_or = place_tmp[place_key]["and_or"]
                            place_det = place_tmp[place_key]["det"]
                            place_array[tmp_place_counter][2] = place_det
                            if place_and_or == "and":
                                place_key+=1
                                place_and_or = place_tmp[place_key]["and_or"]
                                place_det = place_tmp[place_key]["det"]
                                place_array[tmp_place_counter][3] = place_det
                                if place_and_or == "and":
                                    place_key+=1
                                    place_and_or = place_tmp[place_key]["and_or"]
                                    place_det = place_tmp[place_key]["det"]
                                    place_array[tmp_place_counter][4] = place_det
                    tmp_place_counter+=1
                for place_each in place_array:
                    place_tmp = place_each[0].split("_")
                    if(place_tmp[0] == "deck"):
                        deck =  Deck.objects.get(id = place_tmp[1])
                        if deck.mine_or_other  == 1:
                            return_val.append(return_deck(duelobj,duel,deck.id,3,place_tmp[2],deck.deck_name,room_number,exclude,monster_effect_det))
                        else:
                            return_val.append(return_deck(duelobj,duel,deck.id,user,place_tmp[2],deck.deck_name,room_number,exclude,monster_effect_det))
                        break;
                    elif place_tmp[0] == "grave":
                        grave =  Grave.objects.get(id = place_tmp[1])
                        if grave.mine_or_other  == 1:
                            return_val.append(return_grave(duelobj,duel,grave.id,3,place_tmp[2],grave.grave_name,room_number,exclude,monster_effect_det))
                        else:
                            return_val.append(return_grave(duelobj,duel,grave.id,user,place_tmp[2],grave.grave_name,room_number,exclude,monster_effect_det))
                    elif place_tmp[0] == "hand":
                        hand =  Hand.objects.get(id = place_tmp[1])
                        if hand.mine_or_other  == 1:
                            return_val.append(return_hand(duelobj,duel,hand.id,3,place_tmp[2],hand.hand_name,room_number,exclude,monster_effect_det))
                        else:
                            return_val.append(return_hand(duelobj,duel,hand.id,user,place_tmp[2],hand.hand_name,room_number,exclude,monster_effect_det))
                    elif place_tmp[0] == "field":
                        kind = ""
                        for place_each2 in place_each:
                            place_tmp2 = place_each2.split("_")
                            if kind == "":
                                kind = place_tmp2[1]
                            else:
                                kind+= "_"+place_tmp2[1]
                        val = {}
                        val["field"] = True
                        val["kind"] = kind
                        val["mine_or_other"] = place_tmp[2]
                        val["monster_effect_det"] = monster_effect_det_monster
                        val["field_info"] = duelobj.field
                        val["user"] = user
                        return_val.append(val)

    tmp_val["return_val"] = return_val
    tmp_val["equation"] = monster_effect_det["equation"]["equation"]
    tmp_val["equation_kind"] = monster_effect_det["equation"]["equation_kind"]
    tmp_val["equation_number"] = monster_effect_det["equation"]["equation_number"]
    tmp_val["min_equation_number"] = duelobj.calculate_boland(monster_effect_det["min_equation_number"])
    tmp_val["max_equation_number"] = duelobj.calculate_boland(monster_effect_det["max_equation_number"])
    tmp_val["whether_monster"] = whether_monster
    tmp_val["sentence"] = sentence
    tmp_val["prompt"] = prompt
    tmp_val["monster_name_kind"] = monster_effect_det_monster["monster_name_kind"]
    if "flag" in monster_effect_det_monster:
        tmp_val["flag"] = monster_effect_det_monster["flag"]
    if "monster_condition" in monster_effect_det_monster:
        tmp_val["variables"] = monster_effect_det_monster["monster_condition"]
    val_exclude = []
    timing_mess = duel.timing_mess
    if exclude != "":
        excludes = exclude.split(",")
        for exclude_det in excludes:

            if(exclude_det[0]=="%"):
                if(exclude_det[1:] in timing_mess):
                    for timing_det in timing_mess[exclude_det[1:]]:
                        val_exclude.append(timing_det["place_id"])
            if(exclude_det[0]=="~"):
                if(exclude_det[1:] in cost_chain):
                    for cost_det in cost_chain[exclude_det[1:]]:
                        val_exclude.append(cost_det["place_id"])
            if(exclude_det in mess):
                 for mess_det in mess[exclude_det]:
                    val_exclude.append(mess_det["place_id"])
    tmp_val["exclude"] = val_exclude
    return HttpResponse(json.dumps(tmp_val))
def return_deck(duelobj,duel,deck_id,user,mine_or_other,deck_name,room_number,exclude="",monster_effect_det=None):
    html = {}
    html["deck_id"] = deck_id;
    html["mine_or_other_val"] = mine_or_other;
    cost =duelobj.cost
    mess =duelobj.mess
    effect_kind = duel.ask_kind
    if duel.in_cost == True:
        if str(duel.chain) in cost:
            cost_chain = cost[str(duel.chain)]
        else:
            cost_chain = []
    else:
        if str(duel.chain-1) in cost:
            cost_chain = cost[str(duel.chain-1)]
        else:
            cost_chain = []
    if str(duel.chain-1) in mess:
        mess = mess[str(duel.chain-1)]
    else:
        mess= []
    if mine_or_other == "1":
            html["mine_or_other"] = "自分の"+deck_name
    elif mine_or_other == "2":
            html["mine_or_other"] = "相手の"+deck_name
            if user == 1:
                user = 2
            elif user==2:
                user = 1
    else:
            html["mine_or_other"] = "共通の"+deck_name
    if mine_or_other == "1":
        tmp = duelobj.decks[deck_id]["mydeck"]
    elif mine_or_other == "2":
        tmp = duelobj.decks[deck_id]["otherdeck"]
    elif mine_or_other == "3":
        tmp = duelobj.decks[deck_id]["commondeck"]
    user_decks = tmp
    html["cards"] = []
    for user_deck in user_decks:
        flag = True;
        if exclude != "":
            excludes = exclude.split(",")
            for exclude_det in excludes:

                if exclude_det in cost:
                    for cost_det in cost[exclude_det]:
                        if(user_deck["place_unique_id"]== cost_det["place_id"]):
                            flag = False
                            continue
                if exclude_det in mess:
                    for mess_det in mess[exclude_det]:
                        if(user_deck["place_unique_id"] == mess_det["place_id"]):
                            flag = False
                            continue
        if not duelobj.check_monster_condition_det(monster_effect_det,user_deck,user,effect_kind,1) :
            flag = False
        if(flag == True):
            tmp = user_deck
            html["cards"].append(tmp)
    return html
def return_grave(duelobj,duel,grave_id,user,mine_or_other,grave_name,room_number,exclude="",monster_effect_det=None):
    cost =json.loads(duel.cost)
    mess =json.loads(duel.mess)
    effect_kind = duel.ask_kind
    html = {}
    html["grave_id"] = grave_id;
    html["mine_or_other_val"] = mine_or_other;
    if mine_or_other == "1":
            html["mine_or_other"] = "自分の"+grave_name
    elif mine_or_other == "2":
            html["mine_or_other"] = "相手の"+grave_name
            if user == 1:
                user = 2
            elif user==2:
                user = 1
    else:
            html["mine_or_other"] = "共通の"+grave_name
    if user == 1:
        tmp = DuelGrave.objects.get(room_number = room_number,mine_or_other = 1,grave_id = grave_id)
    elif user == 2:
        tmp = DuelGrave.objects.get(room_number = room_number,mine_or_other = 2,grave_id = grave_id)
    elif user == 3:
        tmp = DuelGrave.objects.get(room_number = room_number,mine_or_other = 3,grave_id = grave_id)
    user_graves = json.loads(tmp.grave_content)
    html["grave"] = []
    for user_grave in user_graves:
        flag = True;
        if exclude != "":
            excludes = exclude.split(",")
            for exclude_det in excludes:

                if exclude_det in cost:
                    for cost_det in cost[exclude_det]:
                        if(user_grave["place_unique_id"]== cost_det["place_id"]):
                            flag = False
                            continue
                if exclude_det in mess:
                    for mess_det in mess[exclude_det]:
                        if(user_grave["place_unique_id"] == mess_det["place_id"]):
                            flag = False
                            continue
        if duelobj.check_monster_condition_det(monster_effect_det,user_grave,user,effect_kind,1) == False:
            flag = False
        if(flag == True):
            tmp = user_grave
            html["grave"].append(tmp)
    return html
def return_hand(duelobj,duel,hand_id,user,mine_or_other,hand_name,room_number,exclude="",monster_effect_det=None):
    html = {}
    html["hand_id"] = hand_id;
    html["mine_or_other_val"] = mine_or_other;
    cost =json.loads(duel.cost)
    mess =json.loads(duel.mess)
    timing_mess =json.loads(duel.timing_mess)
    effect_kind = duel.ask_kind
    if mine_or_other == "1":
            html["mine_or_other"] = "自分の"+hand_name
    elif mine_or_other == "2":
            html["mine_or_other"] = "相手の"+hand_name
            if user == 1:
                user = 2
            elif user==2:
                user = 1
    else:
            html["mine_or_other"] = "共通の"+hand_name
    if user == 1:
        tmp = DuelHand.objects.get(room_number = room_number,mine_or_other = 1,hand_id = hand_id)
    elif user == 2:
        tmp = DuelHand.objects.get(room_number = room_number,mine_or_other = 2,hand_id = hand_id)
    elif user == 3:
        tmp = DuelHand.objects.get(room_number = room_number,mine_or_other = 3,hand_id = hand_id)
    user_hands = json.loads(tmp.hand_content)
    html["hand"] = []
    for user_hand in user_hands:
        flag = True;
        if exclude != "":
            excludes = exclude.split(",")
            for exclude_det in excludes:

                if exclude_det[0]=="~":
                    if exclude_det[1:] in cost:
                        for cost_det in cost[exclude_det[1:]]:
                            if(user_hand["place_unique_id"]== cost_det["place_id"]):
                                flag = False
                                continue
                elif exclude_det[0]=="%":
                    if exclude_det[1:] in timing_mess:
                        for timing_det in timing_mess[exclude_det[1:]]:
                            if(user_hand["place_unique_id"]== timing_det["place_id"]):
                                flag = False
                                continue
                elif exclude_det in mess:
                    for mess_det in mess[exclude_det]:
                        if(user_hand["place_unique_id"] == mess_det["place_id"]):
                            flag = False
                            continue
        if duelobj.check_monster_condition_det(monster_effect_det,user_hand,user,effect_kind,1) == False:
            flag = False
        if(flag == True):
            tmp = user_hand
            html["hand"].append(tmp)
    return html
