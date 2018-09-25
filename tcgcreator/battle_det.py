from .models import FieldSize,MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,Deck,UserDeck,UserDeckGroup,UserDeckChoice,Duel,Phase,Trigger,Grave,Hand,DuelGrave, CostWrapper,Config,Flag
from django.http import HttpResponse,HttpResponseRedirect
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_user_deck_det
from django.db.models import Q
from django.shortcuts import render
from .duel import DuelObj
from django.db import connection
import json
import copy
from time import time
from pprint import pprint


def send_message(request):
    room_number = int(request.POST["room_number"])
    duel=Duel.objects.get(id=room_number);
    duelobj =  DuelObj(room_number)
    duelobj.duel = duel;
    duelobj.room_number = room_number
    duelobj.in_execute = False
    user_1 = duel.user_1
    user_2 = duel.user_2
    if(request.user != user_1 and request.user != user_2):
        return HttpResponse("error")
    if(request.user == user_1):
        duelobj.user = 1;
        user = 1
        other_user = 2
    if(request.user == user_2):
        duelobj.user = 2;
        user = 2
        other_user = 1
    if user == 1:
        tmp = user_1.first_name+":「"+request.POST["message"]+"』\n"
    else:
        tmp = user_2.first_name+":「"+request.POST["message"]+"」\n"
    log_turn = duel.log_turn+tmp
    log = tmp
    cursor = connection.cursor()
    cursor.execute("update tcgcreator_duel set log_turn = '"+log_turn+"',log = '"+log_turn+"' where id = "+str(room_number))
    return HttpResponse(log_turn)

def battle_det(request,duelobj = None,choices = None):
    room_number = int(request.POST["room_number"])
    if duelobj is None:
        duel=Duel.objects.get(id=room_number);
        duelobj =  DuelObj(room_number)
        duelobj.duel = duel;
        duelobj.room_number = room_number
        duelobj.in_execute = False

        tmp_flag = True
    else:
        duel = duelobj.duel
        tmp_flag = False

    user_1 = duel.user_1
    user_2 = duel.user_2
    if(request.user != user_1 and request.user != user_2):
        return HttpResponse("error")
    if(request.user == user_1):
        duelobj.user = 1;
        user = 1
        other_user = 2
    if(request.user == user_2):
        duelobj.user = 2;
        user = 2
        other_user = 1
    if tmp_flag == True:
        duelobj.init_all(user,other_user,room_number)
    decks = Deck.objects.all()
    graves = Grave.objects.all()
    hands = Hand.objects.all()
    turn = duel.user_turn;
    if choices is None:
        choices = []
        choices.append(None)
        choices.append(10000)
    if duel.winner !=0:
        return battle_det_return_org(duelobj,decks,graves,hands,user,other_user,choices,room_number)
    if duel.appoint != user and duel.ask!=2 and duel.ask != 3:
        return battle_det_return(duelobj,decks,graves,hands,user,other_user,choices,room_number)
    if duel.appoint == user and duel.ask==2 :
        return battle_det_return(duelobj,decks,graves,hands,user,other_user,choices,room_number)
    DuelFlag = Flag.objects.get(id=room_number)
    DuelFlag.flag = True
    DuelFlag.save()

    trigger_waiting = json.loads(duel.trigger_waiting)
    duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
    if (duel.chain == 0 or duel.in_trigger_waiting == True) and trigger_waiting and duel.in_cost == False:
        duelobj.invoke_trigger_waiting(duel.trigger_waiting)
    flag = True
    while flag == True:
        flag = False
        if duel.in_cost == True and duelobj.in_execute == False:
            cost = CostWrapper.objects.get(id = duel.cost_det)
            duelobj.pay_cost(cost,user)
        elif duel.in_cost == False:
            choices = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,other_user,user)
            choices2 = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,other_user,user)
            while True:
                flag_2 = False
                if duel.appoint == other_user:
                    while True:
                        choices2 = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,other_user,user)
                        if choices2[0] is not None:
                            choices[0] = None
                            flag_2 = True
                            break
                        else:
                            choices = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
                            if choices[0] is not None:
                                if duel.appoint == 1:
                                    duel.appoint = 2
                                else:
                                    duel.appoint = 1
                                break
                            else:
                                duel.current_priority = choices2[1]
                                if duel.current_priority == 0:
                                    duel.current_priority = 10000
                                    flag_2 = True
                                    break
                if flag_2 == True:
                    break
                if duel.appoint == user:
                    choices = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
                    choices2 = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,other_user,user)
                    if choices2[1]> choices[1]:
                        if duel.appoint == 1:
                            duel.appoint = 2
                        else:
                            duel.appoint = 1
                        break
                    if choices[0] != "monster_trigger":
                        if(choices[0] is None and choices2[0] is not None and duel.appoint == duel.user_turn):
                            if duel.appoint == 1:
                                duel.appoint = 2
                            else:
                                duel.appoint = 1
                            break
                        elif(choices[0] is None and choices2[0] is not None and duel.appoint != duel.user_turn):
                            duel.current_priority = choices2[1]
                        elif(choices[0] is None and choices2[0] is None and duel.appoint == duel.user_turn and duel.chain == 0 and duel.timing is not None and choices[1]==0):
                            duel.current_priority = choices[1]
                            duel.timing = duel.timing.next_timing
                            if duel.timing is None:
                                duel.timing_mess = "{}"
                            duel.appoint = duel.user_turn
                            duel.current_priority = 10000
                        elif(choices[0] is None and choices2[0] is None and duel.chain == 0 or choices[1] == True):
                            duel.current_priority = choices[1]
                            if duel.current_priority ==0:
                                duel.current_priority = 10000
                                choices = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
                                if choices[0] != True:
                                    break

                        if(choices[0] is None and choices2[0] is None and duel.chain != 0 and duel.ask==0):
                            duelobj.check_eternal_effect(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)
                            fields = duelobj.field
                            pprint(user)
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
                                duel.current_priority = 10000
                                duelobj.invoke_trigger_waiting(duel.trigger_waiting)
                                choices = duelobj.check_trigger(decks,graves,hands,duel.phase,duel.user_turn,user,other_user)

                if not (duel.in_cost == False and (choices[0] is None or choices[0] == True) ) or duel.ask !=0 or duel.winner != 0:
                    break
        if (duel.chain == 0 or duel.in_trigger_waiting == True) and duel.trigger_waiting != "[]" and duel.in_cost == False:
            duelobj.invoke_trigger_waiting(duel.trigger_waiting)
            flag = True
    duelobj.save_all(user,other_user,room_number)
    return battle_det_return(duelobj,decks,graves,hands,user,other_user,choices,room_number)
def battle_det_return(duelobj,decks,graves,hands,user,other_user,choices,room_number):
    duel = duelobj.duel
    if duel.winner !=0:
        return battle_det_return_org(duelobj,decks,graves,hands,user,other_user,choices,room_number)
    return_value={}
    return_value["variable"] = duelobj.get_variables()
    return_value["phase"] = duel.phase.id
    return_value["turn"] = duel.user_turn
    return_value["log"] = duel.log_turn
    if duel.ask > 0:
        return_value["ask_org"] = True
    else:
        return_value["ask_org"] = False
    if duelobj.user == 1:
        return_value["user_name1"] = duel.user_1.first_name
        return_value["user_name2"] =  duel.user_2.first_name
    else:
        return_value["user_name1"] = duel.user_2.first_name
        return_value["user_name2"] =  duel.user_1.first_name
    if(duelobj.user == duel.user_turn):
        if(duel.ask == 1 or duel.ask==3):
            return_value["ask"] = True
        else:
            return_value["ask"] = False

    else:
        if(duel.ask == 2 or duel.ask==3):
            return_value["ask"] = True
        else:
            return_value["ask"] = False
    return_value["ask_det"] = duel.ask_det
    return_value["user"] = user
    return_value["other_user"] = other_user
    if duel.appoint == user:
        return_value["appoint"] = True
    elif duel.appoint == other_user:
        return_value["appoint"] = False
    deck_info = duelobj.get_deck_info(decks,user,other_user,1)
    return_value["deck_info"] = copy.deepcopy(deck_info)
    if duel.appoint == user:
        return_value["deck_info"] = duelobj.modify_deck_info(return_value["deck_info"],decks.count(),user,other_user,choices[1])
    return_value["grave_info"] = duelobj.get_grave_info(graves,user,other_user,1)
    hand_info = duelobj.get_hand_info(hands,user,other_user,1)
    return_value["hand_info"] = copy.deepcopy(hand_info)
    if duel.appoint == user:
        return_value["hand_info"] = duelobj.modify_hand_info(return_value["hand_info"],hands.count(),user,other_user,choices[1])
    field = duelobj.field
    return_value["field_info"] = copy.deepcopy(field)
    if duel.appoint == user:
        return_value["field_info"] = duelobj.modify_field_info(return_value["field_info"],user,other_user,choices[1])
    else:
        return_value["field_info"] = duelobj.modify_field_info(return_value["field_info"],user,other_user,choices[1])
    if (duel.timing != None and duel.appoint == user and duel.ask ==0 and choices[0] is not None) or (duel.chain > 0 and duel.ask==0 and duel.appoint==user):
        return_value["pri"] = True
    else:
        return_value["pri"] = False
    if choices[0] == "monster_trigger":
        return_value["choices"] = None
    else:
        return_value["choices"] = choices[0]
    return_value["audio"] = duel.audio
    config = Config.objects.get()
    limit_time = config.limit_time
    if user == 1:
        return_value["time_1"] = limit_time - (time()-duel.time_1 )
        return_value["time_2"] = limit_time - (time()-duel.time_2 )
    else:
        return_value["time_1"] = limit_time -(time()-duel.time_2)
        return_value["time_2"] = limit_time -(time()-duel.time_1)
    return_value["winner"] = False
    return HttpResponse(json.dumps(return_value))
def battle_det_return_org(duelobj,decks,graves,hands,user,other_user,choices,room_number):
    duel = duelobj.duel
    return_value={}
    return_value["variable"] = duelobj.get_variables()
    return_value["phase"] = duel.phase.id
    return_value["turn"] = duel.user_turn
    return_value["log"] = duel.log_turn
    if duel.ask > 0:
        return_value["ask_org"] = True
    else:
        return_value["ask_org"] = False
    if duelobj.user == 1:
        return_value["user_name1"] = duel.user_1.first_name
        return_value["user_name2"] =  duel.user_2.first_name
    else:
        return_value["user_name1"] = duel.user_2.first_name
        return_value["user_name2"] =  duel.user_1.first_name
    return_value["ask_det"] = duel.ask_det
    return_value["user"] = user
    return_value["other_user"] = other_user
    if duel.appoint == user:
        return_value["appoint"] = True
    elif duel.appoint == other_user:
        return_value["appoint"] = False
    deck_info = duelobj.get_deck_info(decks,user,other_user,1)
    return_value["deck_info"] = copy.deepcopy(deck_info)
    return_value["grave_info"] = duelobj.get_grave_info(graves,user,other_user,1)
    hand_info = duelobj.get_hand_info(hands,user,other_user,1)
    return_value["hand_info"] = copy.deepcopy(hand_info)
    field = duelobj.field
    return_value["field_info"] = copy.deepcopy(field)
    if (duel.timing != None and duel.appoint == user and duel.ask ==0 and choices[0] is not None) or (duel.chain > 0 and duel.ask==0 and duel.appoint==user):
        return_value["pri"] = True
    else:
        return_value["pri"] = False
    if choices[0] == "monster_trigger":
        return_value["choices"] = None
    else:
        return_value["choices"] = choices[0]
    return_value["audio"] = duel.audio
    config = Config.objects.get()
    limit_time = config.limit_time
    return_value["time_1"] = 0
    return_value["time_2"] = 0
    return_value["winner"] = True
    return HttpResponse(json.dumps(return_value))
