from .models import Config,MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,Deck,UserDeck,UserDeckGroup,UserDeckChoice,Duel,Phase,Trigger,Grave,Hand,MonsterEffect,MonsterEffectWrapper,GlobalVariable,Cost,CostWrapper,DuelDeck,DuelGrave,DuelHand,FieldSize,TriggerTiming,Timing,Pac,PacWrapper,PacCost,PacCostWrapper,EternalEffect,VirtualVariable,EternalWrapper,Flag,EternalTrigger
from django.http import HttpResponse,HttpResponseRedirect
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_user_deck_det
from django.db.models import Q
from django.shortcuts import render
from django.db import reset_queries
import logging

import json
import re
import os
import uuid
from django.db import connection
import random
import copy
import math
from pprint import pprint
import numpy as np
from time import time
class DuelObj:

    def __init__(self,room_number):
        flag = Flag.objects.get(id=room_number)
        #if flag.flag == True:
        #    exit(1)
    def copy_monster_from_deck(self,monster):
        return monster
    def copy_monster_from_grave(self,monster):
        return monster
    def copy_monster_from_hand(self,monster):
        return monster
    def copy_monster_from_field(self,monster):
        return monster
    def copy_monster_to_deck(self,monster,deck_id,mine_or_other,variable_names):
        monster["place_unique_id"] = str(uuid.uuid4())
        monster["place"] = "deck";
        monster["mine_or_other"] = mine_or_other;
        monster["deck_id"] = deck_id;
        if "kind" in monster:
            del(monster["kind"])
        return monster
    def copy_monster_to_grave(self,monster,grave_id,mine_or_other,variable_names):
        monster["place_unique_id"] = str(uuid.uuid4())
        monster["place"] = "grave";
        monster["mine_or_other"] = mine_or_other;
        monster["grave_id"] = grave_id;
        if "kind" in monster:
            del(monster["kind"])
        return monster
    def copy_monster_to_hand(self,monster,hand_id,mine_or_other,variable_names):
        monster["place_unique_id"] = str(uuid.uuid4())
        monster["place"] = "hand";
        monster["mine_or_other"] = mine_or_other;
        monster["hand_id"] = hand_id;
        if "kind" in monster:
            del(monster["kind"])
        return monster
    def copy_monster_to_field(self,monster,x,y,mine_or_other,variable_names):
        monster["place_unique_id"] = str(uuid.uuid4())
        monster["place"] = "field";
        monster["x"] = x;
        monster["y"] = y;
        monster["mine_or_other"] = mine_or_other;
        if "kind" in monster:
            del(monster["kind"])
        return monster


    def check_eternal_invalid(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other = -1):
        return self.check_eternal_det(monster,user,effect_kind,place,deck_id,x,y,mine_or_other ,2)
    def check_no_choose(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other = -1,index=None):
        duel = self.duel
        monster_det = Monster.objects.get(id=monster["id"])
        eternals = monster_det.eternal_effect.all()
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for eternal in eternals:
            tmps = json.loads(eternal.eternal_monster)
            kind = eternal.eternal_kind
            tmps = tmps["monster"]
            tmp ={}
            if index is not None:
                tmp["index"] = index
            tmp["eternal"] = eternal.id
            tmp["effect_val"] = eternal.eternal_effect_val
            tmp["kind"] = eternal.eternal_kind
            tmp["priority"] = eternal.priority
            tmp["user"] = user
            if "already" in monster:
                tmp["already"] = monster["already"]
            else:
                tmp["already"] = 0
            tmp["place"] =  place
            tmp["deck_id"] =  deck_id
            tmp["x"] =  x
            tmp["y"] =  y
            tmp["place_id"] =   place_id
            tmp["mine_or_other"] =   mine_or_other
            self.invoke_eternal_effect_det(tmp,user)
        return self.check_eternal_det(monster,user,effect_kind,place,deck_id,x,y,mine_or_other ,1)
    def check_not_effected(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other = -1):
        duel = self.duel
        monster_det = Monster.objects.get(id=monster["id"])
        eternals = monster_det.eternal_effect.all()
        decks = self.deck_structure
        graves = self.grave_structure
        hands = self.hand_structure
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        flag = True
        if not hasattr(self,"not_effected"):
            self.not_effected = []
        elif place_id in self.not_effected:
            flag = False
        else:
            self.not_effected.append(place_id)
        if place == "deck":
            tmp_deck=decks.filter(id = deck_id).get()
            if tmp_deck.eternal == True:
                flag = False
        if place == "grave":
            tmp_deck=graves.filter(id = deck_id).get()
            if tmp_deck.eternal == True:
                flag = False
        if place == "hand":
            tmp_deck=hands.filter(id = deck_id).get()
            if tmp_deck.eternal == True:
                flag = False
        if flag == True:
            for eternal in eternals:
                tmps = json.loads(eternal.eternal_monster)
                kind = eternal.eternal_kind
                tmps = tmps["monster"]
                tmp ={}
                tmp["eternal"] = eternal.id
                tmp["effect_val"] = eternal.eternal_effect_val
                tmp["kind"] = eternal.eternal_kind
                tmp["priority"] = eternal.priority
                tmp["user"] = user
                if "already" in monster:
                    tmp["already"] = monster["already"]
                else:
                    tmp["already"] = 0
                tmp["place"] =  place
                tmp["deck_id"] =  deck_id
                tmp["place_id"] =   place_id
                tmp["x"] =  x
                tmp["y"] =  y
                tmp["mine_or_other"] =   mine_or_other
                self.invoke_eternal_effect_det(tmp,user)
        if place_id in self.not_effected:
            self.not_effected.remove(place_id)
        return self.check_eternal_det(monster,user,effect_kind,place,deck_id,x,y,mine_or_other ,0)
    def check_invoke_invalid(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other = -1,persist=0):
        return self.check_eternal_det(monster,user,effect_kind,place,deck_id,x,y,mine_or_other ,3,persist)
    def check_no_invoke(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other = -1,persist = 0):
        return self.check_eternal_det(monster,user,effect_kind,place,deck_id,x,y,mine_or_other ,5,persist)
    def check_change_val(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other = -1):
        return self.check_change_val(monster,user,effect_kind,place,deck_id,x,y,mine_or_other ,4)
    def check_eternal_det(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other = -1,mode=0,persist = 0):
        field = self.field
        effect_kinds = effect_kind.split("_")
        mine_or_other = int(mine_or_other)
        if mode == 0:
            condition = self.not_effected_eternal_effect
            choose = 0
        elif mode == 1:
            condition = self.no_choose_eternal_effect
            choose = 0
        elif mode == 2:
            condition = self.not_eternal_effect
            choose = 2
        elif mode == 3:
            condition = self.invoke_invalid_eternal_effect
            choose = 2
        elif mode == 4:
            condition = self.change_val_eternal_effect
            choose = 2
        elif mode == 5:
            condition = self.no_invoke_eternal_effect
            choose = 2
        for not_effected in condition:
            if persist == 1:
                if not_effected["persist"] == 0:
                    continue
            invalid_kinds = not_effected["invalid_kinds"].split("_")
            kind_flag = False
            if "-1" in invalid_kinds:
                kind_flag = True
            else:
                for invalid_kind in invalid_kinds:
                    if invalid_kind in effect_kinds:
                        kind_flag = True
                        break

            if kind_flag == False:
                continue
            place_id = not_effected["place_id"]
            eternals = EternalEffect.objects.get(id=not_effected["eternal"])
            if monster is None and eternals.invalid_none_monster:
                 return True
            eternals = json.loads(eternals.invalid_monster)
            eternals = eternals["monster"]
            for eternal in eternals:
                eternal_det=eternal["monster"]
                if eternal["as_monster_condition"] == "trigger":
                    if place_id == monster["place_unique_id"]:
                        return True
                if not eternal_det["place"]:
                    continue
                for place_det in eternal_det["place"]:
                    place_det_det = place_det["det"].split("_")
                    mine_or_other2 = place_det_det[2]
                    if place == place_det_det[0]:
                        if place == "field":
                            if mine_or_other2 == -1:
                                pass
                            elif mine_or_other2 != field[x][y]["mine_or_other"]:
                                continue
                            kind = field[x][y]["kind"]
                            if kind != "":
                                kind = kind.split("_")
                            if place_det_det[1] in kind:
                                if self.check_monster_condition_det(eternal,monster,user,effect_kind,choose,None,0,0,0):
                                    return True
                        else:
                            if(int(place_det_det[1]) == int(deck_id) ):
                                if int(mine_or_other2) == -1:
                                    pass
                                if int(mine_or_other2)  == 1:
                                    if (user == 1 and mine_or_other == 1) or (user == 2 and mine_or_other == 2):
                                        pass
                                    else:
                                        continue
                                elif int(mine_or_other2)  == 2:
                                    if (user == 1 and mine_or_other == 2) or (user == 2 and mine_or_other == 1):
                                        pass
                                    else:
                                        continue
                            else:
                                continue
                            if self.check_monster_condition_det(eternal,monster,user,effect_kind,choose,place_det_det[0],place_det_det[1],0,0,mine_or_other):
                                return True

        return False

    def check_monster_condition_det(self, monster_condition: object, monster: object, user: object,effect_kind="",choose=0,place=None,deck_id=0,x=0,y=0,mine_or_other = -1) -> object:
        monster_condition = monster_condition["monster"]
        flag = monster_condition["flag"]
        if choose == 1 and effect_kind != "":
            if self.check_no_choose(monster,user,effect_kind,place,deck_id,x,y,mine_or_other):
                return False
        elif choose == 2 and effect_kind != "":
            if self.check_not_effected(monster,user,effect_kind,place,deck_id,x,y,mine_or_other):
                return False
        if flag != None and flag != "":
            if(flag["operator"] == "="):
                if(monster["flag"] != int(flag["flag_det"])):
                    return False
        if("place_id" in monster_condition and monster_condition["place_id"]!= ""):
            if monster["place_unique_id"] != self.get_place_unique_id(monster_condition["place_id"]):
                return False
        if("unique_id" in monster_condition and monster_condition["unique_id"]!= ""):
            if monster["card_unique_id"] != self.get_card_unique_id(monster_condition["unique_id"]):
                return False

        monster_name_kind =  monster_condition["monster_name_kind"]
        name_flag = True;
        current_and_or = "and"
        for name_kind in monster_name_kind:
            if name_kind != "":
                if(name_kind["operator"] == "="):
                    if(monster["monster_name"] != self.get_name(name_kind["monster_name"])):
                        if(current_and_or == "and"):
                            name_flag = False
                    else:
                        if(current_and_or == "or"):
                            name_flag = True
                    current_and_or = name_kind["and_or"]


                elif(name_kind["operator"] == "like"):
                    if(monster["monster_name"].find(self.get_name(name_kind["monster_name"])) >-1):
                        if(current_and_or == "and"):
                            name_flag = False
                    else:
                        if(current_and_or == "or"):
                            name_flag = True
                    current_and_or = name_kind["and_or"]
        if name_flag == False:
            return False
        monster_condition_val = monster_condition["monster_condition"]
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
                    if int(value) != self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "<="):
                    if int(value) > self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == ">="):
                    if int(value) < self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "!="):
                    if int(value) == self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                if current_and_or == "and":
                    if(cond_flag == True):
                        cond_flag = tmp_flag
                    else:
                        cond_flag = False

                else:
                    if(cond_flag == False):
                        cond_flag = tmp_flag
                    else:
                        cond_flag = True
            if(cond_flag == False):
                return False
        custom_monster_condition = monster_condition["custom_monster_condition"]
        for cond_det in custom_monster_condition:
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
                    if int(value) != self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "<="):
                    if int(value) > self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == ">="):
                    if int(value) < self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "!="):
                    if int(value) == self.calculate_boland(cond_val["num"]):
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
    def check_monster_condition(self,monster_conditions,user,cost=False,monster=None):
        duel = self.duel
        room_number = self.room_number
        and_or_all = "and"
        flag = True
        for monster_condition in monster_conditions:
            as_flag = False
            count = 0
            variety = []
            variable_variety = []
            variable_counter = 0
            counter = -1
            x_counter = 0
            y_counter = 0
            equation_kind =monster_condition["equation"]["equation_kind"]
            if(equation_kind == "x"):
                counter = "x"
            elif(equation_kind == "y"):
                counter = "y"
            elif(equation_kind != "number" and equation_kind != "kind"):
                counter= equation_kind
            if monster_condition["as_monster_condition"]:
                as_flag = True
                as_monsters = monster_condition["as_monster_condition"].split(",")
                for as_monster in as_monsters:
                    if as_monster[0] != "~" and as_monster[0] != "%":
                        tmp = self.mess
                        if as_monster not in tmp[str(duel.chain-1)]:
                            continue
                        monsters = tmp[str(duel.chain-1)][as_monster]
                    elif as_monster[0] == "%":
                        tmp = self.timing_mess
                        if as_monster[1:] not in tmp:
                            continue
                        monsters = tmp[as_monster[1:]]
                    elif as_monster[0] == "~":
                        tmp = self.cost
                        if(duel.in_cost == True):
                            if as_monster[1:] not in tmp[str(duel.chain)]:
                                continue
                            monsters = tmp[str(duel.chain)][as_monster[1:]]
                        else:
                            if as_monster[1:] not in tmp[str(duel.chain-1)]:
                                continue
                            monsters = tmp[str(duel.chain-1)][as_monster[1:]]
                    for monster2 in monsters:
                        if self.check_monster_condition_det(monster_condition,monster2["det"],user,"",0,monster2["place"],monster2["deck_id"],monster2["x"],monster2["y"],monster2["mine_or_other"]) == True:
                            if counter == "x":
                                x_counter += monster2["x"]
                            elif counter == "y":
                                y_counter += monster2["y"]
                            elif counter != -1:
                                variable =monster2["det"]["variables"][counter]["value"]
                                tmp_varieties = variable.split("_")
                                for tmp_variety  in tmp_varieties:
                                    variable_variety.append(tmp_variety)
                                variable_counter += int(variable["value"])
                                if monster2["det"]["id"] not in variety:
                                    variety.append(monster2["det"]["id"])
                            count+=1
            place = monster_condition["monster"]["place"];
            if(place and as_flag == False):
                current_and_or = "and"
                for place_tmp in place:
                    place_tmp = place_tmp["det"].split("_")
                    deck_id = place_tmp[1]
                    mine_or_other = int(place_tmp[2])
                    if(( user == 1 and mine_or_other == 1) or ( user==2 and mine_or_other == 2)):
                        mine_or_other = 1
                    elif(( user == 1 and mine_or_other == 2) or ( user==2 and mine_or_other == 1)):
                        mine_or_other = 2
                    else:
                        mine_or_other = 3
                    if(place_tmp[0] == "field" ):
                        field = self.field
                        for x in range(len(field)):
                            for y in range(len(field[x])):
                                kind = field[x][y]["kind"]
                                mine_or_other_field = field[x][y]["mine_or_other"]
                                #if user != 1:
                                #    if mine_or_other_field ==1:
                                #       mine_or_other_field = 2
                                #    elif mine_or_other_field ==2:
                                #        mine_or_other_field = 1
                                if kind != "":
                                    tmp = kind.split("_")
                                else:
                                    tmp = []
                                    tmp.appned("99999")
                                if deck_id in tmp and mine_or_other == mine_or_other_field:
                                    if "det" in field[x][y] and field[x][y]["det"] != None:
                                        if self.check_monster_condition_det(monster_condition,field[x][y]["det"],user,"",0,"field",None,x,y,field[x][y]["mine_or_other"]) == True:
                                            count+=1
                                            if field[x][y]["det"]["id"] not in variety:
                                                variety.append(field[x][y]["det"]["id"])

                                            if counter == "x":
                                                x_counter += x
                                            if counter == "y":
                                                y_counter += y
                                            if counter != -1:
                                                variable = field[x][y]["det"]["variables"][counter]
                                                tmp_varieties = variable["value"].split("_")
                                                for tmp_variety in tmp_varieties:
                                                    if(tmp_variety not in variable_variety):
                                                        variable_variety.append(tmp_variety)
                                                variable_counter += int(variable["value"])

                    if(place_tmp[2] == "1" and user== self.user) or (place_tmp[2] == "2" and user != self.user):
                        mine_or_other2 = 1
                    elif(place_tmp[2] == "1" and user!= self.user) or (place_tmp[2] == "2" and user == self.user):
                        mine_or_other2 = 2
                    else:
                        mine_or_other2 = 3
                    if(place_tmp[2] == "1" and user== 1) or (place_tmp[2] == "2" and user != 1):
                        mine_or_other3 = 1
                    elif(place_tmp[2] == "1" and user!= 1) or (place_tmp[2] == "2" and user == 1):
                        mine_or_other3 = 2
                    else:
                        mine_or_other3 = 3
                    if(place_tmp[0] == "deck" ):
                        deck_id = int(deck_id)
                        if mine_or_other2 == 1:
                            deck = self.decks[deck_id]["mydeck"]
                        elif mine_or_other2 == 2:
                            deck = self.decks[deck_id]["otherdeck"]
                        elif mine_or_other2 == 3:
                            deck = self.decks[deck_id]["3commondeck"]
                        for j in range(len(deck)):
                            if self.check_monster_condition_det(monster_condition,deck[j],user,"",0,"deck",deck_id,0,0,mine_or_other3) == True:
                                if deck[j]["id"] not in variety:
                                    variety.append(deck[j]["id"])
                                count+=1
                                if counter != -1:
                                    variable = deck[j]["variables"][counter]
                                    tmp_varieties = variable["value"].split("_")
                                    for tmp_variety in tmp_varieties:
                                        if(tmp_variety not in variable_variety):
                                            variable_variety.append(tmp_variety)
                                    variable_counter += int(variable["value"])
                    if(place_tmp[0] == "grave" ):
                        grave_id = int(deck_id)
                        if mine_or_other2 == 1:
                            grave = self.graves[grave_id]["mygrave"]
                        elif mine_or_other2 == 2:
                            grave = self.graves[grave_id]["othergrave"]
                        elif mine_or_other2 == 3:
                            grave = self.graves[grave_id]["commongrave"]
                        for j in range(len(grave)):
                            if self.check_monster_condition_det(monster_condition,grave[j],user,"",0,"grave",deck_id,0,0,mine_or_other3) == True:
                                if grave[j]["id"] not in variety:
                                    variety.append(grave[j]["id"])
                                count+=1
                                if counter != -1:
                                    variable = grave[j]["variables"][counter]
                                    tmp_varieties = variable["value"].split("_")
                                    for tmp_variety in tmp_varieties:
                                        if(tmp_variety not in variable_variety):
                                            variable_variety.append(tmp_variety)
                                    variable_counter += int(variable["value"])
                    if(place_tmp[0] == "hand" ):
                        hand_id = int(deck_id)
                        if mine_or_other2 == 1:
                            hand = self.hands[hand_id]["myhand"]
                        elif mine_or_other2 == 2:
                            hand = self.hands[hand_id]["otherhand"]
                        elif mine_or_other2 == 3:
                            hand = self.hands[hand_id]["commonhand"]
                        for j in range(len(hand)):
                            if self.check_monster_condition_det(monster_condition,hand[j],user,"",0,"hand",deck_id,0,0,mine_or_other3) == True:
                                if hand[j]["id"] not in variety:
                                    variety.append(hand[j]["id"])
                                count+=1
                                if counter != -1:
                                    variable = hand[j]["variables"][counter]
                                    tmp_varieties = variable["value"].split("_")
                                    for tmp_variety in tmp_varieties:
                                        if(tmp_variety not in variable_variety):
                                            variable_variety.append(tmp_variety)
                                    variable_counter += int(variable["value"])
            min_equation_number = monster_condition["min_equation_number"]
            max_equation_number = monster_condition["max_equation_number"]
            if(equation_kind == "number"):
                if(count >= self.calculate_boland(min_equation_number,monster) and count<= self.calculate_boland(max_equation_number,monster)):
                    if and_or_all == "or":
                        flag =  True
                    elif flag == True:
                        flag =  True
                else:
                    if and_or_all == "and":
                        flag =  False
                    elif flag == False:
                        flag =  False


            elif(equation_kind == "kind"):
                if(len(variety) >= self.calculate_boland(min_equation_number,monster) and len(variety) <= self.calculate_boland(max_equation_number,monster)):
                    if and_or_all == "or":
                        flag =  True
                    elif flag == True:
                        flag =  True
                else:
                    if and_or_all == "and":
                        flag =  False
                    elif flag == False:
                        flag =  False
            elif counter == "x":
                if(x_counter >= self.calculate_boland(min_equation_number,monster) and x_counter <= self.calculate_boland(max_equation_number,monster)):
                    if and_or_all == "or":
                        flag =  True
                    elif flag == True:
                        flag =  True
                else:
                    if and_or_all == "and":
                        flag =  False
                    elif flag == False:
                        flag =  False
            elif counter == "y":
                if(y_counter >= self.calculate_boland(min_equation_number,monster) and y_counter <= self.calculate_boland(max_equation_number,monster)):
                    if and_or_all == "or":
                        flag =  True
                    elif flag == True:
                        flag =  True
                else:
                    if and_or_all == "and":
                        flag =  False
                    elif flag == False:
                        flag =  False
            #elif(equation_kind.find("num") != -1):
            #    if(variable_counter >= self.calculate_boland(min_equation_number,monster) and variable_counter <= self.calculate_boland(max_equation_number,monster)):
            #        if and_or_all == "or":
            #            flag =  True
            #        elif flag == True:
            #            flag =  True
            #    else:
            #        if and_or_all == "and":
            #            flag =  False
            #        elif flag == False:
            #            flag =  False
            else:
                if(len(variable_variety) >= self.calculate_boland(min_equation_number,monster) and len(variable_variety)<= self.calculate_boland(max_equation_number,monster)):
                    if and_or_all == "or":
                        flag =  True
                    elif flag == True:
                        flag =  True
                else:
                    if and_or_all == "and":
                        flag =  False
                    elif flag == False:
                        flag =  False
            if "and_or" in  monster_condition:
                and_or_all = monster_condition["and_or"]
            else:
                and_or_all = "and"

        return flag

    def check_eternal_effect_monster(self,eternal_effect,user,monster=0):
        if(eternal_effect.eternal_effect_monster == ""):
            return True
        eternal_effect_monster = json.loads(eternal_effect.eternal_effect_monster)
        eternal_effect_monster_condition = eternal_effect_monster[0]
        place = eternal_effect_monster[0]["place"]
        if "flag" in eternal_effect_monster:
            flag = eternal_effect_monster["flag"]
        else:
            flag = None
        if(self.check_eternal_effect_monster_det(place,flag,eternal_effect_monster_condition,monster,user) == False):
            return False
        return True
    def check_trigger_monster(self,trigger,user,monster=0):
        if(trigger.trigger_monster == ""):
            return True
        if(self.check_trigger_monster_det(trigger.trigger_monster,monster,user) == False):
            return False
        return True
    def check_eternal_effect_monster_det(self,places,flag_det,eternal_effect_monster_condition,monster,user):
        if user == 1:
            user = 1
            other_user = 2
        else:
            user = 2
            other_user = 1

        monster_place = monster["place"]
        flag = False
        for place_tmp in places:
            place_tmp = place_tmp.split("_")
            place = place_tmp[0]
            if place == monster_place:
                if str(monster["deck_id"]).find(place_tmp[1]) == -1:
                    continue
                if place_tmp[2] == '1'  and user == self.user or place_tmp[2] =='2' and user != self.user:
                    if int(monster["mine_or_other"]) != 1:
                        continue
                else:
                    if int(monster["mine_or_other"]) != 2:
                        continue
                flag = True
                break
        if flag == False:
            return False
        if self.check_monster_condition_det(eternal_effect_monster_condition["monster_monster"],monster["det"],user,"",0,monster["place"],monster["deck_id"],monster["x"],monster["y"],monster["mine_or_other"]):
            return True
        else:
            return False
    def check_trigger_monster_det(self,trigger_monster_condition,monster,user):
        monster_place = monster["place"]
        tmps2 = json.loads(trigger_monster_condition)
        tmps2 = tmps2["monster"]
        flag = True
        for tmps in tmps2:
            current_and_or = "and"
            places = tmps["monster"]["place"]
            for place_tmp in places:
                place = place_tmp["det"]
                and_or = place_tmp["and_or"]
                place_tmp = place.split("_")
                flag2 = True
                if place_tmp[0] == monster_place:
                    if monster_place == "field":
                        pass
                    if str(monster["deck_id"]).find(place_tmp[1]) == -1:
                        flag2 = False
                else:
                    flag2 = False
                if ( place_tmp[2] == '1' and user == 1 or place_tmp[2]=='2' and user ==2):
                    if int(monster["mine_or_other"]) !=1:
                        flag2 = False
                elif ( place_tmp[2] == '2' and user == 1 or place_tmp[2]=='1' and user ==2):
                    if int(monster["mine_or_other"]) != 2:
                        flag2 = False

                if flag2 == True:
                    if current_and_or == "or":
                        flag = True
                else:
                    if current_and_or == "and":
                        flag = False
                current_and_or = and_or

            if(flag == False):
                return False
            if self.check_monster_condition_det(tmps,monster["det"],user,"",0,monster["place"],monster["deck_id"],monster["x"],monster["y"],monster["mine_or_other"]):
                return True
        return False
    def check_trigger_condition(self,trigger,user,monster=0):
        duel = self.duel
        room_number = self.room_number
        if(trigger.turn != 0):
            if(duel.user_turn == 1 and user==1 or duel.user_turn == 2 and user == 2):
                if(trigger.turn != 1):
                    return False
            elif(duel.user_turn == 2 and user==1 or duel.user_turn == 1 and user == 2):
                if(trigger.turn != 2):
                    return False
        if(trigger.trigger_condition == ""):
            return True
        trigger_condition = json.loads(trigger.trigger_condition)
        if "monster" in trigger_condition:
            if(self.check_monster_condition(trigger_condition["monster"],user,False,monster) == False):
                return False
        if "variable" in trigger_condition:
            variable_conditions = trigger_condition["variable"]
            for i in range(len(variable_conditions)):
                variable_condition = variable_conditions[i]
                variable = variable_condition["variable"].split("_")
                mine_or_other = int(variable[1])
                variable_name = variable[0]
                variable = json.loads(duel.global_variable)
                if mine_or_other == 0:
                    if(variable_condition["variable_equation"] == "="):
                        if not variable[variable_name]["value"]==self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == "<="):
                        if not variable[variable_name]["value"]<=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == ">="):
                        if not variable[variable_name]["value"]>=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == "!="):
                        if not variable[variable_name]["value"]!=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                if mine_or_other == 1 and user == 1 or mine_or_other == 2 and user == 2:
                    if(variable_condition["variable_equation"] == "="):
                        if not variable[variable_name]["1_value"]==self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == "<="):
                        if not variable[variable_name]["1_value"]<=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == ">="):
                        if not variable[variable_name]["1_value"]>=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == "!="):
                        if not variable[variable_name]["1_value"]!=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                if mine_or_other == 2 and user == 1 or mine_or_other == 1 and user == 2:
                    if(variable_condition["variable_equation"] == "="):
                        if not variable[variable_name]["2_value"]==self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == "<="):
                        if not variable[variable_name]["2_value"]<=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == ">="):
                        if not variable[variable_name]["2_value"]>=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False
                    elif(variable_condition["variable_equation"] == "!="):
                        if not variable[variable_name]["2_value"]!=self.calculate_boland(variable_condition["variable_val"],monster):
                            return False


        return True

    def end_cost(self,user):
        self.end_cost_remove(user)
        self.end_cost_add(user)
        self.end_cost_variable(user)
        self.end_cost_clear(user)
        self.end_cost_shuffle(user)
        self.cost_result = {}
        self.duel.in_pac_cost = "[]"
        self.duel.in_cost = False
        self.duel.log_turn += self.duel.cost_log
        self.duel.log += self.duel.cost_log
        self.duel.cost_log = ""

    def end_cost_add(self,cost_user):
        duel = self.duel
        room_number = self.room_number
        if(self.cost_result == ''):
            return
        cost = self.cost_result
        if "add" in cost:
            if "field" in cost["add"]:
                user = tmp["user"]
                for tmp in cost["add"]["field"]:
                    x = tmp["x"]
                    y = tmp["y"]
                    effect_kind = tmp["kind"]
                    move_to = json.loads(tmp["det"])
                    if(tmp["det"]["place_id"] == check_cost[str(duel.chain)]["trigger"]["place_id"]):
                        check_cost = self.cost
                        check_mess = self.mess
                        tmp2 = {}
                        tmp2["x"] = x
                        tmp2["y"] = y
                        tmp2["det"] = tmp["det"]
                        tmp2["det"]["place_id"] = move_to_tmp["place_id"]
                        tmp2["place_id"] = tmp["det"]["place_unique_id"]
                        tmp2["card_unique_id"] = tmp["det"]["card_unique_id"]
                        tmp2["mine_or_other"] =check_cost["trigger"]["mine_or_other"]
                        tmp2["user"] = check_cost["trigger"]["user"]
                        tmp2["place"] = "field"
                        tmp2["deck_id"] = 0
                        check_cost[str(duel.chain)]["trigger"] = []
                        check_cost[str(duel.chain)]["trigger"].append = tmp2
                        check_mess[str(duel.chain)]["trigger"] = []
                        check_mess[str(duel.chain)]["trigger"].append = tmp2
                        self.cost = check_cost
                        self.mess = check_mess
                    move_to_tmp = move_to.copy()
                    field[x][y]["det"]= self.copy_monster_to_field(move_to,x,y,field[x][y]["mine_or_other"])
                    user_det = field[x][y]["user_det"]
                    self.raise_trigger(field[x][y]["det"]["place_unique_id"],move_to_tmp,"cost","field",user,field[x][y]["mine_or_other"],None,effect_kind,x,y)
                self.field = field
            if "deck" in cost["add"]:
                for tmp in cost["add"]["deck"]:

                    effect_kind = tmp["kind"]
                    deck_id = tmp["deck_id"]
                    user = tmp["user"]
                    user_det = tmp["user_det"]
                    how = int(tmp["how"])
                    move_to = json.loads(tmp["det"])
                    if(tmp["det"]["place_id"] == check_cost[str(duel.chain)]["trigger"]["place_id"]):
                        check_cost = self.cost
                        check_mess = self.mess
                        tmp2 = {}
                        tmp2["x"] = 0
                        tmp2["y"] = 0
                        tmp2["det"] = tmp["det"]
                        tmp2["det"]["place_id"] = move_to_tmp["place_id"]
                        tmp2["place_id"] = tmp["det"]["place_unique_id"]
                        tmp2["card_unique_id"] = tmp["det"]["card_unique_id"]
                        tmp2["mine_or_other"] =user
                        tmp2["user"] = check_cost["trigger"]["user"]
                        tmp2["place"] = "deck"
                        tmp2["deck_id"] = deck_id
                        check_cost[str(duel.chain)]["trigger"] = []
                        check_cost[str(duel.chain)]["trigger"].append = tmp2
                        check_mess[str(duel.chain)]["trigger"] = []
                        check_mess[str(duel.chain)]["trigger"].append = tmp2
                        self.cost = check_cost
                        self.mess = check_mess
                    move_to_tmp = move_to.copy()
                    move_to = self.copy_monster_to_deck(move_to,deck_id,user)
                    self.raise_trigger(move_to,move_to_tmp,"cost","deck",user,user_det,deck_id,effect_kind,None,None)
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_decks = self.decks[deck_id]["mydeck"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_decks = self.decks[deck_id]["otherdeck"]
                    elif user == 3:
                        user_decks = self.decks[deck_id]["commondeck"]
                    if(how == 0):
                        user_decks.insert(0,move_to)
                    elif(how  == 1):
                        user_decks.append(move_to)
                    else:
                        range_i =random.randrange(len(user_decks))
                        user_decks.insert(range_i,move_to)
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.decks[deck_id]["mydeck"] = user_decks
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.decks[deck_id]["otherdeck"] = user_decks
                    elif user == 3:
                        self.decks[deck_id]["commondeck"] = user_decks
            if "grave" in cost["add"]:
                for tmp in cost["add"]["grave"]:

                    effect_kind = tmp["kind"]
                    grave_id = tmp["grave_id"]
                    user = tmp["user"]
                    user_det = tmp["user_det"]
                    move_to = json.loads(tmp["det"])
                    how = int(tmp["how"])
                    move_to = json.loads(tmp["det"])

                    if(tmp["det"]["place_id"] == check_cost[str(duel.chain)]["trigger"]["place_id"]):
                        check_cost = self.cost
                        check_mess = self.mess
                        tmp2 = {}
                        tmp2["x"] = 0
                        tmp2["y"] = 0
                        tmp2["det"] = tmp["det"]
                        tmp2["det"]["place_id"] = move_to_tmp["place_id"]
                        tmp2["place_id"] = tmp["det"]["place_unique_id"]
                        tmp2["card_unique_id"] = tmp["det"]["card_unique_id"]
                        tmp2["mine_or_other"] =user
                        tmp2["user"] = check_cost["trigger"]["user"]
                        tmp2["place"] = "grave"
                        tmp2["deck_id"] = grave_id
                        check_cost[str(duel.chain)]["trigger"] = []
                        check_cost[str(duel.chain)]["trigger"].append = tmp2
                        check_mess[str(duel.chain)]["trigger"] = []
                        check_mess[str(duel.chain)]["trigger"].append = tmp2
                        self.cost = check_cost
                        self.mess = check_mess
                    move_to_tmp = move_to.copy()
                    move_to = self.copy_monster_to_grave(move_to,grave_id,user)
                    self.raise_trigger(move_to,move_to_tmp,"cost","grave",user,user_det,grave_id,effect_kind,None,None)
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_graves = self.graves[grave_id]["mygrave"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_graves = self.graves[grave_id]["othergrave"]
                    elif user == 3:
                        user_graves = self.graves[grave_id]["commongrave"]
                    if(how == 0):
                        user_graves.insert(0,move_to)
                    elif(how  == 1):
                        user_graves.append(move_to)
                    else:
                        range_i =random.randrange(len(user_graves))
                        user_graves.insert(range_i,move_to)
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.graves[grave_id]["mygrave"] = user_graves
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.graves[grave_id]["othergrave"] = user_graves
                    elif user == 3:
                        self.graves[grave_id]["commongrave"] = user_graves
            if "hand" in cost["add"]:
                for tmp in cost["add"]["hand"]:

                    hand_id = tmp["hand_id"]
                    user = tmp["user"]
                    user_det = tmp["user_det"]
                    move_to = json.loads(tmp["det"])
                    how = int(tmp["how"])
                    move_to = json.loads(tmp["det"])
                    if(tmp["det"]["place_id"] == check_cost[str(duel.chain)]["trigger"]["place_id"]):
                        check_cost = self.cost
                        check_mess = self.mess
                        tmp2 = {}
                        tmp2["x"] = 0
                        tmp2["y"] = 0
                        tmp2["det"] = tmp["det"]
                        tmp2["det"]["place_id"] = move_to_tmp["place_id"]
                        tmp2["place_id"] = tmp["det"]["place_unique_id"]
                        tmp2["card_unique_id"] = tmp["det"]["card_unique_id"]
                        tmp2["mine_or_other"] = user
                        tmp2["user"] = check_cost["trigger"]["user"]
                        tmp2["place"] = "hand"
                        tmp2["deck_id"] = hand_id
                        check_cost[str(duel.chain)]["trigger"] = []
                        check_cost[str(duel.chain)]["trigger"].append = tmp2
                        check_mess[str(duel.chain)]["trigger"] = []
                        check_mess[str(duel.chain)]["trigger"].append = tmp2
                        self.cost = check_cost
                        self.mess = check_mess
                    move_to_tmp = move_to.copy()
                    move_to = self.copy_monster_to_hand(move_to,hand_id,user)
                    self.raise_trigger(move_to,move_to_tmp,"cost","hand",user,user_det,hand_id,effect_kind,None,None)
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_hands = self.hands[hand_id]["myhand"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_hands = self.hands[hand_id]["otherhand"]
                    elif user == 3:
                        user_hands = self.hands[hand_id]["commonhand"]
                    if(how == 0):
                        user_hands.insert(0,move_to)
                    elif(how  == 1):
                        user_hands.append(move_to)
                    else:
                        range_i =random.randrange(len(user_hands))
                        user_hands.insert(range_i,move_to)
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.hands[hand_id]["myhand"] = user_hands
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.hands[hand_id]["otherhand"] = user_hands
                    elif user == 3:
                        self.hands[hand_id]["commonhand"] = user_hands
    def get_val_designated(self,val,other_user_flag=False):
        duel = self.duel
        val = val[1:-1]
        val = val.split(":")
        x = int(val[0])
        y = int(val[1])
        val_name = val[2]
        field = self.field
        field = field[x][y]["det"]["variables"]
        return_value = int(field[val_name]["value"])
        if "add" in field[val_name] :
            return_value += int(field[val_name]["add"])
        return return_value
    def floor(self,src, num):
        range = pow(10,num)
        return (int)(src / range) * range
    def get_val_floor(self,val,pre,other_user_flag = False):
        val = val[1:-1]
        val= self.floor(pre,int(val))
        return val

    def get_val_sum(self,val,other_user_flag = False):
        duel = self.duel
        room_number = self.room_number
        val = val[1:-1]
        val = val.split(":")
        place= val[0]
        deck_id= int(val[1])
        mine_or_other= int(val[2])
        if other_user_flag == True:
            if mine_or_other == 1:
                mine_or_other = 2
            elif mine_or_other == 2:
                mine_or_other = 1
        return_value =  0
        if duel.in_cost == 1 :
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain)]
        elif duel.chain==0 or duel.ask>0:
            user = self.user
        else:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain-1)]
        val_name = val[3]
        if place == "deck":
            if mine_or_other == 1 and user == self.user or mine_or_other == 2 and user != self.user:
                cards = self.decks[deck_id]["mydeck"]
            elif mine_or_other == 2 and user == self.user or mine_or_other == 1 and user != self.user:
                cards = self.decks[deck_id]["otherdeck"]
            elif mine_or_other == 3:
                cards = self.decks[deck_id]["commondeck"]
        if place == "grave":
            if mine_or_other == 1 and user == self.user or mine_or_other == 2 and user != self.user:
                cards = self.graves[deck_id]["mygrave"]
            elif mine_or_other == 2 and user == self.user or mine_or_other == 1 and user != self.user:
                cards = self.graves[deck_id]["othergrave"]
            elif mine_or_other == 3:
                cards = self.graves[deck_id]["commongrave"]
        if place == "hand":
            if mine_or_other == 1 and user == self.user or mine_or_other == 2 and user != self.user:
                cards = self.hands[deck_id]["myhand"]
            elif mine_or_other == 2 and user == self.user or mine_or_other == 1 and user != self.user:
                cards = self.hands[deck_id]["otherhand"]
            elif mine_or_other == 3:
                cards = self.hands[deck_id]["commonhand"]
        for card in cards:
            tmp2 = card["variables"]
            return_value += int(tmp2[val_name]["value"])
            if "add" in tmp2[val_name] :
                return_value += int(tmp2[val_name]["add"])
        return return_value
    def get_val_sum_field(self,val,other_user_flag = False):
        duel = self.duel
        val = val[1:-1]
        val = val.split(":")
        place= int(val[0])
        mine_or_other= int(val[1])
        if other_user_flag == True:
            if mine_or_other == 1:
                mine_or_other = 2
            elif mine_or_other == 2:
                mine_or_other = 1
        return_value =  0
        if duel.in_cost == 1 :
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain)]
        elif duel.chain==0 or duel.ask>0:
            user = self.user
        else:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain-1)]
        if(mine_or_other !=3):
            if user == 1 and mine_or_other == 1 or user == 2 and mine_or_other == 2:
                mine_or_other = 1
            else:
                mine_or_other = 2
        val_name = val[2]
        field = self.field
        field_size = FieldSize.objects.get(id=1);
        tmp3 = 0
        for x in range(field_size.field_x):
            for y in range(field_size.field_y):
                if field[x][y]["mine_or_other"] == mine_or_other and int(field[x][y]["kind"]) == place:
                    if field[x][y]["det"] is not None:
                        tmp2 = field[x][y]["det"]["variables"]
                        tmp3 +=int(tmp2[val_name]["value"])
                        if "add" in tmp2[val_name] :
                            return_value += int(tmp2[val_name]["add"])
        return tmp3
    def get_val_trigger(self,val,monster,other_user_flag = False):
        duel = self.duel
        val = val[1:-1]
        val = val.split(":")
        name = val[0]
        val_name = val[1]
        return_value = 0
        tmp2 = monster["det"]["variables"]
        return_value += int(tmp2[val_name]["value"])
        if "add" in tmp2[val_name] :
            return_value += int(tmp2[val_name]["add"])
        return return_value
    def get_place_unique_id(self,val,mode=0):
        if(val[0] == "~"):
            return self.get_place_unique_id_cost(val,mode)
        elif(val[0] == "%"):
            return self.get_place_unique_id_timing_mess(val,mode)
        else:
            return self.get_place_unique_id_effect(val,mode)
    def get_name(self,val,mode=0):
        if(val[0] != "{"):
            return val
        if(val[1] == "~"):
            return self.get_name_cost(val,mode)
        elif(val[1] == "%"):
            return self.get_name_timing_mess(val,mode)
        else:
            return self.get_name_effect(val,mode)
    def get_name_monster_all(self,monsters):
        return_value = ""
        for monster in monsters:
            return_value+=monster["det"]["monster_name"]+" "
        return return_value
            
    def get_name_all(self,val,mode=0):
        if(val[0] != "{"):
            return val
        if(val[1] == "~"):
            return self.get_name_cost_all(val,mode)
        elif(val[1] == "%"):
            return self.get_name_timing_mess_all(val,mode)
        else:
            return self.get_name_effect_all(val,mode)
    def get_place_unique_id_cost(self,val,mode):
        duel = self.duel
        val = val[1:]
        tmp = self.cost
        tmp = tmp[str(duel.chain)][val]
        tmp = tmp[0]
        return tmp["det"]["place_unique_id"]
    def get_place_unique_id_timing_mess(self,val,mode):
        duel = self.duel
        val = val[1:]
        tmp = self.timing_mess
        tmp = tmp[val]
        tmp = tmp[0]
        return tmp["det"]["place_unique_id"]
    def get_place_unique_id_effect(self,val,mode):
        duel = self.duel
        tmp = self.mess
        tmp = tmp[str(duel.chain-1)][val]
        tmp = tmp[0]
        return tmp["det"]["place_unique_id"]
    def get_card_unique_id_cost(self,val,mode):
        duel = self.duel
        val = val[1:]
        tmp = self.cost
        tmp = tmp[str(duel.chain)][val]
        tmp = tmp[0]
        return tmp["det"]["card_unique_id"]
    def get_card_unique_id_timing_mess(self,val,mode):
        duel = self.duel
        val = val[1:]
        tmp = self.timing_mess
        tmp = tmp[val]
        tmp = tmp[0]
        return tmp["det"]["card_unique_id"]
    def get_card_unique_id_effect(self,val,mode):
        duel = self.duel
        tmp = self.mess
        tmp = tmp[str(duel.chain-1)][val]
        tmp = tmp[0]
        return tmp["det"]["card_unique_id"]
    def get_name_cost(self,val,mode):
        duel = self.duel
        val = val[2:-1]
        tmp = self.cost
        tmp = tmp[str(duel.chain)][val]
        tmp = tmp[0]
        if mode == 1 and tmp["det"]["variables"]["show"]["value"]=="1":
            config = Config.objects.get()
            hide_name = config.hide_name
            return hide_name
        return tmp["det"]["monster_name"]
    def get_name_cost_all(self,val,mode):
        duel = self.duel
        val = val[2:-1]
        tmp = self.cost
        tmps = tmp[str(duel.chain)][val]
        return_value = ""
        for tmp in tmps:
            if mode == 1 and tmp["det"]["variables"]["show"]["value"]=="1":
                config = Config.objects.get()
                hide_name = config.hide_name
                return_value += hide_name +" "
            else:
                return_value += tmp["det"]["monster_name"] + " "
        return return_value
    def get_name_timing_mess_all(self,val,mode):
        duel = self.duel
        val = val[2:-1]
        tmp = self.timing_mess
        tmps = tmp[val]
        return_value = ""
        for tmp in tmps:
            if mode == 1 and tmp["det"]["variables"]["show"]["value"]=="1":
                config = Config.objects.get()
                hide_name = config.hide_name
                return_value += hide_name +" "
        else:
            return_value += tmp["det"]["monster_name"] + " "

        return return_value
    def get_name_timing_mess(self,val,mode):
        duel = self.duel
        val = val[2:-1]
        tmp = self.timing_mess
        tmp = tmp[val]
        tmp = tmp[0]

        if mode == 1 and tmp["det"]["variables"]["show"]["value"]=="1":
            config = Config.objects.get()
            hide_name = config.hide_name
            return hide_name
        return tmp["det"]["monster_name"]
    def get_name_effect_all(self,val,mode):
        duel = self.duel
        val = val[1:-1]
        tmp = self.mess
        tmps = tmp[str(duel.chain-1)][val]
        return_value = ""
        for tmp in tmps:
            if mode == 1 and tmp["det"]["variables"]["show"]["value"]=="1":
                config = Config.objects.get()
                hide_name = config.hide_name
                return_value += hide_name +" "
        else:
            return_value += tmp["det"]["monster_name"] + " "

        return return_value
    def get_name_effect(self,val,mode):
        duel = self.duel
        val = val[1:-1]
        tmp = self.mess
        tmp = tmp[str(duel.chain-1)][val]
        tmp = tmp[0]
        if mode == 1 and tmp["det"]["variables"]["show"]["value"]=="1":
            config = Config.objects.get()
            hide_name = config.hide_name
            return hide_name

        return tmp["det"]["monster_name"]
    def get_val_timing(self,val,other_user_flag = False):
        val = val[1:-1]
        val = val.split(":")
        name = val[0]
        val_name = val[1]
        duel = self.duel
        tmp = self.timing_mess
        tmp = tmp[name]
        return_value = 0
        for monster in tmp:
            tmp2 = monster["det"]["variables"]
            return_value += int(tmp2[val_name]["value"])
            if "add" in tmp2[val_name] :
                return_value += int(tmp2[val_name]["add"])
        return return_value
    def get_val(self,val,other_user_flag = False):
        val = val[1:-1]
        val = val.split(":")
        name = val[0]
        val_name = val[1]
        duel = self.duel
        tmp = self.mess
        tmp = tmp[str(duel.chain-1)][name]
        return_value = 0
        for monster in tmp:
            tmp2 = monster["det"]["variables"]
            return_value += int(tmp2[val_name]["value"])
            if "add" in tmp2[val_name] :
                return_value += int(tmp2[val_name]["add"])
        return return_value
    def get_val_cost(self,val,other_user_flag = False):
        return_value = 0
        val = val[1:-1]
        val = val.split(":")
        name = val[0]
        name = name[1:]
        val_name = val[1]
        duel = self.duel
        tmp = self.cost
        tmp = tmp[str(duel.chain)][name]
        for monster in tmp:
            tmp2 = monster["det"]["variables"]
            return_value += int(tmp2[val_name]["value"])
            if "add" in tmp2[val_name] :
                return_value += int(tmp2[val_name]["add"])
        return return_value
    def get_val_global(self,val,other_user_flag = False):
        duel = self.duel
        if duel.in_cost == True:
            user = duel.cost_user
        elif duel.chain==0 or duel.ask>0:
            user = self.user
        else:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain-1)]
        val = val[1:-1]
        val = val.split(":")
        variable_name=val[0]
        mine_or_other=int(val[1])
        variable = json.loads(duel.global_variable)
        if mine_or_other == 0:
            if variable_name in variable:
                return  int(variable[variable_name]["value"])
            else:
                return  int(self.virtual_variables[variable_name]["value"])
        if (mine_or_other == 1 and user == 1) or (mine_or_other == 2 and user == 2):
            if variable_name in variable:
                return  int(variable[variable_name]["1_value"])
            else:
                return  int(self.virtual_variables[variable_name]["1_value"])
        if (mine_or_other == 2 and user == 1) or (mine_or_other == 1 and user == 2):
            if variable_name in variable:
                return  int(variable[variable_name]["2_value"])
            else:
                return  int(self.virtual_variables[variable_name]["2_value"])
    def calculate_boland(self,boland,monster=None,other_user_flag = False):
        if boland == "":
            return 0
        operator = { '+': (lambda x, y: x + y), '-': (lambda x, y: x - y), '*': (lambda x, y: x * y), '/': (lambda x, y: float(x) / y) }
        stack = []
        boland = str(boland)
        states = boland.split('$')
        for index, z  in enumerate(states):
            if z not in operator.keys():
                if(z[0] == "{"):
                    if(z[1] != "~"):
                        if monster is None or monster == 0:
                            z = self.get_val(z,other_user_flag)
                        else:
                            z = self.get_val_trigger(z,monster,other_user_flag)
                    else:
                        z = self.get_val_cost(z,other_user_flag)
                elif(z[0] == "["):
                    z = self.get_val_designated(z,other_user_flag)
                elif(z[0] == "&"):
                    z = self.get_val_sum(z,other_user_flag)
                elif(z[0] == "|"):
                    z = self.get_val_sum_field(z,other_user_flag)
                elif(z[0] == "="):
                    t = stack.pop()
                    z = self.get_val_floor(z,t,other_user_flag)
                elif(z[0] == "^"):
                    z = self.get_val_global(z,other_user_flag)
                elif(z[0] == "%"):
                    z = self.get_val_timing(z,other_user_flag)
                else:
                    z = int(z)
                stack.append(z)
                continue
            y = stack.pop()
            x = stack.pop()
            stack.append(operator[z](x, y))
        return int(stack[0])

    def end_cost_variable(self,cost_user):
        duel = self.duel
        room_number = self.room_number
        if( not self.cost_result):
            return
        cost = self.cost_result
        if "variable" in cost:
            if "field" in cost["variable"]:
                field = self.field
                for tmp in cost["variable"]["field"]:
                    x = tmp["x"]
                    y = tmp["y"]
                    place_id = tmp["place_id"]
                    if(field[x][y]["det"]["place_unique_id"] != place_id):
                        return "error"
                    else:
                        variable_name = tmp["change_variable"]
                        if tmp["change_variable_how"] == 0:
                            field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(tmp["change_variable_val"]) + int( field[x][y]["det"]["variables"][variable_name]["value"] ))
                        elif tmp["change_variable_how"] == 1:
                            field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(tmp["change_variable_val"]) - int( field[x][y]["det"]["variables"][index]["value"] ))
                        elif tmp["change_variable_how"] == 2:
                            field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(tmp["change_variable_val"]))

                self.field = field

            if "deck" in cost["variable"]:
                for tmp in cost["variable"]["deck"]:
                    deck_id = tmp["deck_id"]
                    user = tmp["user"]
                    place_id = tmp["place_id"]
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_decks = self.decks[deck_id]["mydeck"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_decks = self.decks[deck_id]["otherdeck"]
                    elif user == 3:
                        user_decks = self.decks[deck_id]["commondeck"]
                    for key in range(len(user_decks)):
                        user_deck = user_decks[key]
                        if place_id== user_deck["place_unique_id"]:
                            if user_deck[tmp["change_variable"]] is None:
                                tmp2 = {}
                                tmp2["id"] = len(user_deck["variables"])
                                tmp2["name"] = tmp["change_variable"]
                                tmp2["str"] = 0
                                tmp2["value"] = 0
                            else:
                                tmp2 = user_deck[tmp["change_variable"]]

                            if tmp["change_variable_how"] == 0:

                                tmp2["value"] += self.calculate_boland(tmp["variable_change_val"])
                            elif tmp["change_variable_how"] == 1:
                                tmp2["value"] -= self.calculate_boland(tmp["variable_change_val"])
                            elif tmp["change_variable_how"] == 2:
                                tmp2["value"] = self.calculate_boland(tmp["variable_change_val"])
                            user_deck["variables"][tmp["change_variable"]] = tmp2
                        user_decks[key] = user_deck
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.decks[deck_id]["mydeck"]=user_decks
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.decks[deck_id]["otherdeck"]=user_decks
                    elif user == 3:
                        self.decks[deck_id]["commondeck"]=user_decks

            if "grave" in cost["variable"]:
                for tmp in cost["variable"]["grave"]:
                    grave_id = tmp["grave_id"]
                    user = tmp["user"]
                    place_id = tmp["place_id"]
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_graves = self.graves[grave_id]["mygrave"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_graves = self.graves[grave_id]["othergrave"]
                    elif user == 3:
                        user_graves = self.graves[grave_id]["commongrave"]
                    for key in range(len(user_graves)):
                        user_grave = user_graves[key]
                        if place_id== user_grave["place_unique_id"]:
                            if user_grave[tmp["change_variable"]] is None:
                                tmp2 = {}
                                tmp2["id"] = len(user_grave["variables"])
                                tmp2["name"] = tmp["change_variable"]
                                tmp2["str"] = 0
                                tmp2["value"] = 0
                            else:
                                tmp2 = user_grave[tmp["change_variable"]]

                            if tmp["change_variable_how"] == 0:

                                tmp2["value"] += self.calculate_boland(tmp["variable_change_val"])
                            elif tmp["change_variable_how"] == 1:
                                tmp2["value"] -= self.calculate_boland(tmp["variable_change_val"])
                            elif tmp["change_variable_how"] == 2:
                                tmp2["value"] = self.calculate_boland(tmp["variable_change_val"])
                            user_grave["variables"][tmp["change_variable"]] = tmp2
                        user_graves[key] = user_grave
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.graves[grave_id]["mygrave"]=user_graves
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.graves[grave_id]["othergrave"]=user_graves
                    elif user == 3:
                        self.graves[grave_id]["commongrave"]=user_graves
            if "hand" in cost["variable"]:
                for tmp in cost["variable"]["hand"]:
                    hand_id = tmp["hand_id"]
                    user = tmp["user"]
                    place_id = tmp["place_id"]
                    if user == 1:
                        user_hands = self.hands[hand_id]["myhand"]
                    elif user == 2:
                        user_hands = self.hands[hand_id]["otherhand"]
                    elif user == 3:
                        user_hands = self.hands[hand_id]["commonhand"]
                    for key in range(len(user_hands)):
                        user_hand = user_hands[key]
                        if place_id== user_hand["place_unique_id"]:
                            if user_hand[tmp["change_variable"]] is None:
                                tmp2 = {}
                                tmp2["id"] = len(user_hand["variables"])
                                tmp2["name"] = tmp["change_variable"]
                                tmp2["str"] = 0
                                tmp2["value"] = 0
                            else:
                                tmp2 = user_hand[tmp["change_variable"]]

                            if tmp["change_variable_how"] == 0:

                                tmp2["value"] += self.calculate_boland(tmp["variable_change_val"])
                            elif tmp["change_variable_how"] == 1:
                                tmp2["value"] -= self.calculate_boland(tmp["variable_change_val"])
                            elif tmp["change_variable_how"] == 2:
                                tmp2["value"] = self.calculate_boland(tmp["variable_change_val"])
                            user_hand["variables"][tmp["change_variable"]] = tmp2
                        user_hands[key] = user_hand
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.hands[hand_id]["myhand"]=user_hands
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.hands[hand_id]["otherhand"]=user_hands
                    elif user == 3:
                        self.hands[hand_id]["commonhand"]=user_hands

    def end_cost_remove(self,cost_user):
        duel = self.duel
        room_number = self.room_number
        if(not self.cost_result ):
            return
        cost = self.cost_result
        if "remove" in cost:
            if "field" in cost["remove"]:
                field = self.field
                for tmp in cost["remove"]["field"]:
                    x = tmp["x"]
                    y = tmp["y"]
                    place_id = tmp["place_id"]
                    if(field[x][y]["det"]["place_unique_id"] != place_id):
                        return "error"
                    else:
                        field[x][y]["det"] = None
                self.field = field

            if "deck" in cost["remove"]:
                for tmp in cost["remove"]["deck"]:
                    deck_id = tmp["remove"]["deck_id"]
                    user = tmp["remove"]["user"]
                    place_id = tmp["remove"]["place_id"]
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_decks = self.decks[deck_id]["mydeck"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_decks = self.decks[deck_id]["otherdeck"]
                    elif user == 3:
                        user_decks = self.decks[deck_id]["commondeck"]
                    for user_deck in user_decks:
                        if place_id== user_deck["place_unique_id"]:
                            user_decks.remove(user_deck);
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.decks[deck_id]["mydeck"] = user_decks
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.decks[deck_id]["otherdeck"] = user_decks
                    elif user == 3:
                        self.decks[deck_id]["commondeck"] = user_decks

            if "grave" in cost["remove"]:
                for tmp in cost["remove"]["grave"]:
                    grave_id = tmp["grave_id"]
                    user = tmp["user"]
                    place_id = tmp["place_id"]
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_graves = self.graves[grave_id]["mygrave"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_graves = self.graves[grave_id]["othergrave"]
                    elif user == 3:
                        user_graves = self.graves[grave_id]["commongrave"]
                    for user_grave in user_graves:
                        if place_id== user_grave["place_unique_id"]:
                            user_graves.remove(user_grave);
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.graves[grave_id]["mygrave"] = user_graves
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.graves[grave_id]["othergrave"] = user_graves
                    elif user == 3:
                        self.graves[grave_id]["commongrave"] = user_graves
            if "hand" in cost["remove"]:
                for tmp in cost["remove"]["hand"]:
                    hand_id = tmp["hand_id"]
                    user = tmp["user"]
                    place_id = tmp["place_id"]
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        user_hands = self.hands[hand_id]["myhand"]
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        user_hands = self.hands[hand_id]["otherhand"]
                    elif user == 3:
                        user_hands = self.hands[hand_id]["commonhand"]
                    for user_hand in user_hands:
                        if place_id== user_hand["place_unique_id"]:
                            user_hands.remove(user_hand);
                    if user == 1 and cost_user == self.user or user ==2 and cost_user != self.user:
                        self.hands[hand_id]["myhand"] = user_hands
                    elif user == 2 and cost_user == self.user or user ==1 and cost_user != self.user:
                        self.hands[hand_id]["otherhand"] = user_hands
                    elif user == 3:
                        self.hands[hand_id]["commonhand"] = user_hands

    def pay_cost(self,cost,user):
        self.in_execute = True
        if cost is None:
            self.duel.chain+=1
            return True
        cost_unwrap = cost.cost
        if(cost_unwrap.cost_val == 5):
            self.duel.ask = 3
        elif(cost_unwrap.cost_val == 3):
            self.duel.ask = 1
        elif(cost_unwrap.cost_val == 4):
            self.duel.ask = 2
        self.duel.in_cost = True
        self.cost_det = cost.id
        self.duel.cost_user = user
        cost_next = self.invoke_cost(cost)
        while cost_next and cost_next != -2:

            if cost_next == -1:
                return False
            else:
                cost_det = cost_next.id
                self.cost_det = cost_det
                cost = cost_next
                cost_unwrap = cost.cost
                if(cost_unwrap.cost_val == 5):
                    self.duel.ask = 3
                elif(cost_unwrap.cost_val == 3):
                    self.duel.ask = 1
                elif(cost_unwrap.cost_val == 4):
                    self.duel.ask = 2
                cost_next = self.invoke_cost(cost)
        self.end_cost(user)
        self.duel.chain+=1
        return True
    def invoke_trigger(self,trigger,place,trigger_monster,mine_or_other,user,deck_id,x=0,y=0,monster_from=None,place_from =None,deck_id_from=None,from_x=None,from_y = None):
        duel = self.duel
        room_number = self.room_number
        org_chain = duel.chain
        if(place != ""):
            tmp = self.mess
            tmp2 = {}
            tmp2["x"] = x
            tmp2["y"] = y
            tmp2["from_x"] = from_x
            tmp2["from_y"] = from_y
            tmp2["deck_id_from"] = deck_id_from
            tmp2["place_from"] = place_from
            if monster_from is not None:
                tmp2["place_id_from"] = monster_from["place_id"]
            else:
                tmp2["place_id_from"] = None
            tmp2["det_from"] = monster_from
            tmp2["det"] = trigger_monster
            tmp2["place_id"] = trigger_monster["place_unique_id"]
            tmp2["card_unique_id"] = trigger_monster["card_unique_id"]
            tmp2["mine_or_other"] =mine_or_other
            tmp2["user"] = user
            tmp2["place"] = place
            tmp2["deck_id"] = deck_id
            tmp[str(duel.chain)] = {}
            tmp[str(duel.chain)]["trigger"] = []
            tmp[str(duel.chain)]["trigger"].append(tmp2)
            tmp[str(duel.chain)]["trigger_org"] = []
            tmp[str(duel.chain)]["trigger_org"].append(tmp2)
            self.mess= tmp
            tmp_cost = self.cost
            tmp_cost[str(duel.chain)] = {}
            tmp_cost[str(duel.chain)]["trigger"] = []
            tmp_cost[str(duel.chain)]["trigger"].append(tmp2)
            tmp_cost[str(duel.chain)]["trigger_org"] = []
            tmp_cost[str(duel.chain)]["trigger_org"].append(tmp2)
            self.cost= tmp_cost
        else:
            tmp = self.mess
            tmp[str(duel.chain)] = {}
            self.mess= tmp
            tmp_cost = self.cost
            tmp_cost[str(duel.chain)] = {}
            self.cost= tmp_cost

        flag = True
        if trigger.trigger_cost_pac is not None:
            cost= self.push_pac_cost(trigger.trigger_cost_pac)
        else:
            cost= trigger.trigger_cost
        if self.pay_cost(cost,user) == False:
            flag = False
        chain_det_json={}
        chain_user_json={}
        if(self.duel.chain_det != ""):
            chain_det_json = json.loads(self.duel.chain_det)
        if(self.duel.chain_user != ""):
            chain_user_json = json.loads(self.duel.chain_user)
        if trigger.pac :
            effect= self.push_pac(trigger.pac)
        else:
            effect = trigger.next_effect

        if(effect.monster_effect.monster_effect_val == 5):
            effect_kind = effect.monster_effect_kind
            self.duel.ask = 3
        elif(effect.monster_effect.monster_effect_val == 3):
            effect_kind = effect.monster_effect_kind
            self.duel.ask = 1

        elif(effect.monster_effect.monster_effect_val == 4):
            effect_kind = effect.monster_effect_kind
            self.duel.ask = 2
        else:
            effect_kind = effect.monster_effect_kind
            self.duel.ask = 0
        chain_det_json[str(org_chain)] = effect.id
        chain_user_json[str(org_chain)] = user
        self.duel.chain_det = json.dumps(chain_det_json)
        self.duel.chain_user = json.dumps(chain_user_json)
        return flag

    def check_trigger(self,decks,graves,hands,phase,turn,user,other_user):
        duel=self.duel
        room_number=self.room_number
        return_value = []
        available_trigger=[]
        triggers = Trigger.objects.filter(Q(phase__isnull=True) | Q(phase = phase))
        triggers = triggers.filter(Q(chain__isnull = True) | \
                                   (Q(chain_kind = 0) & Q(chain__lte=duel.chain)) | \
                                   (Q(chain_kind = 1) & Q(chain__gte=duel.chain)) | \
                                   (Q(chain_kind = 2) & Q(chain=duel.chain)))
        if duel.timing != None:
            triggers = triggers.filter(Q(timing=duel.timing))
        else:
            triggers = triggers.filter(Q(none_timing = True))

        triggers = triggers.filter(priority__lt= duel.current_priority)
        triggers = triggers.order_by('-priority').all();

        if(user == duel.user_turn):
            triggers = triggers.filter(Q(turn=0) | Q(turn = 1))
        else:
            triggers = triggers.filter(Q(turn=0) | Q(turn = 2))
        trigger_first = triggers.first()

        if(trigger_first is None):
            return_value.append(None)
            return_value.append(0)
            return return_value
        priority = trigger_first.priority
        none_triggers = triggers.filter(priority = priority,trigger_none_monster = True)
        for trigger in none_triggers:
            if self.check_trigger_condition(trigger,user):
                tmp={}
                if(trigger.force == True):
                    tmp["force"] = True
                else:
                    tmp["force"] = False
                tmp["sentence"] = trigger.trigger_sentence
                tmp["id"] = trigger.id
                available_trigger.append(tmp)
        trigger_num = self.check_monster_trigger(decks,graves,hands,user,other_user,priority)
        if(len(available_trigger)>1):
            return_value.append(available_trigger)
            return_value.append(priority)
        elif len(available_trigger) == 1 and trigger_num == False:
            if(available_trigger[0]["force"] == True):
                force_trigger = Trigger.objects.get(id=available_trigger[0]["id"])
                return_value.append(self.invoke_trigger(force_trigger,"","","",duel.user_turn,""))
                return_value.append(priority)
            else:
                return_value.append(available_trigger)
                return_value.append(priority)
        elif len(available_trigger) == 1 and trigger_num == True:
            return_value.append(available_trigger)
            return_value.append(priority)

        elif len(available_trigger) == 0 and trigger_num == False:
            return_value.append(None)
            return_value.append(priority)
        else:
            return_value.append("monster_trigger")
            return_value.append(priority)
        return return_value

    def check_monster_trigger(self,decks,graves,hands,user,other_user,priority):

        return_value = {}
        deck_info = self.get_deck_info(decks,user,other_user)
        return_value["deck_info"] = copy.deepcopy(deck_info)
        if self.modify_deck_info(return_value["deck_info"],decks.count(),user,other_user,priority,1):
            return True
        hand_info = self.get_hand_info(hands,user,other_user)
        return_value["hand_info"] = copy.deepcopy(hand_info)

        if self.modify_hand_info(return_value["hand_info"],hands.count(),user,other_user,priority,1):
            return True
        field = copy.deepcopy(self.field)
        if self.modify_field_info(field,user,other_user,priority,1):
            return True
        return False
    def init_all(self,user,other_user,room_number):
        self.init_deck_info(user,other_user,room_number)
        self.init_grave_info(user,other_user,room_number)
        self.init_hand_info(user,other_user,room_number)
        self.init_virtual_variable(user,other_user,room_number)
        duel = self.duel
        self.field = json.loads(duel.field)
        self.mess = json.loads(duel.mess)
        self.cost = json.loads(duel.cost)
        self.cost_det = duel.cost_det
        self.cost_result = json.loads(duel.cost_result)
        self.timing_mess = json.loads(duel.timing_mess)
        config = Config.objects.get()
        limit_time = config.limit_time
        time_win = config.time_win
        if user == duel.appoint or duel.ask==2 or duel.ask==3:
            if user == 1:
                if time() - duel.time_1 > limit_time:
                    duel.log_turn += self.write_log(time_win,other_user)
                    duel.log += self.write_log(time_win,other_user)
                    self.lose_the_game(2)
            else:
                if time() - duel.time_2 > limit_time:
                    duel.log_turn += self.write_log(time_win,other_user)
                    duel.log += self.write_log(time_win,other_user)
                    self.lose_the_game(2)
        else:
            if user == 1:
                if time() - duel.time_1 > limit_time:
                    duel.log_turn += self.write_log(time_win,user)
                    duel.log += self.write_log(time_win,user)
                    self.win_the_game(2)
            else:
                if time() - duel.time_2 > limit_time:
                    duel.log_turn += self.write_log(time_win,user)
                    duel.log += self.write_log(time_win,user)
                    self.win_the_game(2)

    def save_all(self,user,other_user,room_number):
        flag = Flag.objects.get(id=room_number)
        flag.flag = False
        flag.save()
        duel = self.duel
        config = Config.objects.get()
        game_name = config.game_name
        pwd = os.path.dirname(__file__)
        self.log = open(pwd+"/logger_"+game_name,mode='a',encoding='utf-8')
        self.log.write('-----------------------\n')
        self.save_deck_info(user,other_user,room_number)
        self.save_grave_info(user,other_user,room_number)
        self.save_hand_info(user,other_user,room_number)
        duel.mess = json.dumps(self.mess)
        duel.cost = json.dumps(self.cost)
        duel.cost_det = self.cost_det
        duel.cost_result = json.dumps(self.cost_result)
        duel.timing_mess = json.dumps(self.timing_mess)
        duel.field = json.dumps(self.field)
        reset_queries()
        duel.time_1 = time()
        duel.time_2 = time()
        duel.save()
        self.log_write()
        self.log.close()
    def log_write(self):
        for history in connection.queries:
            self.log.write(history["sql"]+';\n')
        reset_queries()
        return
    def save_deck_info(self,user,other_user,room_number):
        decks = self.deck_structure
        i=0
        for deck in decks:
            if(deck.mine_or_other == 1):
                tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = 3,deck_id = i+1).first()
                tmp.deck_content = json.dumps(self.decks[i+1]["commondeck"])
                reset_queries()
                tmp.save()
                self.log_write()
            else:
                tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = user,deck_id = i+1).first()
                tmp.deck_content = json.dumps(self.decks[i+1]["mydeck"])
                reset_queries()
                tmp.save()
                self.log_write()
                tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = other_user,deck_id = i+1).first()
                tmp.deck_content = json.dumps(self.decks[i+1]["otherdeck"])
                reset_queries()
                tmp.save()
                self.log_write()
            i+=1
    def save_grave_info(self,user,other_user,room_number):
        graves = self.grave_structure
        i=0
        for grave in graves:
            if(grave.mine_or_other == 1):
                tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = 3,grave_id = i+1).first()
                tmp.grave_content = json.dumps(self.graves[i+1]["commongrave"])
                reset_queries()
                tmp.save()
                self.log_write()
            else:
                tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = user,grave_id = i+1).first()
                tmp.grave_content = json.dumps(self.graves[i+1]["mygrave"])
                reset_queries()
                tmp.save()
                self.log_write()
                tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = other_user,grave_id = i+1).first()
                tmp.grave_content = json.dumps(self.graves[i+1]["othergrave"])
                reset_queries()
                tmp.save()
                self.log_write()
            i+=1
    def save_hand_info(self,user,other_user,room_number):
        hands = self.hand_structure
        i=0
        for hand in hands:
            if(hand.mine_or_other == 1):
                tmp = DuelHand.objects.filter(room_number = room_number,mine_or_other = 3,hand_id = i+1).first()
                tmp.hand_content = json.dumps(self.hands[i+1]["commonhand"])
                reset_queries()
                tmp.save()
                self.log_write()
            else:
                tmp = DuelHand.objects.filter(room_number = room_number,mine_or_other = user,hand_id = i+1).first()
                tmp.hand_content = json.dumps(self.hands[i+1]["myhand"])
                reset_queries()
                tmp.save()
                self.log_write()
                tmp = DuelHand.objects.filter(room_number = room_number,mine_or_other = other_user,hand_id = i+1).first()
                tmp.hand_content = json.dumps(self.hands[i+1]["otherhand"])
                reset_queries()
                tmp.save()
                self.log_write()
            i+=1
    def init_virtual_variable(self,user,other_user,room_number):
        virtual_variables = VirtualVariable.objects.all();
        result_virtual_variables = {}
        for virtual_variable in virtual_variables:
            tmp = {}
            tmp["variable_name"]= virtual_variable.variable_name
            tmp["priority"]= virtual_variable.priority
            tmp["1_show"]= virtual_variable.show
            tmp["2_show"]= virtual_variable.show
            tmp["mine_or_other"]= virtual_variable.mine_or_other
            if virtual_variable.mine_or_other == 0:
                if self.user == 1:
               	        tmp["1_value"]= self.calculate_boland(virtual_variable.value)
               	        tmp["2_value"]= self.calculate_boland(virtual_variable.value,None,True)
                else:
                        tmp["1_value"]= self.calculate_boland(virtual_variable.value,None,True)
                        tmp["2_value"]= self.calculate_boland(virtual_variable.value,None)
            else:
                tmp["value"]= self.calculate_boland(virtual_variable.value)
            result_virtual_variables[virtual_variable.variable_name] = tmp
        self.virtual_variables = result_virtual_variables

    def init_deck_info(self,user,other_user,room_number):
        self.deck_structure = Deck.objects.all()
        decks = self.deck_structure

        i=0
        result_decks = []
        result_decks.append(None)
        for deck in decks:
            result_decks.append({})
            result_decks[i+1]["deck_name"] = deck.deck_name
            if(deck.mine_or_other == 1):
                tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = 3,deck_id = i+1).first()
                tmp = json.loads(tmp.deck_content)
                result_decks[i+1]["commondeck"] =tmp
            else:
                tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = user,deck_id = i+1).first()
                tmp = json.loads(tmp.deck_content)
                result_decks[i+1]["mydeck"] = tmp
                tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = other_user,deck_id = i+1).first()
                tmp = json.loads(tmp.deck_content)
                result_decks[i+1]["otherdeck"] = tmp
            i+=1

        self.decks = result_decks
    def init_grave_info(self,user,other_user,room_number):
        self.grave_structure = Grave.objects.all()
        graves = self.grave_structure
        result_graves = []
        result_graves.append(None)
        i=0
        for grave in graves:
            result_graves.append({})
            result_graves[i+1]["grave_name"] = grave.grave_name
            if(grave.mine_or_other == 1):
                tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = 3,grave_id = i+1).first()
                tmp = json.loads(tmp.grave_content)
                result_graves[i+1]["commongrave"] =tmp
            else:
                tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = user,grave_id = i+1).first()
                tmp = json.loads(tmp.grave_content)
                result_graves[i+1]["mygrave"] = tmp
                tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = other_user,grave_id = i+1).first()
                tmp = json.loads(tmp.grave_content)
                result_graves[i+1]["othergrave"] = tmp
            i+=1

        self.graves = result_graves
    def init_hand_info(self,user,other_user,room_number):
        self.hand_structure = Hand.objects.all()
        hands = self.hand_structure
        result_hands = []
        result_hands.append(None)
        i=0
        for hand in hands:
            result_hands.append({})
            result_hands[i+1]["hand_name"] = hand.hand_name
            if(hand.mine_or_other == 1):
                tmp = DuelHand.objects.filter(room_number = room_number,mine_or_other = 3,hand_id = i+1).first()
                tmp = json.loads(tmp.hand_content)
                result_hands[i+1]["commonhand"] =tmp
            else:
                tmp = DuelHand.objects.filter(room_number = room_number,mine_or_other = user,hand_id = i+1).first()
                tmp = json.loads(tmp.hand_content)
                result_hands[i+1]["myhand"] = tmp
                tmp = DuelHand.objects.filter(room_number = room_number,mine_or_other = other_user,hand_id = i+1).first()
                tmp = json.loads(tmp.hand_content)
                result_hands[i+1]["otherhand"] = tmp
            i+=1

        self.hands = result_hands

    def get_grave_with_effect(self,user_decks,effect_det,effect_kind,exclude,user,place,deck_id,x,y,mine_or_other):
        return self.get_deck_with_effect(user_decks,effect_det,effect_kind,exclude,user,place,deck_id,x,y,mine_or_other)
    def get_hand_with_effect(self,user_decks,effect_det,effect_kind,exclude,user,place,deck_id,x,y,mine_or_other):
        return self.get_deck_with_effect(user_decks,effect_det,effect_kind,exclude,user,place,deck_id,x,y,mine_or_other)
    def get_deck_with_effect(self,user_decks,effect_det,effect_kind,exclude,user,place,deck_id,x,y,mine_or_other):
        duel =self.duel
        return_deck = []
        cost =self.cost
        mess =self.mess
        if duel.in_cost ==1:
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
        timing_mess = self.timing_mess
        for index in range(len(user_decks)):
            effect_flag = False
            if effect_kind != "":
                if self.check_no_choose(user_decks[index],user,effect_kind,place,deck_id,x,y,mine_or_other):
                   effect_flag = True
            if exclude != "":
                excludes = exclude.split(",")
                for exclude_det in excludes:
                    if exclude_det[0] == "~":
                        if exclude_det[1:] in cost:
                            for cost_det in cost[exclude_det[1:]]:
                                if(user_decks[index]["place_unique_id"] == cost_det["place_id"]):
                                    continue
                    if exclude_det[0] == "%":
                        if exclude_det[1:] in timing_mess:
                            for timing_det in timing_mess[exclude_det[1:]]:
                                if(user_decks[index]["place_unique_id"] == timing_det["place_id"]):
                                    continue
                    if exclude_det in mess:
                        for mess_det in mess[exclude_det]:
                            if(user_decks[index]["place_unique_id"] == mess_det["place_id"]):
                                continue

            current_and_or = "and"
            monster_name_kind = effect_det["monster"]["monster_name_kind"]
            name_flag = True
            if len(monster_name_kind) !=1 or monster_name_kind[0]["operator"] != "":
                for name_kind in monster_name_kind:
                    if name_kind != "":
                        if(name_kind["operator"] == "="):
                            if(monster["monster_name"] != self.get_name(name_kind["monster_name"])):
                                if(current_and_or == "and"):
                                    name_flag = False
                            else:
                                if(current_and_or == "or"):
                                    name_flag = True
                            current_and_or = name_kind["and_or"]


                        elif(name_kind["operator"] == "like"):
                            if(monster["monster_name"].find(self.get_name(name_kind["monster_name"])) >-1):
                                if(current_and_or == "and"):
                                    name_flag = False
                            else:
                                if(current_and_or == "or"):
                                    name_flag = True
                            current_and_or = name_kind["and_or"]
            if name_flag == False:
                continue
            monster_condition_val = effect_det["monster"]["monster_condition"]
            if monster_condition_val:
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
                            if int(value) != self.calculate_boland(cond_val["num"]):
                                tmp_flag= False
                        elif(cond_val["operator"] == "<="):
                            if int(value) > self.calculate_boland(cond_val["num"]):
                                tmp_flag= False
                        elif(cond_val["operator"] == ">="):
                            if int(value) < self.calculate_boland(cond_val["num"]):
                                tmp_flag= False
                        elif(cond_val["operator"] == "!="):
                            if int(value) == self.calculate_boland(cond_val["num"]):
                                tmp_flag= False
                        if current_and_or == "and":
                            if(cond_flag == True):
                               cond_flag = tmp_flag

                        else:
                            if(cond_flag == False):
                                cond_flag = tmp_flag

                if(cond_flag == False):
                    continue
            if effect_flag == False:
                return_deck.append(index)
        return return_deck
    def get_deck_info(self,decks,user,other_user,mode=0):
        dueldeck = self.decks
        duel = self.duel
        room_number = self.room_number
        return_value = []

        i=0
        for deck in decks:
            return_value.append({})
            return_value[i]["deck_name"] = deck.deck_name
            return_value[i]["eternal"] = deck.eternal
            return_value[i]["invoke"] = deck.invoke
            if(deck.mine_or_other == 1):
                tmp = dueldeck[i+1]["commondeck"]
                if mode == 1:
                    if(deck.show >= 1):
                        return_value[i]["commondeck"] =tmp
                else:
                    return_value[i]["commondeck"] =tmp
                return_value[i]["commondecknum"] = len(tmp)
            else:
                tmp = dueldeck[i+1]["mydeck"]
                return_value[i]["mydecknum"] = len(tmp)
                if mode == 1:
                    if(deck.show >= 1):
                        return_value[i]["mydeck"] = tmp
                else:
                    return_value[i]["mydeck"] = tmp
                tmp = dueldeck[i+1]["otherdeck"]
                return_value[i]["otherdecknum"] = len(tmp)
                if mode == 1:
                    if(deck.show >= 2):
                        return_value[i]["otherdeck"] = tmp
                else:
                    return_value[i]["otherdeck"] = tmp
            i+=1
        return return_value
    def get_grave_info(self,graves,user,other_user,mode=0):
        duelgrave = self.graves
        duel = self.duel
        room_number = self.room_number
        return_value = []


        i=0
        for grave in graves:
            return_value.append({})
            return_value[i]["grave_name"] = grave.grave_name
            return_value[i]["eternal"] = grave.eternal
            return_value[i]["invoke"] = grave.invoke
            if(grave.mine_or_other == 1):
                tmp = duelgrave[i+1]["commongrave"]
                if mode ==1:
                    if(grave.show >= 1):
                        return_value[i]["commongrave"] =tmp
                else:
                    return_value[i]["commongrave"] =tmp
                return_value[i]["commongravenum"] = len(tmp)
            else:
                tmp = duelgrave[i+1]["mygrave"]
                return_value[i]["mygravenum"] = len(tmp)
                if mode ==1:
                    if(grave.show >= 1):
                        return_value[i]["mygrave"] = tmp
                else:
                    return_value[i]["mygrave"] =tmp
                tmp = duelgrave[i+1]["othergrave"]
                return_value[i]["othergravenum"] = len(tmp)
                if mode ==1:
                    if(grave.show >= 2):
                        return_value[i]["othergrave"] = tmp
                else:
                    return_value[i]["othergrave"] =tmp
            i+=1
        return return_value
    def watch_hand(self,hands):
        return self.get_hand_info(hands,0,0,mode=2)
    def get_hand_info(self,hands,user,other_user,mode=0):
        duelhand = self.hands
        duel = self.duel
        room_number = self.room_number
        return_value = []


        i=0
        for hand in hands:
            return_value.append({})
            return_value[i]["hand_name"] = hand.hand_name
            return_value[i]["eternal"] = hand.eternal
            return_value[i]["invoke"] = hand.invoke
            if(hand.mine_or_other == 1):
                tmp = duelhand[i+1]["commonhand"]
                if mode ==1 or mode == 2:
                    if(hand.show >= 1):
                        return_value[i]["commonhand"] =tmp
                else:
                    return_value[i]["commonhand"] =tmp
                return_value[i]["commonhandnum"] = len(tmp)
            else:
                tmp = duelhand[i+1]["myhand"]
                return_value[i]["myhandnum"] = len(tmp)
                if mode ==1 :
                    if(hand.show >= 1):
                        return_value[i]["myhand"] = tmp
                elif mode ==2 :
                    if(hand.show >= 2):
                        return_value[i]["myhand"] = tmp
                else:
                    return_value[i]["myhand"] = tmp
                tmp = duelhand[i+1]["otherhand"]
                return_value[i]["otherhandnum"] = len(tmp)
                if mode ==1 or mode == 2:
                    if(hand.show >= 2):
                        return_value[i]["otherhand"] = tmp
                else:
                    return_value[i]["otherhand"] = tmp
            i+=1
        return return_value






    def invoke_eternal_effect_det(self,eternal,effect_user):
        duel = self.duel
        eternal_effect = EternalEffect.objects.get(id = eternal["eternal"])
        invalid_kinds=eternal_effect.invalid_eternal_kind
        val = eternal_effect.eternal_effect_val
        persist = eternal_effect.persist
        eternal["persist"] = persist
        val2 = eternal_effect.eternal_effect_val2
        tmps = json.loads(eternal_effect.invalid_monster)
        kinds=eternal_effect.eternal_kind
        eternal["invalid_kinds"] = invalid_kinds
        if val == 1:
            c_val = eternal_effect.eternal_effect_variable
            c2_val = eternal_effect.eternal_effect_variable_val
        else:
            c_val = 0
            c2_val = 0
        tmps = tmps["monster"]
        global_id = eternal_effect.eternal_global_variable
        if eternal["place"]  == "":
            flag = True
            det = {}
            det["place_unique_id"] = ""
        elif eternal["place"] == "field":
            fields= self.field
            x = eternal["x"]
            y = eternal["y"]
            det = fields[x][y]["det"]
            eternal["place_id"] = det["place_unique_id"]
            if  not self.check_eternal_invalid(det,effect_user,invalid_kinds,"field",0,x,y,fields[x][y]["mine_or_other"]):
                fields[x][y]["det"]["already"] = 1
                flag = True
                self.field=fields
            else:
                fields[x][y]["det"]["already"] = 0
                flag =  False
                self.field=fields
        elif eternal["place"] == "deck":
            deck_id = int(eternal["deck_id"])
            mine_or_other = eternal["mine_or_other"]
            if (effect_user == 1 and mine_or_other == 1) or (effect_user == 2 and mine_or_other == 2):
                mine_or_other2 = 1
            elif (effect_user == 2 and mine_or_other == 1) or (effect_user == 1 and mine_or_other == 2):
                mine_or_other2 = 2
            else:
                mine_or_other2 = 3
            if mine_or_other == 1:
                decks = self.decks[deck_id]["mydeck"]
            elif mine_or_other == 2:
                decks = self.decks[deck_id]["otherdeck"]
            elif mine_or_other == 3:
                decks = self.decks[deck_id]["commondeck"]
            if "index" in eternal:
                i = eternal["index"]
            else:
                i=-1
                for deck_i in range(len(decks)):
                    if decks[deck_i]["place_unique_id"] == eternal["place_id"]:
                        i = deck_i
                        break
                if i==-1:
                    return
            det=decks[i]
            if  not self.check_eternal_invalid(decks[i],effect_user,invalid_kinds,"deck",deck_id,0,0,mine_or_other2):
                decks[i]["already"]= 1
                flag = True
            else:
                flag = False
                decks[i]["already"]= 0
            if mine_or_other2 == 1:
                self.decks[deck_id]["mydeck"] = decks
            elif mine_or_other2 == 2:
                self.decks[deck_id]["otherdeck"]= decks
            elif mine_or_other2 == 3:
                self.decks[deck_id]["commondeck"] = decks
        elif eternal["place"] == "grave":
            deck_id = int(eternal["deck_id"])
            mine_or_other = eternal["mine_or_other"]
            if (effect_user == 1 and mine_or_other == 1) or (effect_user == 2 and mine_or_other == 2):
                mine_or_other2 = 1
            elif (effect_user == 2 and mine_or_other == 1) or (effect_user == 1 and mine_or_other == 2):
                mine_or_other2 = 2
            else:
                mine_or_other2 = 3
            if mine_or_other2 == 1:
                graves = self.graves[deck_id]["mygrave"]
            elif mine_or_other2 == 2:
                graves = self.graves[deck_id]["othergrave"]
            elif mine_or_other2 == 3:
                graves = self.graves[deck_id]["commongrave"]
            if "index" in eternal:
                i = eternal["index"]
            else:
                i=-1
                for grave_i in range(len(graves)):
                    if graves[grave_i]["place_unique_id"] == eternal["place_id"]:
                        i = grave_i
                        break
                if i==-1:
                    return
            det=graves[i]
            if  not self.check_eternal_invalid(graves[i],effect_user,invalid_kinds,"grave",deck_id,0,0,mine_or_other2):
                graves[i]["already"]= 1
                flag = True
            else:
                flag = False
                graves[i]["already"]= 0
            if mine_or_other2 == 1:
                self.graves[deck_id]["mygrave"] = graves
            elif mine_or_other2 == 2:
                self.graves[deck_id]["othergrave"] = graves
            elif mine_or_other2 == 3:
                self.graves[deck_id]["commongrave"] = graves
        elif eternal["place"] == "hand":
            deck_id = int(eternal["deck_id"])
            mine_or_other = eternal["mine_or_other"]
            if (effect_user == 1 and mine_or_other == 1) or (effect_user == 2 and mine_or_other == 2):
                mine_or_other2 = 1
            elif (effect_user == 2 and mine_or_other == 1) or (effect_user == 1 and mine_or_other == 2):
                mine_or_other2 = 2
            else:
                mine_or_other2 = 3
            if mine_or_other2 == 1:
                hands = self.hands[deck_id]["myhand"]
            elif mine_or_other2 == 2:
                hands = self.hands[deck_id]["otherhand"]
            elif mine_or_other2 == 3:
                hands = self.hands[deck_id]["commonhand"]
            if "index" in eternal:
                i = eternal["index"]
            else:
                i=-1
                for hand_i in range(len(hands)):
                    if hands[hand_i]["place_unique_id"] == eternal["place_id"]:
                        i = hand_i
                        break
                if i != -1:
                    det=hands[i]
                else:
                    return
            if  not self.check_eternal_invalid(hands[i],effect_user,invalid_kinds,"hand",deck_id,0,0,mine_or_other2):
                hands[i]["already"]= 1
                flag = True
            else:
                flag =  False
                hands[i]["already"]= 0
            if mine_or_other2 == 1:
                self.hands[deck_id]["myhand"] = hands
            elif mine_or_other2 == 2:
                self.hands[deck_id]["otherhand"] = hands
            elif mine_or_other2 == 3:
                self.hands[deck_id]["commonhand"] = hands
        if flag == True:
            if val == 0:
                if val2 == 0 or val2 == 2 or val2 == 4:
                    self.no_eternal_effect(eternal,invalid_kinds,det["place_unique_id"],global_id)
                if val2 == 1 or val2 == 2 or val2 == 4:
                    self.invoke_invalid_effect(eternal,invalid_kinds,det["place_unique_id"],global_id)
                if val2 == 3 :
                    self.not_effected_effect(eternal,invalid_kinds,det["place_unique_id"],global_id)
            if val == 1:
                self.change_variable_effect(eternal,invalid_kinds,det["place_unique_id"],global_id)
            if val == 2 or val == 0 and val2 == 4:
                self.no_invoke_effect(eternal,invalid_kinds,det["place_unique_id"],global_id)
            if val == 3:
                self.no_choose_effect(eternal,invalid_kinds,det["place_unique_id"],global_id)
        else:
            if val == 0:
                if val2 == 0 or val2 == 2 or val2 == 4:
                    self.no_eternal_effect_remove(eternal,invalid_kinds,det["place_unique_id"],global_id)
                if val2 == 1 or val2 == 2 or val2 == 4:
                    self.invoke_invalid_effect_remove(eternal,invalid_kinds,det["place_unique_id"],global_id)
                if val2 == 3 :
                    self.not_effected_effect_remove(eternal,invalid_kinds,det["place_unique_id"],global_id)
            if val == 1:
                self.change_variable_effect_remove(eternal,invalid_kinds,det["place_unique_id"],global_id)
            if val == 2 or val == 0 and val2 == 4:
                self.no_invoke_variable_effect_remove(eternal,invalid_kinds,det["place_unique_id"],global_id)
            if val == 3:
                self.no_choose_effect_remove(eternal,invalid_kinds,det["place_unique_id"],global_id)
        return
    def no_choose_effect_remove(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if eternal in self.no_choose_eternal_effect:
            self.no_choose_eternal_effect.remove(eternal)
    def no_choose_effect(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if not eternal in self.no_choose_eternal_effect:
            self.no_choose_eternal_effect.append(eternal)
    def change_variable_effect_remove(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if eternal in self.change_val_eternal_effect:
            self.change_val_eternal_effect.remove(eternal)
    def change_variable_effect(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if not eternal in self.change_val_eternal_effect:
            self.change_val_eternal_effect.append(eternal)
    def no_eternal_effect_remove(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if eternal in self.not_eternal_effect:
            self.not_eternal_effect.remove(eternal)
    def no_eternal_effect(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if not eternal in self.not_eternal_effect:
            self.not_eternal_effect.append(eternal)
    def not_effected_effect_remove(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if eternal in self.not_effected_eternal_effect:
            self.not_effected_eternal_effect.remove(eternal)
    def not_effected_effect(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if not eternal in self.not_effected_eternal_effect:
            self.not_effected_eternal_effect.append(eternal)
    def invoke_invalid_effect_remove(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if eternal in self.invoke_invalid_eternal_effect:
            self.invoke_invalid_eternal_effect.remove(eternal)
    def invoke_invalid_effect(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if not eternal in self.invoke_invalid_eternal_effect:
            self.invoke_invalid_eternal_effect.append(eternal)
    def no_invoke_effect_remove(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if eternal in self.no_invoke_eternal_effect:
            self.no_invoke_eternal_effect.remove(eternal)
    def no_invoke_effect(self,eternal,invalid_kinds,place_id,global_id):
        eternal["invalid_kinds"] = invalid_kinds
        eternal["place_id"] = place_id
        eternal["global_name"] = global_id
        if not eternal in self.no_invoke_eternal_effect:
            self.no_invoke_eternal_effect.append(eternal)





    def invoke_eternal_effect(self,eternal_effects,user,other_user):
        duel = self.duel
        room_number = self.room_number
        decks = self.deck_structure
        graves = self.grave_structure
        hands = self.hand_structure
        fields = self.field
        eternals = []
        for eternal in eternal_effects:


            if(eternal.eternal_global_variable):
                tmp = eternal.eternal_global_variable.split("_")
                mine_or_other = int(tmp[1])
                variable = json.loads(duel.global_variable)
                tmp_val = int(eternal.eternal_global_variable_val)
                user_flag = True
                other_user_flag = True
                if mine_or_other == 3:
                    other_user_flag = False
                    if not variable[tmp[0]]["value"]==tmp_val:
                        user_flag = False
                else :
                    if user == 1:
                        other_user_flag = False
                        if mine_or_other == 1 :
                            if not variable[tmp[0]]["1_value"]==tmp_val:
                                user_flag = False
                        elif mine_or_other == 2 :
                            if not variable[tmp[0]]["2_value"]==tmp_val:
                                user_flag = False
                    else:
                        user_flag = False
                        if mine_or_other == 1 :
                            if not variable[tmp[0]]["2_value"]==tmp_val:
                                other_user_flag = False
                        elif mine_or_other == 2:
                            if not variable[tmp[0]]["1_value"]==tmp_val:
                                other_user_flag = False
                    if user_flag == True:
                        tmp={}
                        tmp["eternal"] = eternal.id
                        tmp["place"] = ""
                        tmp["effect_val"] = eternal.eternal_effect_val
                        tmp["kind"] = eternal.eternal_kind
                        tmp["priority"] = eternal.priority
                        tmp["already"] = 0
                        tmp["user"] = user
                        eternals.append(tmp)
                    if other_user_flag == True:
                        tmp={}
                        tmp["eternal"] = eternal.id
                        tmp["place"] = ""
                        tmp["effect_val"] = eternal.eternal_effect_val
                        tmp["kind"] = eternal.eternal_kind
                        tmp["priority"] = eternal.priority
                        tmp["already"] = 0
                        tmp["user"] = other_user
                        eternals.append(tmp)
        deck_info = self.get_deck_info(decks,user,other_user,0)
        grave_info = self.get_grave_info(graves,user,other_user,0)
        hand_info = self.get_hand_info(hands,user,other_user,0)
        eternals += self.check_field_eternal(fields,user,other_user)
        eternals += self.check_deck_eternal(deck_info,decks.count(),user,other_user)
        eternals += self.check_grave_eternal(grave_info,graves.count(),user,other_user)
        eternals += self.check_hand_eternal(hand_info,hands.count(),user,other_user)
        eternals = sorted(eternals,key = lambda x: x["already"],reverse=True)
        eternals = sorted(eternals,key = lambda x: x["priority"],reverse=True)
        while True:
            no_choose_eternal_effect = self.no_choose_eternal_effect
            change_val_eternal_effect = self.change_val_eternal_effect
            invoke_invalid_eternal_effect = self.invoke_invalid_eternal_effect
            no_invoke_eternal_effect = self.no_invoke_eternal_effect
            not_effected_eternal_effect = self.not_effected_eternal_effect
            not_eternal_effect = self.not_eternal_effect
            for eternal in eternals:
                if eternal["user"] == user:
                    self.invoke_eternal_effect_det(eternal,user)
                elif eternal["user"] == other_user:
                    self.invoke_eternal_effect_det(eternal,other_user)
            if self.no_choose_eternal_effect== no_choose_eternal_effect and  self.change_val_eternal_effect == change_val_eternal_effect and self.invoke_invalid_eternal_effect == invoke_invalid_eternal_effect and self.invoke_invalid_eternal_effect == invoke_invalid_eternal_effect and self.not_effected_eternal_effect == not_effected_eternal_effect and self.not_eternal_effect == not_eternal_effect and self.no_invoke_eternal_effect == no_invoke_eternal_effect:
                break


    def clear_eternal_effect(self,decks,graves,hands):
        duel = self.duel
        room_number = self.room_number
        i=0
        self.no_choose_eternal_effect= []
        self.change_val_eternal_effect =[]
        self.invoke_invalid_eternal_effect = []
        self.no_invoke_eternal_effect = []
        self.not_effected_eternal_effect = []
        self.not_eternal_effect = []
    def check_eternal_effect(self,decks,graves,hands,phase,turn,user,other_user):
        self.clear_eternal_effect(decks,graves,hands)
        self.init_virtual_variable(user,other_user,self.room_number)
        duel = self.duel
        eternal_effects = EternalEffect.objects.filter(Q(phase = phase) | Q(phase__isnull=True ))
        eternal_effects = eternal_effects.filter(Q(chain__isnull = True) | Q(chain=duel.chain,chain_kind=2) | Q(chain__lte=duel.chain,chain_kind=0)| Q(chain__gte=duel.chain,chain_kind=1)  )
        eternal_effects = eternal_effects.filter(none_monster = True)
        if duel.timing != None:
            eternal_effects = eternal_effects.filter(Q(timing=duel.timing))
        else:
            eternal_effects = eternal_effects.filter(Q(none_timing = True))
        eternal_effects = eternal_effects.order_by('eternal_effect_val')
        eternal_effects = eternal_effects.order_by('-priority')
        self.invoke_eternal_effect(eternal_effects,user,other_user)
        none_chain_effects = EternalTrigger.objects.all()
        none_chain_effects = none_chain_effects.filter(Q(phase__isnull=True) | Q(phase = phase))
        none_chain_effects = none_chain_effects.filter(Q(chain__isnull = True) | \
                                   (Q(chain_kind = 0) & Q(chain__lte=duel.chain)) | \
                                   (Q(chain_kind = 1) & Q(chain__gte=duel.chain)) | \
                                   (Q(chain_kind = 2) & Q(chain=duel.chain)))
        if duel.timing != None:
            none_chain_effects = none_chain_effects.filter(Q(timing=duel.timing))
        else:
            none_chain_effects = none_chain_effects.filter(Q(none_timing = True))
        none_chain_effects = none_chain_effects.order_by('-priority')
        eternal_det = json.loads(duel.eternal_det)
        flag = True
        for none_chain_effect in none_chain_effects:
            if none_chain_effect.id in eternal_det:
                continue
            eternal_wrapper = none_chain_effect.eternal_effect_next

            kinds = eternal_wrapper.monster_effect_kind
            if self.invoke_no_chain_effect(eternal_wrapper,user,other_user,kinds) == 0:
                eternal_det.append(none_chain_effect.id)
            else:
                flag = False
                break;
        if flag == True:
            duel.eternal_det = json.dumps([])
        else:
            duel.eternal_det = json.dumps(eternal_det)


    def retrieve_chain(self,decks,graves,hands,phase,user_turn,user,other_user):
        duel = self.duel
        chain_det = json.loads(self.duel.chain_det)
        current_chain = chain_det[str(self.duel.chain-1)]
        monster_effect = MonsterEffectWrapper.objects.get(id = current_chain)
        kinds = monster_effect.monster_effect_kind
        monster_effect_next = self.invoke_monster_effect(monster_effect,decks,graves,kinds)
        if monster_effect_next == None:
            pac = json.loads(duel.in_pac)
            if pac != []:
                pac_id = pac.pop()
                pac = PacWrapper.objects.get(id=pac_id)
                monster_effect_next =  pac.monster_effect_next
        elif monster_effect_next == -2:
            monster_effect_next = None
        while monster_effect_next:
            if duel.winner != 0:
                return
            if monster_effect_next == -1:
                return
            else:
                chain_det[str(self.duel.chain-1)] = monster_effect_next.id
                self.duel.chain_det = json.dumps(chain_det)
                monster_effect = monster_effect_next
                if(monster_effect.monster_effect.monster_effect_val == 5):
                    effect_kind = monster_effect.monster_effect_kind
                    if duel.in_pac != "[]":
                        pac = json.loads(duel.in_pac)
                        pac_id = pac.pop()
                        pac = PacWrapper.objects.get(id=pac_id)
                        if pac.monster_effect_kind != "":
                            effect_kind = pac.monster_effect_kind
                    self.duel.ask_kind = effect_kind
                    self.duel.ask = 3
                elif(monster_effect.monster_effect.monster_effect_val == 3):
                    effect_kind = monster_effect.monster_effect_kind
                    if duel.in_pac != "[]":
                        pac = json.loads(duel.in_pac)
                        pac_id = pac.pop()
                        pac = PacWrapper.objects.get(id=pac_id)
                        if pac.monster_effect_kind != "":
                            effect_kind = pac.monster_effect_kind
                    self.duel.ask_kind = effect_kind
                    self.duel.ask = 1

                elif(monster_effect.monster_effect.monster_effect_val == 4):
                    effect_kind = monster_effect.monster_effect_kind
                    if duel.in_pac != "[]":
                        pac = json.loads(duel.in_pac)
                        pac_id = pac.pop()
                        pac = PacWrapper.objects.get(id=pac_id)
                        if pac.monster_effect_kind != "":
                            effect_kind = pac.monster_effect_kind
                    self.duel.ask_kind = effect_kind
                    self.duel.ask = 2
                if(monster_effect.monster_effect.eternal_flag == True):
                    self.check_eternal_effect(decks,graves,hands,phase,turn,user,other_user)
                effect_kind = monster_effect.monster_effect_kind
                monster_effect_next = self.invoke_monster_effect(monster_effect,decks,graves,effect_kind)
                if monster_effect_next == None:
                    pac = json.loads(duel.in_pac)
                    if pac != []:
                        pac_id = pac.pop()
                        pac = PacWrapper.objects.get(id=pac_id)
                        monster_effect_next =  pac.monster_effect_next
                elif monster_effect_next == -2:
                    monster_effect_next = None

        del chain_det[str(self.duel.chain-1)]
        self.duel.chain_det = json.dumps(chain_det)
        self.duel.chain-=1
        if(self.duel.chain != 0):
            current_chain = chain_det[str(self.duel.chain-1)]
            monster_effect = MonsterEffectWrapper.objects.get(id = current_chain)
            if(monster_effect.monster_effect.monster_effect_val == 5):
                effect_kind = monster_effect.monster_effect_kind
                if duel.in_pac != "[]":
                    pac = json.loads(duel.in_pac)
                    pac_id = pac.pop()
                    pac = PacWrapper.objects.get(id=pac_id)
                    if pac.monster_effect_kind != "":
                        effect_kind = pac.monster_effect_kind
                self.duel.ask_kind = effect_kind
                self.duel.ask = 3
            elif(monster_effect.monster_effect.monster_effect_val == 3):
                effect_kind = monster_effect.monster_effect_kind
                if duel.in_pac != "[]":
                    pac = json.loads(duel.in_pac)
                    pac_id = pac.pop()
                    pac = PacWrapper.objects.get(id=pac_id)
                    if pac.monster_effect_kind != "":
                        effect_kind = pac.monster_effect_kind
                self.duel.ask_kind = effect_kind
                self.duel.ask = 1

            elif(monster_effect.monster_effect.monster_effect_val == 4):
                effect_kind = monster_effect.monster_effect_kind
                if duel.in_pac != "[]":
                    pac = json.loads(duel.in_pac)
                    pac_id = pac.pop()
                    pac = PacWrapper.objects.get(id=pac_id)
                    if pac.monster_effect_kind != "":
                        effect_kind = pac.monster_effect_kind
                self.duel.ask_kind = effect_kind
                self.duel.ask = 2
            else:
                self.duel.ask = 0



    def invoke_cost(self,cost):
        duel = self.duel
        cost_unwrap = cost.cost
        chain_user = json.loads(duel.chain_user)
        user = chain_user[str(duel.chain)]
        if cost_unwrap.cost_val == 0:
            cost_condition = json.loads(cost_unwrap.cost_condition)
            duel.cost_log += self.write_log(cost.log,user)
            if self.check_cost_condition(cost_condition):
                if cost.pac:
                    return self.push_pac_cost(cost.pac)
                else:
                    if cost.cost_next:
                        return cost.cost_next
                    else:
                        return self.pop_pac_cost(user)
            else:
                if cost.pac2:
                    return self.push_pac_cost(cost.pac2)
                else:
                    if cost.cost_next2:
                        return cost.cost_next2
                    else:
                        return self.pop_pac_cost2(user)


        elif cost_unwrap.cost_val == 5 or cost_unwrap.cost_val == 4 or cost.cost.cost_val == 3:
            duel.cost_log += self.write_log(cost.log,user)
            if(self.duel.ask > 0):
                self.duel.ask_det = cost.cost.cost
                return -1

            else:
                if cost.pac:
                    return self.push_pac_cost(cost.pac)
                elif cost.cost_next:
                    return cost.cost_next
                else:
                    return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 17:
            cost_kind = cost_unwrap.cost_kind
            duel.cost_log += self.write_log(cost.log,user)
            move_to = self.move_from_monster_simple_cost(cost_kind)

            if move_to is not None:
                self.move_to_monster_cost(move_to,cost_kind)
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 1:
            duel.cost_log += self.write_log(cost.log,user)
            cost_kind = cost.cost.cost_kind
            move_to = self.move_from_monster_cost(cost_kind)

            if move_to is not None:
                self.move_to_monster_cost(move_to,cost_kind)
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 7:
            duel.cost_log += self.write_log(cost.log,user)
            self.move_phase_cost()
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 8:
            duel.cost_log += self.write_log(cost.log,user)
            self.change_turn_cost()
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 2:
            duel.cost_log += self.write_log(cost.log,user)
            self.change_variable_cost()
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 9:
            duel.cost_log += self.write_log(cost.log,user)
            cost_kind = cost.cost_kind
            self.change_monster_variable_cost(cost.cost.cost,cost_kind)
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 10:
            duel.cost_log += self.write_log(cost.log,user)
            self.shuffle_cost()
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 11:
            duel.cost_log += self.write_log(cost.log,user)
            self.clear_cost()
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 18:
            duel.cost_log += self.write_log(cost.log,user)
            self.move_effect_variable_to_timing(1)
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
        elif cost_unwrap.cost_val == 20:
            duel.cost_log += self.write_log(cost.log,user)
            self.cancel_cost()
            return -1
        elif cost_unwrap.cost_val == 21:
            duel.cost_log += self.write_log(cost.log,user)
            self.play_music(monster_effect.monster_effect.monster_effect)
            if cost.pac:
                return self.push_pac_cost(cost.pac)
            elif cost.cost_next:
                return cost.cost_next
            else:
                return self.pop_pac_cost(user)
    def play_music(self,music_name):
        self.duel.audio = music_name;
        return
    def win_the_game(self,cost =0):
        self.duel.end_time = time()
        if cost == 0:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain-1)]
        elif cost == 1:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain)]
        else :
            user = self.user
        if self.duel.winner == 0:
            self.duel.winner = user;
            self.duel.save();
    def lose_the_game(self,cost =0):
        self.duel.end_time = time()
        if cost == 0:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain-1)]
        elif cost == 1:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain)]
        else :
            user = self.user
        if self.duel.winner == 0:
            if user == 1:
                self.duel.winner = 2;
            elif user == 2:
                self.duel.winner = 1;
            self.duel.save();
        return
    def cancel_cost(self):
        self.duel.in_cost = False
        self.duel.in_pac = "[]"
        self.duel.in_pac_cost = "[]"
        self.duel.cost_log = ""
        self.cost_result = {}
        self.duel.ask = 0
        return
    def check_cost_condition(self,cost_condition):
        return self.check_monster_effect_condition(cost_condition,1)

    def check_monster_effect_condition(self,monster_effect_conditions,cost=0):
        duel = self.duel
        if cost == 0:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain-1)]
        elif cost == 1:
            chain_user = json.loads(duel.chain_user)
            user = chain_user[str(duel.chain)]
        else:
            user = self.user
        if "monster" in monster_effect_conditions:
            if(self.check_monster_condition(monster_effect_conditions["monster"],user,False) == False):
                return False
            else:
                return True
        for monster_effect_condition in monster_effect_conditions:
            if "variable" in monster_effect_condition:
                for key in monster_effect_condition["variable"].keys():
                    variable_condition=monster_effect_condition
                    variable = monster_effect_condition["variable"][key]
                    variable = variable.split("_")
                    mine_or_other = int(variable[2])
                    variable_name = variable[1]
                    variable = json.loads(duel.global_variable)
                    virtual_variables = self.virtual_variables
                    variable.update(virtual_variables)
                    if mine_or_other == 0:
                        if(variable_condition["variable_equation"][key] == "="):
                            if not variable[variable_name]["value"]==self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == "<="):
                            if not variable[variable_name]["value"]<=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == ">="):
                            if not variable[variable_name]["value"]>=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == "!="):
                            if not variable[variable_name]["value"]!=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                    if mine_or_other == 1 and user == 1 or mine_or_other == 2 and user == 2:
                        if(variable_condition["variable_equation"][key]== "="):
                            if not variable[variable_name]["1_value"]==self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == "<="):
                            if not variable[variable_name]["1_value"]<=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == ">="):
                            if not variable[variable_name]["1_value"]>=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == "!="):
                            if not variable[variable_name]["1_value"]!=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                    if mine_or_other == 2 and user == 1 or mine_or_other == 1 and user == 2:
                        if(variable_condition["variable_equation"][key] == "="):
                            if not variable[variable_name]["2_value"]==self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == "<="):
                            if not variable[variable_name]["2_value"]<=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == ">="):
                            if not variable[variable_name]["2_value"]>=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
                        elif(variable_condition["variable_equation"][key] == "!="):
                            if not variable[variable_name]["2_value"]!=self.calculate_boland(variable_condition["variable_equation_val"][key]):
                                return False
        return True
    def pop_pac_cost(self,user):
        duel = self.duel
        if duel.in_pac_cost == "[]":
            return -2
        pac = json.loads(duel.in_pac_cost)

        pac_id = pac.pop()
        duel.in_pac_cost = json.dumps(pac)
        pac = PacCostWrapper.objects.get(id=pac_id)
        duel.cost_log += self.write_log(pac.log,user)
        if pac.pac_next is not None:
            return self.push_pac_cost(pac.pac_next)
        if pac.cost_next is None:
            return -2
        else:
            return pac.cost_next
    def pop_pac_cost2(self,user):
        duel = self.duel
        if duel.in_pac_cost == "[]":
            return -2
        pac = json.loads(duel.in_pac_cost)

        pac_id = pac.pop()
        duel.in_pac_cost = json.dumps(pac)
        pac = PacCostWrapper.objects.get(id=pac_id)
        duel.cost_log += self.write_log(pac.log,user)
        if pac.pac_next2 is not None:
            return self.push_pac_cost(pac.pac_next2)
        if pac.cost_next2 is None:
            return -2
        else:
            return pac.cost_next2
    def get_pac_effect_kind(self):
        duel = self.duel
        if duel.in_pac == "[]":
            return None
        pac = json.loads(duel.in_pac)
        pac_id = pac[0]
        pac = PacWrapper.objects.get(id=pac_id)
        if pac.monster_effect_kind == "":
            return None
        else:
            return pac.monster_effect_kind
    def get_pac_cost_effect_kind(self):
        duel = self.duel
        if duel.in_pac_cost == "[]":
            return None
        pac = json.loads(duel.in_pac_cost)
        pac_id = pac[0]
        pac = PacCostWrapper.objects.get(id=pac_id)
        if pac.monster_effect_kind == "":
            return None
        else:
            return pac.monster_effect_kind
    def pop_pac(self,user):
        duel = self.duel
        if duel.in_pac == "[]":
            return -2
        pac = json.loads(duel.in_pac)

        pac_id = pac.pop()
        duel.in_pac = json.dumps(pac)
        pac = PacWrapper.objects.get(id=pac_id)
        log_tmp = self.write_log(pac.log,user)
        duel.log_turn += log_tmp
        duel.log += log_tmp
        if pac.pac_next is not None:
            return self.push_pac(pac.pac_next)
        if pac.monster_effect_next is None:
            return -2
        else:
            return pac.monster_effect_next
    def pop_pac2(self,user):
        duel = self.duel
        if duel.in_pac == "[]":
            return -2
        pac = json.loads(duel.in_pac)

        pac_id = pac.pop()
        duel.in_pac = json.dumps(pac)
        pac = PacWrapper.objects.get(id=pac_id)
        log_tmp = self.write_log(pac.log,user)
        duel.log_turn += log_tmp
        duel.log += log_tmp
        if pac.pac_next2 is not None:
            return self.push_pac(pac.pac_next2)
        if pac.monster_effect_next2 is None:
            return -2
        else:
            return pac.monster_effect_next2
    def push_pac(self,effect_pac):
        duel = self.duel
        pac = json.loads(duel.in_pac)
        pac.append(effect_pac.id)
        duel.in_pac=json.dumps(pac)
        return effect_pac.pac.pac_next
    def push_pac_cost(self,cost_pac):
        duel = self.duel
        pac = json.loads(duel.in_pac_cost)
        pac.append(cost_pac.id)
        duel.in_pac_cost=json.dumps(pac)
        return cost_pac.pac_cost.pac_cost_next
    def get_trigger_monster(self):
        duel = self.duel
        room_number = self.room_number
        mess = self.mess
        if not str(duel.chain-1) in mess:
            return None
        if not 0 in mess[str(duel.chain-1)]:
            return None
        trigger = mess[str(duel.chain-1)][0]
        return trigger


    def check_invoke_monster_effect(self,monster,user,effect_kind,place,deck_id,x,y,mine_or_other,monster_from,place_from,deck_id_from,from_x,from_y):
        duel = self.duel
        if self.check_invoke_invalid(monster,user,effect_kind,place,deck_id,x,y,mine_or_other):
            return False
        if self.check_invoke_invalid(monster_from,user,effect_kind,place_from,deck_id_from,from_x,from_y,mine_or_other,1):
            return False
        return True

    def invoke_no_chain_effect(self,monster_effect,decks,graves,kinds):
        duel = self.duel
        user = self.user

        while monster_effect:
            if duel.winner != 0:
                return
            monster_effect_unwrap = monster_effect.monster_effect
            if monster_effect_unwrap.monster_effect_val == 0:
                monster_effect_condition = json.loads(monster_effect.monster_effect.monster_condition)
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                if self.check_monster_effect_condition(monster_effect_condition,2):
                    monster_effect= monster_effect.monster_effect_next
                else:
                    monster_effect= monster_effect.monster_effect_next2

            elif monster_effect_unwrap.monster_effect_val == 5 or monster_effect_unwrap.monster_effect_val == 4 or monster_effect_unwrap.monster_effect_val == 3:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                if(self.duel.ask > 0):
                    duel.in_eternal = True
                    effect_kind = monster_effect.monster_effect_kind
                    self.duel.ask_kind = effect_kind
                    self.duel.ask_det = monster_effect_unwrap.monster_effect
                    return -1

                else:
                    monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 17:
                duel.log_turn += log_tmp
                duel.log += log_tmp
                effect_kind = self.get_pac_effect_kind()
                if effect_kind is None:
                    effect_kind = monster_effect.monster_effect_kind
                move_to = self.move_from_monster_simple(effect_kind)
                log_tmp = self.write_log(monster_effect.log,user,move_to)

                if move_to is not None:
                    self.move_to_monster(move_to,effect_kind)
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 1:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                effect_kind = self.get_pac_effect_kind()
                if effect_kind is None:
                    effect_kind = monster_effect.monster_effect_kind
                move_to = self.move_from_monster(effect_kind)

                if move_to is not None:
                    self.move_to_monster(move_to,effect_kind)
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 7:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.move_phase()
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 8:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.change_turn()
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 2:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.change_variable()
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 9:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                effect_kind = monster_effect.monster_effect_kind
                self.change_monster_variable(monster_effect.monster_effect.monster_effect,effect_kind)
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 10:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.shuffle()
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 11:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.clear()
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 12:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.raise_by_monster_effect()
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 13:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.change_appointment()
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 14:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                monster_effect_text = json.loads(monster_effect.monster_effect.monster_effect)
                timing = Timing.objects.get(id=int(monster_effect_text["move_to_timing"]));
                self.change_timing(timing.id)
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 19:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                timing = duel.timing.next_timing
                duel.timing = timing
                if duel.timing is None:
                    self.timing_mess = {}
                monster_effect= monster_effect.monster_effect_next

            elif monster_effect_unwrap.monster_effect_val == 18:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.move_effect_variable_to_timing(0)
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 21:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.play_music(monster_effect.monster_effect.monster_effect)
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 22:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.win_the_game(2)
                monster_effect= monster_effect.monster_effect_next
            elif monster_effect_unwrap.monster_effect_val == 23:
                log_tmp = self.write_log(monster_effect.log,user)
                duel.log_turn += log_tmp
                duel.log += log_tmp
                self.lose_the_game(2)
                monster_effect= monster_effect.monster_effect_next
        return 0
    def invoke_monster_effect(self,monster_effect,decks,graves,kinds):
        duel = self.duel
        trigger_info = self.get_trigger_monster()
        chain_user = json.loads(duel.chain_user)
        user = chain_user[str(duel.chain-1)]
        if trigger_info is None:
            trigger_det = None
            trigger_place = None
            trigger_deck_id = 0
            trigger_x =0
            trigger_y = 0
            trigger_det_from = None
            trigger_place_from = None
            trigger_deck_id_from = 0
            trigger_from_x =0
            trigger_from_y = 0
        if not self.check_invoke_monster_effect(trigger_det,user,kinds,trigger_place,trigger_deck_id,trigger_x,trigger_y,1,trigger_det_from,trigger_place_from,trigger_deck_id_from,trigger_from_x,trigger_from_y):
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next is not None:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)




        monster_effect_unwrap = monster_effect.monster_effect
        if monster_effect_unwrap.monster_effect_val == 0:
            monster_effect_condition = json.loads(monster_effect.monster_effect.monster_condition)
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            if self.check_monster_effect_condition(monster_effect_condition):

                if monster_effect.pac :
                    return self.push_pac(monster_effect.pac)
                else:
                    if monster_effect.monster_effect_next is not None:
                        return monster_effect.monster_effect_next
                    else:
                        return self.pop_pac(user)
            else:
                if monster_effect.pac2:
                    return self.push_pac(monster_effect.pac2)
                else:
                    if monster_effect.monster_effect_next2 is None:
                        return self.pop_pac2(user)
                    else:
                        return monster_effect.monster_effect_next2

        elif monster_effect_unwrap.monster_effect_val == 5 or monster_effect_unwrap.monster_effect_val == 4 or monster_effect_unwrap.monster_effect_val == 3:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            if(self.duel.ask > 0):
                effect_kind = monster_effect.monster_effect_kind
                if self.duel.in_pac != "[]":
                    pac = json.loads(self.duel.in_pac)
                    pac_id = pac.pop()
                    pac = PacWrapper.objects.get(id=pac_id)
                    if pac.monster_effect_kind != "":
                        effect_kind = pac.monster_effect_kind
                self.duel.ask_kind = effect_kind
                self.duel.ask_det = monster_effect_unwrap.monster_effect
                return -1

            else:
                if monster_effect.pac :
                    return self.push_pac(monster_effect.pac)
                else:
                    if monster_effect.monster_effect_next is not None:
                        return monster_effect.monster_effect_next
                    else:
                        return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 17:
            effect_kind = self.get_pac_effect_kind()
            if effect_kind is None:
                effect_kind = monster_effect.monster_effect_kind
            move_to = self.move_from_monster_simple(effect_kind)
            data ={}
            data["monsters"] = move_to
            if move_to == []:
                pass
            else:
                log_tmp = self.write_log(monster_effect.log,user,data)
                duel.log_turn += log_tmp
                duel.log += log_tmp

            if move_to is not None:
                self.move_to_monster(move_to,effect_kind)
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 1:
            effect_kind = self.get_pac_effect_kind()
            if effect_kind is None:
                effect_kind = monster_effect.monster_effect_kind
            move_to = self.move_from_monster(effect_kind)
            data ={}
            data["monsters"] = move_to
            if move_to == []:
                pass
            else:
                log_tmp = self.write_log(monster_effect.log,user,data)
                duel.log_turn += log_tmp
                duel.log += log_tmp

            if move_to is not None:
                self.move_to_monster(move_to,effect_kind)
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 7:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.move_phase()
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 8:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.change_turn()
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 2:
            change_val = self.change_variable()
            data ={}
            data["val"] = change_val
            log_tmp = self.write_log(monster_effect.log,user,data)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 9:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            effect_kind = monster_effect.monster_effect_kind
            self.change_monster_variable(monster_effect.monster_effect.monster_effect,effect_kind)
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 10:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.shuffle()
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 11:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.clear()
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 12:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.raise_by_monster_effect()
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 13:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.change_appointment()
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 14:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            monster_effect_text = json.loads(monster_effect.monster_effect.monster_effect)
            timing = Timing.objects.get(id=int(monster_effect_text["move_to_timing"]));
            self.change_timing(timing.id)
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 19:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            if duel.timing is not None:
                timing = duel.timing.next_timing
                duel.timing = timing
            if duel.timing is None:
                self.timing_mess = {}
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)

        elif monster_effect_unwrap.monster_effect_val == 18:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.move_effect_variable_to_timing(0)
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
        elif monster_effect_unwrap.monster_effect_val == 21:
            log_tmp = self.write_log(monster_effect.log,user)
            duel.log_turn += log_tmp
            duel.log += log_tmp
            self.play_music(monster_effect.monster_effect.monster_effect)
            if monster_effect.pac :
                return self.push_pac(monster_effect.pac)
            else:
                if monster_effect.monster_effect_next:
                    return monster_effect.monster_effect_next
                else:
                    return self.pop_pac(user)
    def write_log(self,log_text,user,data=None):
        if log_text == "":
            return ""
        while 1:
            log_calc = re.search("\(.*?\)",log_text)
            if log_calc is None:
                break
            dummy = log_calc.group()
            dummy = dummy[1:-1]
            if dummy == "@":
                tmp_log = self.get_name_monster_all(data["monsters"])
            elif dummy == "*":
                tmp_log = str(data["val"])
            elif dummy[0] != "/":
                tmp_log = self.get_name_all(dummy,1)
            elif dummy[1] == "1":
                if user == 1:
                    tmp_log = self.duel.user_1.first_name
                else:
                    tmp_log = self.duel.user_2.first_name
            elif dummy[1] == "2":
                if user == 1:
                    tmp_log = self.duel.user_2.first_name
                else:
                    tmp_log = self.duel.user_1.first_name
            log_text = log_text.replace(log_calc.group(),tmp_log)


        return log_text+"\n"

    def raise_by_monster_effect(self):
        duel = self.duel
        chain_det = json.loads(self.duel.chain_det)
        chain_user = json.loads(duel.chain_user)
        effect_user = chain_user[str(duel.chain-1)]
        monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        monster_effect = monster_effect_wrapper.monster_effect
        monster_effect_text = json.loads(monster_effect.monster_effect)
        trigger_waitings = json.loads(duel.trigger_waiting)
        for monster_effect_det in monster_effect_text:
            trigger = Trigger.objects.get(id=monster_effect_det["trigger"]["0"])
            tmp = {}
            tmp["monster"] = ""
            tmp["move_from"] = None
            tmp["trigger"] = monster_effect_det["trigger"]["0"]
            tmp["priority"] = trigger.priority
            tmp["mine_or_other"] =1
            tmp["user"] = effect_user
            tmp["place"] = ""
            tmp["deck_id"] = ""
            tmp["place_from"] = ""
            tmp["deck_id_from"] = ""
            tmp["x"] = 0
            tmp["y"] = 0
            tmp["from_x"] = 0
            tmp["from_y"] = 0
            trigger_waitings.append(tmp)
        duel.trigger_waiting = json.dumps(trigger_waitings)
    def move_phase(self):
        duel = self.duel
        room_number = self.room_number
        chain_det = json.loads(self.duel.chain_det)
        monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        monster_effect = monster_effect_wrapper.monster_effect
        monster_effect_text = json.loads(monster_effect.monster_effect)
        duel.phase = Phase.objects.get(id=int(monster_effect_text["move_to_phase"]));
    def move_effect_variable_to_timing(self,cost =0):
        duel = self.duel
        room_number = self.room_number
        cost = self.cost
        cost = cost[str(int(duel.chain-1))]
        tmp = self.mess
        tmp = tmp[str(int(duel.chain-1))]
        chain_det = json.loads(self.duel.chain_det)
        tmp2 = self.timing_mess
        monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        monster_effect = monster_effect_wrapper.monster_effect
        monster_effect_text = json.loads(monster_effect.monster_effect)
        from_val_name = monster_effect_text["org_val"]
        to_val_name = monster_effect_text["val"]
        if from_val_name[0] != "~":
            if not from_val_name in tmp:
                return
            org_val = tmp[from_val_name]
        else:
            if not from_val_name[1:] in cost:
                return
            org_val = cost[from_val_name[1:]]
        tmp2[to_val_name] = org_val
        self.timing_mess = tmp2
    def change_turn(self):
        duel = self.duel
        room_number = self.room_number
        chain_det = json.loads(self.duel.chain_det)
        if duel.user_turn == 1:
            duel.user_turn =2
            duel.log_turn = duel.user_2.first_name +"のターン\n"
            duel.log += duel.log_turn
        elif duel.user_turn == 2:
            duel.user_turn =1
            duel.log_turn = duel.user_1.first_name +"のターン\n"
            duel.log += duel.log_turn
        duel.appoint = duel.user_turn
    def change_appointment(self):
        duel = self.duel
        room_number = self.room_number
        if duel.appoint== 1:
            duel.appoint =2
        elif duel.appoint == 2:
            duel.appoint =1
    def change_timing(self,timing_id):
        duel = self.duel
        if timing_id ==0:
            duel.timing = None
        else:
            duel.timing = Timing.objects.get(id = timing_id)

    def change_variable(self):
        duel = self.duel
        room_number = self.room_number
        chain_det = json.loads(self.duel.chain_det)
        chain_user = json.loads(self.duel.chain_user)
        user = chain_user[str(duel.chain-1)]
        monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        monster_effect = monster_effect_wrapper.monster_effect
        monster_effect_text = json.loads(monster_effect.monster_effect)
        variable_id = monster_effect_text["variable_name"].split("_")
        mine_or_other = int(variable_id[2])
        variable_id = variable_id[1]
        variable = json.loads(duel.global_variable)
        change_val = self.calculate_boland(monster_effect_text["variable_change_val"])
        if mine_or_other == 0:
            if(monster_effect_text["variable_change_how"] == 0):
                variable[str(variable_id)]["value"]+= change_val
            elif(monster_effect_text["variable_change_how"] == 1):
                variable[str(variable_id)]["value"]-= change_val
            elif(monster_effect_text["variable_change_how"] == 2):
                variable[str(variable_id)]["value"]= change_val
        elif (mine_or_other == 1 and user == 1) or (mine_or_other == 2 and user == 2) :
            if(monster_effect_text["variable_change_how"] == 0):
                variable[str(variable_id)]["1_value"]+= change_val
            elif(monster_effect_text["variable_change_how"] == 1):
                variable[str(variable_id)]["1_value"]-= change_val
            elif(monster_effect_text["variable_change_how"] == 2):
                variable[str(variable_id)]["1_value"]= change_val
        elif (mine_or_other == 2 and user == 1) or (mine_or_other == 1 and user == 2) :
            if(monster_effect_text["variable_change_how"] == 0):
                variable[str(variable_id)]["2_value"]+= change_val
            elif(monster_effect_text["variable_change_how"] == 1):
                variable[str(variable_id)]["2_value"]-= change_val
            elif(monster_effect_text["variable_change_how"] == 2):
                variable[str(variable_id)]["2_value"]= change_val
        duel.global_variable = json.dumps(variable)
        return change_val

    def change_monster_variable(self,monster_effect,effect_kind,cost =0):
        duel = self.duel
        chain_user = json.loads(duel.chain_user)
        if cost == 0:
            chain_user = chain_user[str(duel.chain-1)]
        else:
            chain_user = chain_user[str(duel.chain)]
        room_number = self.room_number
        field = self.field
        monster_effect = json.loads(monster_effect)
        monster_effect_monster = monster_effect["monster"]
        for monster_effect_det in monster_effect_monster:
            if not "as_monster_condition" in monster_effect_det:
                continue
            if monster_effect_det["as_monster_condition"] == "":
               continue
            as_monsters = monster_effect_det["as_monster_condition"]
            if not isinstance(as_monsters,list):
                tmp_monster = []
                tmp_monster.append(as_monsters)
                as_monsters = tmp_monster
            for as_monster in as_monsters:
                if as_monster[0] == "~":
                    tmp = self.cost
                    tmp = tmp[str(int(duel.chain))]
                    place1 = tmp[as_monster[1:]]
                elif as_monster[0] == "%":
                    tmp = self.timing_mess
                    place1 = tmp[as_monster[1:]]
                else:
                    tmp = self.mess
                    tmp = tmp[str(int(duel.chain-1))]
                    place1 = tmp[as_monster]
                for place2 in place1:
                    place = place2["place"]
                    if place == "field":
                        x = int(place2["x"])
                        y = int(place2["y"])
                        field = self.field
                        if cost ==0:
                            if( "place_id" in place2):
                                place_id = place2["place_id"]
                                if(field[x][y]["det"]["place_unique_id"] != place_id):
                                    return "error"
                                if self.check_not_effected(field[x][y]["det"],chain_user,effect_kind,"field",0,x,y,1):
                                    continue;
                                for index in range(len(monster_effect["monster_variable_change_how"])):
                                    variable_name = monster_effect["monster_variable_change_name"][index]
                                    if monster_effect["monster_variable_change_how"][index] == 0:
                                        field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index]) + int( field[x][y]["det"]["variables"][variable_name]["value"] ))
                                    elif monster_effect["monster_variable_change_how"][index] == 1:
                                        field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index]) - int( field[x][y]["det"]["variables"][variable_name]["value"] ))
                                    elif monster_effect["monster_variable_change_how"][index] == 2:
                                        field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index]) )
                                self.field = field
                                continue;
                        else:
                            place_id = place2["place_id"]
                            if(field[x][y]["det"]["place_unique_id"] != place_id):
                                return "error"
                            cost_result = self.cost_result
                            if not "variable" in cost_result:
                                cost_result["variable"] = {}

                            if not "field" in cost_result["variable"]:
                                cost_result["variable"]["field"] = []
                            for index in range(len(monster_effect["monster_variable_change_how"])):
                                cost_result_tmp = {}
                                cost_result_tmp["x"]= x
                                cost_result_tmp["y"]= y
                                cost_result_tmp["place_id"]= place_id
                                cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index]
                                cost_result_tmp["change_variable_val"]= monster_effect["monster_variable_change_val"][index]
                                cost_result_tmp["change_variable_how"]= monster_effect["monster_variable_change_how"][index]
                                cost_result["variable"]["field"].append(cost_result_tmp)
                            self.cost_result = cost_result
                            continue;

                    mine_or_other = place2["mine_or_other"]
                    user = place2["user"]
                    deck_id = place2["deck_id"]
                    place_id = place2["place_id"]
                    if (self.user == chain_user and  mine_or_other == "1") or (chain_user != self.user and mine_or_other == "2"):
                        mine_or_other = "1"
                    elif (self.user != chain_user and  mine_or_other == "1") or (chain_user == self.user and mine_or_other == "2"):
                        mine_or_other = "2"
                    else:
                        mine_or_other = "3"
                    if place == "deck":
                        if mine_or_other == "1":
                            tmp = self.decks[deck_id]["mydeck"]
                        elif mine_or_other == "2":
                            tmp = self.decks[deck_id]["otherdeck"]
                        else:
                            tmp = self.decks[deck_id]["commondeck"]
                        user_decks = tmp
                        for index in range(len(user_decks)):
                            if place_id== user_decks[index]["place_unique_id"]:
                                if cost == 0:
                                    effect_flag = False
                                    if not self.check_not_effected(user_decks[index],chain_user,effect_kind,"deck",deck_id,0,0,1):
                                        for index2 in range(len(monster_effect["monster_variable_change_how"])):
                                            variable_name = monster_effect["monster_variable_change_name"][index2]
                                            if monster_effect["monster_variable_change_how"][index2] == 0:
                                                user_decks[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_decks[index]["variables"][variable_name]["value"] ))
                                            elif monster_effect["monster_variable_change_how"][index2] == 1:
                                                user_decks[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_decks[index]["variables"][variable_name]["value"] ))
                                            elif monster_effect["monster_variable_change_how"][index2] == 2:
                                                user_decks[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]))
                                    if mine_or_other == "1":
                                        self.decks[deck_id]["mydeck"] =user_decks
                                    elif mine_or_other == "2":
                                        self.decks[deck_id]["otherdeck"] =user_decks
                                    else:
                                        self.decks[deck_id]["commondeck"] =user_decks
                                else:
                                    cost_result = self.cost_result
                                    if not "variable" in cost_result:
                                        cost_result["variable"] = {}
                                    if not "deck" in cost_result["variable"]:
                                        cost_result["variable"]["deck"] = []
                                    cost_result_tmp = {}
                                    cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index]
                                    cost_result_tmp["change_variable_val"]= monster_effect["monster_variable_change_val"][index]
                                    cost_result_tmp["change_variable_how"]= monster_effect["monster_variable_change_how"][index]
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result_tmp["deck_id"]= deck_id
                                    cost_result_tmp["user"]= int(mine_or_other)
                                    cost_result["variable"]["deck"].append(cost_result_tmp)
                                    self.cost_result = cost_result


                    if place == "grave":
                        if mine_or_other == "1":
                            tmp = self.graves[deck_id]["mygrave"]
                        elif mine_or_other == "2":
                            tmp = self.graves[deck_id]["othergrave"]
                        else:
                            tmp = self.graves[deck_id]["commongrave"]
                        user_graves = tmp
                        for index in range(len(user_graves)):
                            if place_id== user_graves[index]["place_unique_id"]:
                                if cost == 0:
                                    effect_flag = False
                                    if not self.check_not_effected(user_graves[index],chain_user,effect_kind,"grave",deck_id,0,0,mine_or_other):
                                        for index2 in range(len(monster_effect["monster_variable_change_how"])):
                                            variable_name = monster_effect["monster_variable_change_name"][index2]
                                            if monster_effect["monster_variable_change_how"][index2] == 0:
                                                user_graves[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_graves[index]["variables"][variable_name]["value"] ))
                                            elif monster_effect["monster_variable_change_how"][index2] == 1:
                                                user_graves[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_graves[index]["variables"][variable_name]["value"] ))
                                            elif monster_effect["monster_variable_change_how"][index2] == 2:
                                                user_graves[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]))
                                    if mine_or_other == "1":
                                        self.graves[deck_id]["mygrave"] =user_graves
                                    elif mine_or_other == "2":
                                        self.graves[deck_id]["othergrave"] =user_graves
                                    else:
                                        self.graves[deck_id]["commongrave"] =user_graves
                                else:
                                    cost_result = self.cost_result
                                    if not "variable" in cost_result:
                                        cost_result["variable"] = {}
                                    if not "grave" in cost_result["variable"]:
                                        cost_result["variable"]["grave"] = []
                                    cost_result_tmp = {}
                                    cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index]
                                    cost_result_tmp["change_variable_val"]= monster_effect["monster_variable_change_val"][index]
                                    cost_result_tmp["change_variable_how"]= monster_effect["monster_variable_change_how"][index]
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result_tmp["grave_id"]= deck_id
                                    cost_result_tmp["user"]= int(mine_or_other)
                                    cost_result["variable"]["grave"].append(cost_result_tmp)
                                    self.cost_result = cost_result
                    if place == "hand":
                        if mine_or_other == "1":
                            tmp = self.hands[deck_id]["myhand"]
                        elif mine_or_other == "2":
                            tmp = self.hands[deck_id]["otherhand"]
                        else:
                            tmp = self.hands[deck_id]["commonhand"]
                        user_hands = tmp
                        for index in range(len(user_hands)):
                            if place_id== user_hands[index]["place_unique_id"]:
                                if cost == 0:
                                    effect_flag = False
                                    if not self.check_not_effected(user_hands[index],chain_user,effect_kind,"hand",deck_id,0,0,mine_or_other):
                                        for index2 in range(len(monster_effect["monster_variable_change_how"])):
                                            variable_name = monster_effect["monster_variable_change_name"][index2]
                                            if monster_effect["monster_variable_change_how"][index2] == 0:
                                                user_hands[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_hands[index]["variables"][variable_name]["value"] ))
                                            elif monster_effect["monster_variable_change_how"][index2] == 1:
                                                user_hands[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_hands[index]["variables"][variable_name]["value"] ))
                                            elif monster_effect["monster_variable_change_how"][index2] == 2:
                                                user_hands[index]["variables"][variable_name]["value"] = int(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]))
                                    if mine_or_other == "1":
                                        self.hands[deck_id]["myhand"] =user_hands
                                    elif mine_or_other == "2":
                                        self.hands[deck_id]["otherhand"] =user_hands
                                    else:
                                        self.hands[deck_id]["commonhand"] =user_hands
                                else:
                                    cost_result = self.cost_result
                                    if not "variable" in cost_result:
                                        cost_result["variable"] = {}
                                    if not "hand" in cost_result["variable"]:
                                        cost_result["variable"]["hand"] = []
                                    cost_result_tmp = {}
                                    cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index]
                                    cost_result_tmp["change_variable_val"]= monster_effect["monster_variable_change_val"][index]
                                    cost_result_tmp["change_variable_how"]= monster_effect["monster_variable_change_how"][index]
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result_tmp["hand_id"]= deck_id
                                    cost_result_tmp["user"]= int(mine_or_other)
                                    cost_result["variable"]["hand"].append(cost_result_tmp)
                                    self.cost_result = cost_result


        field=self.field
        for monster_effect_det2 in monster_effect_monster:
            monster_effect_det = monster_effect_det2["monster"]
            field_tmp = []
            tmp_deck = None
            for place in monster_effect_det["place"]:
                place_tmp = place["det"].split("_")
                deck_id = int(place_tmp[1])
                if(place_tmp[0] == "deck" ):
                    chain_user = json.loads(duel.chain_user)
                    effect_user = chain_user[str(duel.chain-1)]
                    if tmp_deck is None:
                        if((place_tmp[2] == "1" and effect_user ==1) or (place_tmp[2] == "2" and effect_user !=1)):
                            mine_or_other = 1
                        elif((place_tmp[2] == "1" and effect_user !=1) or (place_tmp[2] == "2" and effect_user ==1)):
                            mine_or_other = 2
                        else:
                            mine_or_other = 3
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "1" and effect_user !=self.user) or (place_tmp[2] == "2" and effect_user ==self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if mine_or_other2 == 1:
                            tmp_deck = self.get_deck_with_effect(self.decks[deck_id]["mydeck"],monster_effect_det,effect_kind,exclude,effect_user,"deck",deck_id,0,0,mine_or_other3)
                            org_deck = self.decks[deck_id]["mydeck"]
                        elif mine_or_other2 == 2:
                            tmp_deck = self.get_deck_with_effect(self.decks[deck_id]["otherdeck"],monster_effect_det,effect_kind,exclude,effect_user,"deck",deck_id,0,0,mine_or_other3)
                            org_deck = self.decks[deck_id]["otherdeck"]
                        else:
                            tmp_deck = self.get_deck_with_effect(self.decks[deck_id]["commondeck"],monster_effect_det,effect_kind,exclude,effect_user,"deck",deck_id,0,0,mine_or_other3)
                            org_deck = self.decks[deck_id]["commondeck"]
                        user_decks = org_deck

                    if not tmp_deck:
                        return
                    if "move_how" not in monster_effect_det:
                        for index3 in range(len(user_decks)):
                            effect_flag = False
                            if not self.check_not_effected(user_decks[index3],chain_user,effect_kind,"deck",deck_id,0,0,mine_or_other):
                                for index2 in range(len(user_decks[index3]["variables"])):
                                    variable_name = monster_effect["monster_variable_change_name"][index2]
                                    if cost == 0:
                                        if monster_effect["monster_variable_change_how"][index2] == 0:
                                            user_decks[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_decks[index3]["variables"][variable_name]["value"] ))
                                        if monster_effect["monster_variable_change_how"][index2] == 1:
                                            user_decks[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_decks[index3]["variables"][variable_name]["value"] ))
                                        if monster_effect["monster_variable_change_how"][index2] == 2:
                                            user_decks[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) )
                                    else:
                                         cost_result = self.cost_result
                                         cost_result_tmp = {}
                                         cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index2]
                                         cost_result_tmp["change_variable_val"]=monster_effect["monster_variable_change_val"][index2]
                                         cost_result_tmp["change_variable_how"]=monster_effect["monster_variable_change_how"][index2]
                                         cost_result_tmp["place_id"]= user_decks[index3]["place_unique_id"]
                                         cost_result_tmp["user"]= int(place_tmp[2])
                                         cost_result_tmp["deck_id"]= deck_id
                                         cost_result["variable"]["deck"].append(cost_result_tmp)
                                         self.cost_result =cost_result
                        if cost == 0:
                            if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                                mine_or_other2 = 1
                            elif((place_tmp[2] == "1" and effect_user !=self.user) or (place_tmp[2] == "2" and effect_user ==self.user)):
                                mine_or_other2 = 2
                            else:
                                mine_or_other2 =3
                            if mine_or_other2 == 1:
                                self.decks[deck_id]["mydeck"] =user_decks
                            elif mine_or_other2 == 2:
                                self.decks[deck_id]["otherdeck"] =user_decks
                            else:
                                self.decks[deck_id]["commondeck"] =user_decks
                        continue
                    elif(monster_effect_det["move_how"] == 0):
                        range_i = tmp_deck[0]
                        del tmp_deck[0]
                        for tmpdecktmp in range(len(tmp_deck)):
                            tmp_deck[tmpdecktmp]-=1
                    elif(monster_effect_det["move_how"] == 1):
                        range_i = tmp_deck[len(tmp_deck)-1]
                        tmp_deck.pop()
                    else:
                        rand_i = random.randrange(len(tmp))
                        range_i = tmp[rand_i]
                        tmp_deck.pop(rand_i)
                        for tmpdecktmp in range(len(tmp_deck)-rand_i):
                            tmp_deck[tmpdecktmp+rand_i]-=1
                    for index2 in range(len(user_decks[range_i]["variables"])):
                        effect_flag = False
                        if not self.check_not_effected(user_decks[range_i],chain_user,effect_kind,"deck",deck_id,0,0,mine_or_other):
                            for index2 in monster_effect["monster_variable_change_how"]:
                                variable_name = monster_effect["monster_variable_change_name"][index2]
                                if cost == 0:
                                    if monster_effect["monster_variable_change_how"][index2] == 0:
                                        user_decks[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_decks[range_i]["variables"][variable_name]["value"] ))
                                    if monster_effect["monster_variable_change_how"][index2] == 1:
                                        user_decks[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_decks[range_i]["variables"][variable_name]["value"] ))
                                    if monster_effect["monster_variable_change_how"][index2] == 2:
                                        user_decks[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) )
                                else:
                                    cost_result = self.cost_result
                                    cost_result_tmp = {}
                                    cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index2]
                                    cost_result_tmp["change_variable_val"]=monster_effect["monster_variable_change_val"][index2]
                                    cost_result_tmp["change_variable_how"]=monster_effect["monster_variable_change_how"][index2]
                                    cost_result_tmp["place_id"]= user_decks[range_i]["place_unique_id"]
                                    cost_result_tmp["user"]= int(place_tmp[2])
                                    cost_result_tmp["deck_id"]= deck_id
                                    cost_result["variable"]["deck"].append(cost_result_tmp)
                                    self.cost_result = cost_result

                    if cost ==0:
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "1" and effect_user !=self.user) or (place_tmp[2] == "2" and effect_user ==self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if mine_or_other2 == 1:
                            self.decks[deck_id]["mydeck"] =user_decks
                        elif mine_or_other2 == 2:
                            self.decks[deck_id]["otherdeck"] =user_decks
                        else:
                            self.decks[deck_id]["commondeck"] =user_decks
                elif(place_tmp[0] == "grave" ):
                    chain_user = json.loads(duel.chain_user)
                    effect_user = chain_user[str(duel.chain-1)]
                    if tmp_deck is None:
                        if((place_tmp[2] == "1" and effect_user ==1) or (place_tmp[2] == "2" and effect_user !=1)):
                            mine_or_other = 1
                        elif((place_tmp[2] == "1" and effect_user !=1) or (place_tmp[2] == "2" and effect_user ==1)):
                            mine_or_other = 2
                        else:
                            mine_or_other = 3
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if mine_or_other2 == 1:
                            tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["mygrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                            org_grave = self.graves[deck_id]["mygrave"]
                        elif mine_or_other2 == 2:
                            tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["othergrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                            org_grave = self.graves[deck_id]["othergrave"]
                        else:
                            tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["commongrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                            org_grave = self.graves[deck_id]["commongrave"]
                        user_graves = org_grave
                    if not tmp:
                        return None
                    if "move_how" not in monster_effect_det:
                        for index3 in range(len(user_graves)):
                            effect_flag = False
                            if not self.check_not_effected(user_graves[index3],chain_user,effect_kind,"grave",deck_id,0,0,mine_or_other):
                                for index2 in range(len(monster_effect["monster_variable_change_how"])):
                                    variable_name = monster_effect["monster_variable_change_name"][index2]
                                    if cost == 0:
                                        if monster_effect["monster_variable_change_how"][index2] == 0:
                                            user_graves[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_graves[index3]["variables"][variable_name]["value"] ))
                                        if monster_effect["monster_variable_change_how"][index2] == 1:
                                            user_graves[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_graves[index3]["variables"][variable_name]["value"] ))
                                        if monster_effect["monster_variable_change_how"][index2] == 2:
                                            user_graves[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) )
                                    else:
                                        cost_result = self.cost_result
                                        cost_result_tmp = {}
                                        cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index4]
                                        cost_result_tmp["change_variable_val"]=monster_effect["monster_variable_change_val"][index4]
                                        cost_result_tmp["change_variable_how"]=monster_effect["monster_variable_change_how"][index4]
                                        cost_result_tmp["place_id"]= user_graves[index3]["place_unique_id"]
                                        cost_result_tmp["user"]= int(place_tmp[2])
                                        cost_result_tmp["grave_id"]= deck_id
                                        cost_result["variable"]["deck"].append(cost_result_tmp)
                                        self.cost_result =cost_result
                    if cost == 0:
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if mine_or_other2 == 1:
                            self.decks[deck_id]["mydeck"] =user_decks
                        elif mine_or_other2 == 2:
                            self.decks[deck_id]["otherdeck"] =user_decks
                        else:
                            self.decks[deck_id]["commondeck"] =user_decks
                        if mine_or_other2 == 1:
                            self.graves[deck_id]["mygrave"] =user_graves
                        elif mine_or_other2 == 2:
                            self.graves[deck_id]["othergrave"] =user_graves
                        else:
                            self.graves[deck_id]["commongrave"] =user_graves
                        continue
                    elif(monster_effect_det["move_how"] == 0):
                        range_i = tmp_deck[0]
                        del tmp_deck[0]
                        for tmpdecktmp in range(len(tmp_deck)):
                            tmp_deck[tmpdecktmp]-=1
                    elif(monster_effect_det["move_how"] == 1):
                        range_i = tmp_deck[len(tmp_deck)-1]
                        tmp_deck.pop()
                    else:
                        rand_i = random.randrange(len(tmp))
                        range_i = tmp[rand_i]
                        tmp_deck.pop(rand_i)
                        for tmpdecktmp in range(len(tmp_deck)-rand_i):
                            tmp_deck[tmpdecktmp+rand_i]-=1
                    effect_flag = False
                    if not self.check_not_effected(user_graves[range_i],chain_user,effect_kind,"grave",deck_id,0,0,mine_or_other):
                        for index2 in range(len(monster_effect["monster_variable_change_how"])):
                            variable_name = monster_effect["monster_variable_change_name"][index2]
                            if cost ==0:
                                if monster_effect["monster_variable_change_how"][index2] == 0:
                                    user_graves[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_graves[range_i]["variables"][variable_name]["value"] ))
                                if monster_effect["monster_variable_change_how"][index2] == 1:
                                    user_graves[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_graves[range_i]["variables"][variable_name]["value"] ))
                                if monster_effect["monster_variable_change_how"][index2] == 2:
                                    user_graves[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) )
                            else:
                                cost_result = self.cost_result
                                cost_result_tmp = {}
                                cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index2]
                                cost_result_tmp["change_variable_val"]=monster_effect["monster_variable_change_val"][index2]
                                cost_result_tmp["change_variable_how"]=monster_effect["monster_variable_change_how"][index2]
                                cost_result_tmp["place_id"]= user_graves[range_i]["place_unique_id"]
                                cost_result_tmp["user"]= int(place_tmp[2])
                                cost_result_tmp["grave_id"]= deck_id
                                cost_result["variable"]["grave"].append(cost_result_tmp)
                                self.cost_result = cost_result
                    if cost == 0:
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if mine_or_other2 == 1:
                            self.graves[deck_id]["mygrave"] =user_graves
                        elif mine_or_other2 == 2:
                            self.graves[deck_id]["othergrave"] =user_graves
                        else:
                            self.graves[deck_id]["commongrave"] =user_graves
                elif(place_tmp[0] == "hand" ):
                    chain_user = json.loads(duel.chain_user)
                    effect_user = chain_user[str(duel.chain-1)]
                    if tmp_deck is None:
                        if((place_tmp[2] == "1" and effect_user ==1) or (place_tmp[2] == "2" and effect_user !=1)):
                            mine_or_other = 1
                        elif((place_tmp[2] == "1" and effect_user !=1) or (place_tmp[2] == "2" and effect_user ==1)):
                            mine_or_other = 2
                        else:
                            mine_or_other = 3
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if mine_or_other2 == 1:
                            tmp_deck = self.get_hand_with_effect(self.hands[deck_id]["myhand"],monster_effect_det,effect_kind,exclude,effect_user,"hand",deck_id,0,0,mine_or_other3)
                            org_hand = self.hands[deck_id]["myhand"]
                        elif mine_or_other2 ==2:
                            tmp_deck = self.get_hand_with_effect(self.hands[deck_id]["otherhand"],monster_effect_det,effect_kind,exclude,effect_user,"hand",deck_id,0,0,mine_or_other3)
                            org_hand = self.hands[deck_id]["otherhand"]
                        else:
                            tmp_deck = self.get_hand_with_effect(self.hands[deck_id]["commonhand"],monster_effect_det,effect_kind,exclude,effect_user,"hand",deck_id,0,0,mine_or_other3)
                            org_hand = self.hands[deck_id]["commonhand"]
                        user_hands = tmp
                    if not user_hands:
                        return None
                    if "move_how" not in monster_effect_det:
                        for index3 in range(len(user_hands)):
                            effect_flag = False
                            if not self.check_not_effected(user_hands[index3],chain_user,effect_kind,"hand",deck_id,0,0,mine_or_other):
                                for index2 in range(len(monster_effect["monster_variable_change_how"])):
                                    variable_name = monster_effect["monster_variable_change_name"][index2]
                                    if cost == 0:
                                        if(user_hands[index3]["variables"][variable_name]["name"] == monster_effect["monster_variable_change_name"][index2]):
                                            if monster_effect["monster_variable_change_how"][index2] == 0:
                                                user_hands[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_hands[index3]["variables"][variable_name]["value"] ))
                                            if monster_effect["monster_variable_change_how"][index2] == 1:
                                                user_hands[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_hands[index3]["variables"][variable_name]["value"] ))
                                            if monster_effect[0]["monster_variable_change_how"] == 2:
                                                user_hands[index3]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) )
                                    else:
                                        cost_result = self.cost_result
                                        cost_result_tmp = {}
                                        cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index4]
                                        cost_result_tmp["change_variable_val"]=monster_effect["monster_variable_change_val"][index4]
                                        cost_result_tmp["change_variable_how"]=monster_effect["monster_variable_change_how"][index4]
                                        cost_result_tmp["place_id"]= user_hands[index3]["place_unique_id"]
                                        cost_result_tmp["user"]= int(place_tmp[2])
                                        cost_result_tmp["hand_id"]= deck_id
                                        cost_result["variable"]["deck"].append(cost_result_tmp)
                                        self.cost_result = cost_result
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if mine_or_other2 == 1:
                            self.hands[deck_id]["myhand"] =user_hands
                        elif mine_or_other2 == 2:
                            self.hands[deck_id]["otherhand"] =user_hands
                        else:
                            self.hands[deck_id]["commonhand"] =user_hands
                        continue
                    elif(monster_effect_det["move_how"] == 0):
                        range_i = tmp[0]
                    elif(monster_effect_det["move_how"] == 1):
                        range_i = tmp[len(tmp)-1]
                    else:
                        range_i =tmp[random.randrange(len(user_hands))]
                    effect_flag = False
                    if not self.check_not_effected(user_hands[range_i],chain_user,effect_kind,"hand",deck_id,0,0,mine_or_other):
                        for index2 in range(len(monster_effect["monster_variable_change_how"])):
                            variable_name = monster_effect["monster_variable_change_name"][index2]
                            if cost == 0:
                                if monster_effect["monster_variable_change_how"][index2] == 0:
                                    user_hands[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( user_hands[range_i]["variables"][variable_name]["value"] ))
                                if monster_effect["monster_variable_change_how"][index2] == 1:
                                    user_hands[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( user_hands[range_i]["variables"][variable_name]["value"] ))
                                if monster_effect["monster_variable_change_how"][index2] == 2:
                                    user_hands[range_i]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) )
                            else:
                                cost_result = self.cost_result
                                cost_result_tmp = {}
                                cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index2]
                                cost_result_tmp["change_variable_val"]=monster_effect["monster_variable_change_val"][index2]
                                cost_result_tmp["change_variable_how"]=monster_effect["monster_variable_change_how"][index2]
                                cost_result_tmp["place_id"]= user_graves[range_i]["place_unique_id"]
                                cost_result_tmp["user"]= int(place_tmp[2])
                                cost_result_tmp["hand_id"]= deck_id
                                cost_result["variable"]["hand"].append(cost_result_tmp)
                                self.cost_result = cost_result
                        if cost == 0:
                            if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                                mine_or_other2 = 1
                            elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                                mine_or_other2 = 2
                            else:
                                mine_or_other2 = 3
                            if mine_or_other2 == 1:
                                self.hands[deck_id]["myhand"] =user_hands
                            elif mine_or_other2 == 2:
                                self.hands[deck_id]["otherhand"] =user_hands
                            else:
                                self.hands[deck_id]["commonhand"] =user_hands
                elif(place_tmp[0] == "field" ):
                    field_tmp.append(place_tmp[1])
                    if place["and_or"] == "and":
                            continue
                    else:
                        field_tmp2 = field_tmp
                        field_tmp = []
                    chain_user = json.loads(duel.chain_user)
                    effect_user = chain_user[str(duel.chain-1)]
                    if((place_tmp[2] == "1" and effect_user ==1) or (place_tmp[2] == "2" and effect_user ==2)):
                        mine_or_other2 = 1
                    elif((place_tmp[2] == "1" and effect_user ==2) or (place_tmp[2] == "2" and effect_user ==1)):
                        mine_or_other2 = 2
                    else:
                        mine_or_other2 = 3
                    for x in range(len(field)):
                        for y in range(len(field[x])):
                            exclude = ""
                            field_kind_flag = True
                            if field[x][y]["kind"] != "":
                                tmp = field[x][y]["kind"].split("_")
                                for kind in field_tmp2:
                                    if  not kind in tmp:
                                        field_kind_flag = False
                                        break


                            if field_kind_flag == False:
                                continue
                            if field[x][y]["mine_or_other"] != mine_or_other2:
                                continue
                            if field[x][y]["det"] is None:
                                continue
                            if self.check_not_effected(field[x][y]["det"],chain_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                continue
                            if( self.validate_answer(field[x][y]["det"],monster_effect_det,exclude,duel)):
                                for index2 in range(len(monster_effect["monster_variable_change_how"])):
                                    variable_name = monster_effect["monster_variable_change_name"][index2]
                                    if cost == 0:
                                        if monster_effect["monster_variable_change_how"][index2] == 0:
                                            field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) + int( fields[x][y]["det"]["variables"][variable_name]["value"] ))
                                        if monster_effect["monster_variable_change_how"][index2] == 1:
                                            field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]) - int( fields[x][y]["det"]["variables"][variable_name]["value"] ))
                                        if monster_effect["monster_variable_change_how"][index2] == 2:
                                            field[x][y]["det"]["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect["monster_variable_change_val"][index2]))
                                    else:
                                        cost_result = self.cost_result
                                        if not "variable" in cost_result:
                                            cost_result["variable"] = {}

                                        if not "field" in cost_result["variable"]:
                                            cost_result["variable"]["field"] = []
                                        cost_result_tmp = {}
                                        cost_result_tmp["x"]= x
                                        cost_result_tmp["y"]= y
                                        cost_result_tmp["place_id"]= field[x][y]["place_unique_id"]
                                        cost_result_tmp["change_variable"]= monster_effect["monster_variable_change_name"][index2]
                                        cost_result_tmp["change_variable_val"]= monster_effect["monster_variable_change_val"][index2]
                                        cost_result_tmp["change_variable_how"]= monster_effect["monster_variable_change_how"][index2]
                                        cost_result["variable"]["field"].append(cost_result_tmp)
                                        self.cost_result = cost_result

        self.field = field
    def change_monster_variable_cost(self,cost_text,effect_kind):
        self.change_monster_variable(cost_text,effect_kind,1)

    def end_cost_shuffle(self,cost_user):
        duel = self.duel
        room_number = self.room_number
        if(self.cost_result == ''):
            return
        cost = self.cost_result
        if not "clear" in cost:
            return
        for cost_det in cost:
            for place in cost_det["place"].values():
                place_tmp = place.split("_")
                deck_id = int(place_tmp[1])
                if(place_tmp[0] == "deck" ):
                    if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                        mine_or_other2 = 1
                    elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                        mine_or_other2 = 2
                    else:
                        mine_or_other2 = 3
                    if mine_or_other2 == 1:
                        tmp = self.decks[deck_id]["mydeck"]
                    elif mine_or_other2 == 2:
                        tmp = self.decks[deck_id]["otherdeck"]
                    elif mine_or_other2 == 3:
                        tmp = self.decks[deck_id]["commondeck"]
                    user_decks = tmp
                    np.random.shuffle(user_decks)
                    if mine_or_other2 == 1:
                        self.decks[deck_id]["mydeck"] = user_decks
                    elif mine_or_other2 == 2:
                        self.decks[deck_id]["otherdeck"] = user_decks
                    elif mine_or_other2 == 3:
                        self.decks[deck_id]["commondeck"] = user_decks
                if(place_tmp[0] == "grave" ):
                    if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                        mine_or_other2 = 1
                    elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                        mine_or_other2 = 2
                    else:
                        mine_or_other2 = 3
                    if mine_or_other2 == 1:
                        tmp = self.graves[deck_id]["mygrave"]
                    elif mine_or_other2 == 2:
                        tmp = self.graves[deck_id]["othergrave"]
                    elif mine_or_other2 == 3:
                        tmp = self.graves[deck_id]["commongrave"]
                    user_graves = tmp
                    np.random.shuffle(user_graves)
                    if mine_or_other2 == 1:
                        self.graves[deck_id]["mygrave"] = user_graves
                    elif mine_or_other2 == 2:
                        self.graves[deck_id]["othergrave"] = user_graves
                    elif mine_or_other2 == 3:
                        self.graves[deck_id]["commongrave"] = user_graves
                if(place_tmp[0] == "hand" ):
                    if((place_tmp[2] == "1" and cost_user ==self.user) or (place_tmp[2] == "2" and cost_user !=self.user)):
                        mine_or_other2 = 1
                    elif((place_tmp[2] == "2" and cost_user ==self.user) or (place_tmp[2] == "1" and cost_user !=self.user)):
                        mine_or_other2 = 2
                    else:
                        mine_or_other2 = 3
                    if mine_or_other2 == 1:
                        tmp = self.hands[deck_id]["myhand"]
                    elif mine_or_other2 == 2:
                        tmp = self.hands[deck_id]["otherhand"]
                    elif mine_or_other2 == 3:
                        tmp = self.hands[deck_id]["commonhand"]
                    user_hands = tmp
                    np.random.shuffle(user_hands)
                    if place_tmp[2] == "1":
                        self.hands[deck_id]["myhand"] = user_hands
                    elif place_tmp[2] == "2":
                        self.hands[deck_id]["otherhand"] = user_hands
                    elif place_tmp[2] == "3":
                        self.hands[deck_id]["commonhand"] = user_hands
        return
    def end_cost_clear(self,cost_user):
        duel = self.duel
        room_number = self.room_number
        if(self.cost_result == ''):
            return
        cost = self.cost_result
        if not "clear" in cost:
            return
        for cost_det in cost:
            for place in cost_det["place"].values():
                place_tmp = place.split("_")
                deck_id = int(place_tmp[1])
                if((place_tmp[2] == "1" and cost_user ==self.user) or (place_tmp[2] == "2" and cost_user !=self.user)):
                    mine_or_other2 = 1
                elif((place_tmp[2] == "2" and cost_user ==self.user) or (place_tmp[2] == "1" and cost_user !=self.user)):
                    mine_or_other2 = 2
                else:
                    mine_or_other2 = 3
                if(place_tmp[0] == "deck" ):
                    if mine_or_other2 == 1:
                        tmp = self.decks[deck_id]["mydeck"]
                    elif mine_or_other2 == 2:
                        tmp = self.decks[deck_id]["otherdeck"]
                    elif mine_or_other2 == 3:
                        tmp = self.decks[deck_id]["commondeck"]
                    user_decks = tmp
                    result_user_decks = []
                    for user_deck in user_decks:
                        user_deck["flag"] =0
                        result_user_decks.append(user_deck)
                    if place_tmp[2] == "1":
                        self.decks[deck_id]["mydeck"] = user_decks
                    elif place_tmp[2] == "2":
                        self.decks[deck_id]["otherdeck"] = user_decks
                    elif place_tmp[2] == "3":
                        self.decks[deck_id]["commondeck"] = user_decks
                if(place_tmp[0] == "grave" ):
                    if mine_or_other2 == 1:
                        tmp = self.graves[deck_id]["mygrave"]
                    elif mine_or_other2 == 2:
                        tmp = self.graves[deck_id]["othergrave"]
                    elif mine_or_other2 == 3:
                        tmp = self.graves[deck_id]["commongrave"]
                    user_graves = tmp
                    result_user_graves = []
                    for user_grave in user_graves:
                        user_grave["flag"] =0
                        result_user_graves.append(user_grave)
                    if mine_or_other2 == 1:
                        self.graves[deck_id]["mygrave"] = user_graves
                    elif mine_or_other2 == 2:
                        self.graves[deck_id]["othergrave"] = user_graves
                    elif mine_or_other2 == 3:
                        self.graves[deck_id]["commongrave"] = user_graves
                if(place_tmp[0] == "hand" ):
                    if mine_or_other2 == 1:
                        tmp = self.hands[deck_id]["myhand"]
                    elif mine_or_other2 == 2:
                        tmp = self.hands[deck_id]["otherhand"]
                    elif mine_or_other2 == 3:
                        tmp = self.hands[deck_id]["commonhand"]
                    user_hands = tmp
                    result_user_hands = []
                    for user_hand in user_hands:
                        user_hand["flag"] =0
                        result_user_hands.append(user_hand)
                    if mine_or_other2 == 1:
                        self.hands[deck_id]["myhand"] = user_hands
                    elif mine_or_other2 == 2:
                        self.hands[deck_id]["otherhand"] = user_hands
                    elif mine_or_other2 == 3:
                        self.hands[deck_id]["commonhand"] = user_hands
                elif(place_tmp[0] == "field" ):
                    if((place_tmp[2] == "1" and cost_user ==1) or (place_tmp[2] == "2" and cost_user ==2)):
                        mine_or_other = 1
                    elif((place_tmp[2] == "2" and cost_user ==1) or (place_tmp[2] == "1" and cost_user ==2)):
                        mine_or_other = 2
                    else:
                        mine_or_other = 3
                    field = self.field
                    for x in range(len(field)):
                        for y in range(len(field[x])):
                            kind = field[x][y]["kind"]
                            mine_or_other_field = field[x][y]["mine_or_other"]
                            if kind.find(str(deck_id)) > -1 and mine_or_other == mine_or_other:
                                if field[x][y]["det"] is not None:
                                    field[x][y]["det"]["flag"] = 0
                    self.field = field
        return
    def clear(self):
        duel = self.duel
        room_number = self.room_number
        chain_user = json.loads(duel.chain_user)
        effect_user = chain_user[str(duel.chain-1)]
        chain_det = json.loads(self.duel.chain_det)
        monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        monster_effect = monster_effect_wrapper.monster_effect
        monster_effect_text = json.loads(monster_effect.monster_effect)
        for monster_effect_det in monster_effect_text:
            for place in monster_effect_det["place"].values():
                place_tmp = place.split("_")
                deck_id = int(place_tmp[1])
                if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                    mine_or_other2 = 1
                elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                    mine_or_other2 = 2
                else:
                    mine_or_other2 = 3
                if(place_tmp[0] == "deck" ):
                    if mine_or_other2 ==1:
                        tmp = self.decks[deck_id]["mydeck"]
                    elif mine_or_other2 ==2:
                        tmp = self.decks[deck_id]["otherdeck"]
                    elif mine_or_other2 ==3:
                        tmp = self.decks[deck_id]["commondeck"]
                    user_decks = tmp
                    result_user_decks = []
                    for user_deck in user_decks:
                        user_deck["flag"] = 0
                        result_user_decks.append(user_deck)
                    if mine_or_other2 ==1:
                        self.decks[deck_id]["mydeck"] = user_decks
                    elif mine_or_other2 ==2:
                        self.decks[deck_id]["otherdeck"] = user_decks
                    elif mine_or_other2 ==3:
                        self.decks[deck_id]["commondeck"] = user_decks
                elif(place_tmp[0] == "grave" ):
                    if mine_or_other2 ==1:
                        tmp = self.graves[deck_id]["mygrave"]
                    elif mine_or_other2 ==2:
                        tmp = self.graves[deck_id]["othergrave"]
                    elif mine_or_other2 ==3:
                        tmp = self.graves[deck_id]["commongrave"]
                    user_graves = tmp
                    result_user_graves = []
                    for user_grave in user_graves:
                        user_grave["flag"] = 0
                        result_user_graves.append(user_grave)
                    if mine_or_other2 ==1:
                        self.graves[deck_id]["mygrave"] = user_graves
                    elif mine_or_other2 ==2:
                        self.graves[deck_id]["othergrave"] = user_graves
                    elif mine_or_other2 ==3:
                        self.graves[deck_id]["commongrave"] = user_graves
                elif(place_tmp[0] == "hand" ):
                    if mine_or_other2 ==1:
                        tmp = self.hands[deck_id]["myhand"]
                    elif mine_or_other2 ==2:
                        tmp = self.hands[deck_id]["otherhand"]
                    elif mine_or_other2 ==3:
                        tmp = self.hands[deck_id]["commonhand"]
                    user_hands = tmp
                    result_user_hands = []
                    for user_hand in user_hands:
                        user_hand["flag"] = 0
                        result_user_hands.append(user_hand)
                    if mine_or_other2 ==1:
                        self.hands[deck_id]["myhand"] = user_hands
                    elif mine_or_other2 ==2:
                        self.hands[deck_id]["otherhand"] = user_hands
                    elif mine_or_other2 ==3:
                        self.hands[deck_id]["commonhand"] = user_hands
                elif(place_tmp[0] == "field" ):
                    field = self.field
                    for x in range(len(field)):
                        for y in range(len(field[x])):
                            kind = field[x][y]["kind"]
                            mine_or_other_field = field[x][y]["mine_or_other"]
                            if kind.find(str(deck_id)) > -1 and mine_or_other == mine_or_other:
                                if field[x][y]["det"] is not None:
                                    field[x][y]["det"]["flag"] = 0
                    field = self.field
        return
    def shuffle(self):
        duel = self.duel
        room_number = self.room_number
        chain_user = json.loads(duel.chain_user)
        effect_user = chain_user[str(duel.chain-1)]
        chain_det = json.loads(self.duel.chain_det)
        monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        monster_effect = monster_effect_wrapper.monster_effect
        monster_effect_text = json.loads(monster_effect.monster_effect)
        for monster_effect_det in monster_effect_text:
            for place in monster_effect_det["place"].values():
                place_tmp = place.split("_")
                deck_id = int(place_tmp[1])
                if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                    mine_or_other2 = 1
                elif((place_tmp[2] == "2" and effect_user ==self.user) or (place_tmp[2] == "1" and effect_user !=self.user)):
                    mine_or_other2 = 2
                else:
                    mine_or_other2 = 3
                if(place_tmp[0] == "deck" ):
                    if mine_or_other2 ==1:
                        tmp = self.decks[deck_id]["mydeck"]
                    elif mine_or_other2 ==2:
                        tmp = self.decks[deck_id]["otherdeck"]
                    elif mine_or_other2 ==3:
                        tmp = self.decks[deck_id]["commondeck"]
                    user_decks = tmp
                    np.random.shuffle(user_decks)
                    if place_tmp[2] == "1":
                        self.decks[deck_id]["mydeck"] = user_decks
                    elif place_tmp[2] == "2":
                        self.decks[deck_id]["otherdeck"] = user_decks
                    elif place_tmp[2] == "0":
                        self.decks[deck_id]["commondeck"] = user_decks
                elif(place_tmp[0] == "grave" ):
                    if mine_or_other2 ==1:
                        tmp = self.graves[deck_id]["mygrave"]
                    elif mine_or_other2 ==2:
                        tmp = self.graves[deck_id]["othergrave"]
                    elif mine_or_other2 ==3:
                        tmp = self.graves[deck_id]["commongrave"]
                    user_graves = tmp
                    np.random.shuffle(user_graves)
                    if mine_or_other2 ==1:
                        self.graves[deck_id]["mygrave"] = user_graves
                    elif mine_or_other2 ==2:
                        self.graves[deck_id]["othergrave"] = user_graves
                    elif mine_or_other2 ==3:
                        self.graves[deck_id]["commongrave"] = user_graves
                elif(place_tmp[0] == "hand" ):
                    if mine_or_other2 ==1:
                        tmp = self.hands[deck_id]["myhand"]
                    elif mine_or_other2 ==2:
                        tmp = self.hands[deck_id]["otherhand"]
                    elif mine_or_other2 ==3:
                        tmp = self.hands[deck_id]["commonhand"]
                    user_hands = tmp
                    np.random.shuffle(user_hands)
                    if mine_or_other2 ==1:
                        self.hands[deck_id]["myhand"] = user_hands
                    elif mine_or_other2 ==2:
                        self.hands[deck_id]["otherhand"] = user_hands
                    elif mine_or_other2 ==3:
                        self.hands[deck_id]["commonhand"] = user_hands
        return

    def clear_cost(self):
        duel = self.duel
        room_number = self.room_number
        cost_det = self.cost_det
        cost_wrapper = CostWrapper.objects.get(id = cost_det)
        cost = cost_wrapper.cost
        cost_text = json.loads(cost.cost)
        for cost_det in cost_text:
            for place in cost_det["place"].values():
                cost_result = self.cost_result
                if not "clear" in cost_result:
                    cost_result["clear"] = []

                    cost_result_tmp = {}
                    cost_result_tmp["place"]= place
                    cost_result["clear"].append(cost_result_tmp)
                    self.cost_result = cost_result
        return
    def shuffle_cost(self):
        duel = self.duel
        room_number = self.room_number
        cost_det = self.cost_det
        cost_wrapper = CostWrapper.objects.get(id = cost_det)
        cost = cost_wrapper.cost
        cost_text = json.loads(cost.cost)
        for cost_det in cost_text:
            for place in cost_det["place"].values():
                cost_result = self.cost_result
                if not "shuffle" in cost_result:
                    cost_result["shuffle"] = []

                    cost_result_tmp = {}
                    cost_result_tmp["place"]= place
                    cost_result["shuffle"].append(cost_result_tmp)
                    self.cost_result = cost_result
        return


    def move_from_monster_simple_cost(self,monster_effect_kind):
        return self.move_from_monster_simple(monster_effect_kind,1)
    def move_from_monster_simple(self,effect_kind,cost=0):
        duel = self.duel
        room_number = self.room_number
        chain_det = json.loads(self.duel.chain_det)
        chain_user = json.loads(duel.chain_user)
        effect_user = chain_user[str(duel.chain-1)]
        if cost == 0:
            monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
            monster_effect = monster_effect_wrapper.monster_effect
            monster_effect_text = json.loads(monster_effect.monster_effect)
            monster_effect_text_monster = monster_effect_text["monster"]
        else:
            cost_wrapper = CostWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
            cost = cost_wrapper.cost
            monster_effect_text = json.loads(cost.cost)
            monster_effect_text_monster = monster_effect_text["monster"]
        return_value = []
        exclude = monster_effect_text["exclude"]

        user_decks2 = None
        user_graves2 = None
        user_hands2 = None
        for monster_effect_det in monster_effect_text_monster:
            if "as_monster_condition" in monster_effect_det and monster_effect_det["as_monster_condition"] != "":
                as_monster_effects = monster_effect_det["as_monster_condition"]
                as_monster_effects = as_monster_effects.split(",")
                for as_monster_effect in as_monster_effects:
                    tmp = self.mess
                    cost_tmp = self.cost
                    timing_tmp = self.timing_mess
                    if str(duel.chain-1) not in tmp:
                        tmp[str(duel.chain-1)] = {}
                    if as_monster_effect[0]== "~":
                        if as_monster_effect[1:] not in cost_tmp[str(duel.chain)]:
                            continue
                        else:
                            place1 = cost_tmp[str(duel.chain)][as_monster_effect[1:]]
                    elif as_monster_effect[0]== "%":
                        if as_monster_effect[1:] not in timing_tmp:
                            continue
                        else:
                            place1 = timing_tmp[as_monster_effect[1:]]
                    elif(as_monster_effect not in tmp[str(duel.chain-1)]):
                        continue
                    else:
                        place1 = tmp[str(duel.chain-1)][as_monster_effect]
                    for place2 in place1:
                        place = place2["place"]
                        if place == "field":
                            x = int(place2["x"])
                            y = int(place2["y"])
                            field = self.field
                            if( "place_id" in place2):
                                place_id = place2["place_id"]
                                if cost == 0:
                                    if(field[x][y]["det"]["place_unique_id"] != place_id):
                                        return "error"
                                    effect_flag = False
                                    if self.check_not_effected(field[x][y]["det"],effect_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                        continue
                                    field[x][y]["det"]["kind"] = effect_kind
                                    field[x][y]["det"]["user"] = int(field[x][y]["mine_or_other"])
                                    field[x][y]["det"]["user_det"] = effect_user
                                    return_tmp={}
                                    return_tmp["x"] = x
                                    return_tmp["y"] = y
                                    return_tmp["place"] = "field"
                                    return_tmp["deck_id"] = 0
                                    return_tmp["det"] = self.copy_monster_from_field(field[x][y]["det"])
                                    return_value.append(return_tmp)
                                    field[x][y]["det"] = None
                                    self.field = field
                                    continue
                                else:
                                    if self.check_not_effected(field[x][y]["det"],effect_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                        continue
                                    cost_result = self.cost_result
                                    if not "remove" in cost_result:
                                        cost_result["remove"] = {}

                                    if not "field" in cost_result["remove"]:
                                        cost_result["remove"]["field"] = []
                                    cost_result_tmp = {}
                                    cost_result_tmp["x"]= x
                                    cost_result_tmp["y"]= y
                                    cost_result_tmp["place_id"]= place_id

                                    cost_result["remove"]["field"].append(cost_result_tmp)
                                    self.cost_result = cost_result
                                    continue

                        mine_or_other2=int( place2["mine_or_other"]  )
                        mine_or_other3 = mine_or_other2
                        if self.user == 2:
                            if mine_or_other2 == 1:
                                mine_or_other2 = 2
                            elif mine_or_other2 == 2:
                                mine_or_other2 = 1
                        deck_id = place2["deck_id"]
                        place_id = place2["place_id"]
                        if place == "deck":
                            if mine_or_other2 ==1:
                                deck = self.decks[deck_id]["mydeck"]
                            elif mine_or_other2 ==2:
                                deck = self.decks[deck_id]["otherdeck"]
                            elif mine_or_other2 ==3:
                                deck = self.decks[deck_id]["commondeck"]
                            user_decks = deck
                            for user_deck in user_decks:
                                if place_id== user_deck["place_unique_id"]:
                                    effect_flag = False
                                    if not self.check_not_effected(user_deck,effect_user,effect_kind,"deck",deck_id,0,0,mine_or_other3):
                                        if cost == 0:
                                            user_decks.remove(user_deck);
                                            user_deck["kind"] = effect_kind
                                            user_deck["user"] = mine_or_other3
                                            user_deck["user_det"] = effect_user
                                            return_tmp={}
                                            return_tmp["x"] = 0
                                            return_tmp["y"] = 0
                                            return_tmp["place"] = "deck"
                                            return_tmp["deck_id"] = deck_id
                                            return_tmp["mine_or_other"] = mine_or_other3
                                            return_tmp["det"] = self.copy_monster_from_deck(user_deck)
                                            return_value.append(return_tmp)
                                            if mine_or_other2 ==1:
                                                self.decks[deck_id]["mydeck"] = user_decks
                                            elif mine_or_other2 ==2:
                                                self.decks[deck_id]["otherdeck"]= user_decks
                                            elif mine_or_other2 ==3:
                                                self.decks[deck_id]["commondeck"] = user_decks
                                        else:
                                            if not "remove" in cost_result:
                                                cost_result["remove"] = {}
                                            if not "deck" in cost_result["remove"]:
                                                cost_result["remove"]["deck"] = []
                                                place_id=user_deck["place_unique_id"]
                                                cost_result_tmp = {}
                                                cost_result_tmp["place_id"]= place_id
                                                cost_result_tmp["user"]=mine_or_other3
                                                cost_result_tmp["deck_id"]= deck_id
                                                cost_result["remove"]["deck"].append(cost_result_tmp)
                                                self.cost_result = cost_result
                                                return_tmp = {}
                                                return_tmp["x"] = 0
                                                return_tmp["y"] = 0
                                                return_tmp["place"] = "deck"
                                                return_tmp["deck_id"] = deck_id
                                                return_tmp["det"] = self.copy_monster_from_deck(user_deck)
                                                return_value.append(return_tmp)
                        if place == "grave":
                            if mine_or_other2 ==1:
                                grave = self.graves[deck_id]["mygrave"]
                            elif mine_or_other2 ==2:
                                grave = self.graves[deck_id]["othergrave"]
                            elif mine_or_other2 ==3:
                                grave = self.graves[deck_id]["commongrave"]
                            user_graves = grave
                            for user_grave in user_graves:
                                if place_id== user_grave["place_unique_id"]:
                                    effect_flag = False
                                    if not self.check_not_effected(user_grave,effect_user,effect_kind,"grave",deck_id,0,0,mine_or_other3):
                                        if cost == 0:
                                            user_graves.remove(user_grave);
                                            user_grave["kind"] = effect_kind
                                            user_grave["user"] = mine_or_other3
                                            user_grave["user_det"] = effect_user
                                            return_tmp = {}
                                            return_tmp["x"] = 0
                                            return_tmp["y"] = 0
                                            return_tmp["place"] = "grave"
                                            return_tmp["deck_id"] = deck_id
                                            return_tmp["mine_or_other"] = mine_or_other3
                                            return_tmp["det"] = self.copy_monster_from_grave(user_grave)
                                            return_value.append( return_tmp)
                                            if mine_or_other2 ==1:
                                                self.graves[deck_id]["mygrave"] = user_graves
                                            elif mine_or_other2 ==2:
                                                self.graves[deck_id]["othergrave"]= user_graves
                                            elif mine_or_other2 ==3:
                                                self.graves[deck_id]["commongrave"] = user_graves
                                        else:
                                            if not "remove" in cost_result:
                                                cost_result["remove"] = {}
                                            if not "grave" in cost_result["remove"]:
                                                cost_result["remove"]["grave"] = []
                                            place_id=user_grave["place_unique_id"]
                                            cost_result_tmp = {}
                                            cost_result_tmp["place_id"]= place_id
                                            cost_result_tmp["user"]=mine_or_other3
                                            cost_result_tmp["user_det"]=self.duel.cost_user
                                            cost_result_tmp["grave_id"]= deck_id
                                            cost_result["remove"]["grave"].append(cost_result_tmp)
                                            self.cost_result =cost_result
                                            return_tmp = {}
                                            return_tmp["x"] = 0
                                            return_tmp["y"] = 0
                                            return_tmp["place"] = "grave"
                                            return_tmp["mine_or_other"] = mine_or_other3
                                            return_tmp["deck_id"] = deck_id
                                            return_tmp["det"] = self.copy_monster_from_grave(user_grave)
                                            return_value.append( return_tmp)
                        if place == "hand":
                            if mine_or_other2 ==1:
                                hand = self.hands[deck_id]["myhand"]
                            elif mine_or_other2 ==2:
                                hand = self.hands[deck_id]["otherhand"]
                            elif mine_or_other2 ==3:
                                hand = self.hands[deck_id]["commonhand"]
                            user_hands = hand
                            for user_hand in user_hands:
                                if place_id== user_hand["place_unique_id"]:
                                    if not self.check_not_effected(user_hand,effect_user,effect_kind,"hand",deck_id,0,0,mine_or_other3):
                                        if cost == 0:
                                            user_hands.remove(user_hand);
                                            return_tmp = {}
                                            return_tmp["x"] = 0
                                            return_tmp["y"] = 0
                                            return_tmp["place"] = "hand"
                                            return_tmp["mine_or_other"] = mine_or_other3
                                            return_tmp["deck_id"] = deck_id
                                            return_tmp["det"] = self.copy_monster_from_hand(user_hand)
                                            return_value.append( return_tmp)
                                            if mine_or_other2 ==1:
                                                self.hands[deck_id]["myhand"] = user_hands
                                            elif mine_or_other2 ==2:
                                                self.hands[deck_id]["otherhand"]= user_hands
                                            elif mine_or_other2 ==3:
                                                self.hands[deck_id]["commonhand"] = user_hands
                                        else:
                                            if not "remove" in cost_result:
                                                cost_result["remove"] = {}
                                            if not "hand" in cost_result["remove"]:
                                                cost_result["remove"]["hand"] = []
                                            place_id=user_hand["place_unique_id"]
                                            cost_result_tmp = {}
                                            cost_result_tmp["place_id"]= place_id
                                            cost_result_tmp["user"]=mine_or_other3
                                            cost_result_tmp["user_det"]=self.duel.cost_user
                                            cost_result_tmp["hand_id"]= deck_id
                                            cost_result["remove"]["hand"].append(cost_result_tmp)
                                            self.cost_result =cost_result
                                            return_tmp = {}
                                            return_tmp["x"] = 0
                                            return_tmp["y"] = 0
                                            return_tmp["place"] = "hand"
                                            return_tmp["deck_id"] = deck_id
                                            return_tmp["mine_or_other"] = mine_or_other3
                                            return_tmp["det"] = self.copy_monster_from_hand(user_hand)
                                            return_value.append( return_tmp)

            place_array_tmp = []
            for place in monster_effect_det["monster"]["place"]:
                place_tmp = place["det"].split("_")
                if place["det"] == "":
                    continue
                if place["and_or"] != "" and place_tmp[0] == "field":
                    tmptmp["and_or"]=place["and_or"]
                    tmptmp["det"]=place["det"]
                    place_array_tmp.append(tmptmp)
                    continue
                else:
                    place_array = place_array_tmp
                    place_array_tmp = []
                deck_id = int(place_tmp[1])
                tmp_deck = None
                for tmp_i in range(self.calculate_boland(monster_effect_det["min_equation_number"])):
                    tmp_i2 = 0
                    if monster_effect_text["field_x"]:
                        field = self.field
                        for str_x in monster_effect_text["field_x"]:
                            x  = int(str_x)
                            y = int(monster_effect_text["field_y"][tmp_i2])
                            if cost == 0:
                                if(field[x][y]["det"] is not None):
                                    effect_flag = False
                                    if not self.check_not_effected(field[x][y]["det"],effect_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                        det = field[x][y]["det"].copy();
                                        field[x][y]["det"] = None
                                        det =self.copy_monster_from_field(det)
                                        self.field = field
                                        det["kind"] = effect_kind
                                        det["user"] = int(field[x][y]["mine_or_other"])
                                        det["user_det"] = effect_user
                                else:
                                    field[x][y]["det"] = None
                                    self.field = field
                                    det = None
                                return_tmp = {}
                                return_tmp["x"] = x
                                return_tmp["y"] = y
                                return_tmp["mine_or_other"] = field[x][y]["mine_or_other"]
                                return_tmp["place"] = "field"
                                return_tmp["deck_id"] = 0
                                return_tmp["det"] = det
                                return_value.append( return_tmp)
                            else:
                                cost_result_tmp = {}
                                cost_result_tmp["x"]= x
                                cost_result_tmp["y"]= y
                                cost_result_tmp["place_id"]= place_id
                                cost_result["remove"]["field"].append(cost_result_tmp)
                                self.cost_result = cost_result
                                det =self.copy_monster_from_field(det)
                                return_tmp = {}
                                return_tmp["x"] = x
                                return_tmp["y"] = y
                                return_tmp["mine_or_other"] = field[x][y]["mine_or_other"]
                                return_tmp["place"] = "field"
                                return_tmp["deck_id"] = 0
                                return_tmp["det"] = det
                                return_value.append( return_tmp)
                        continue
                    if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                        mine_or_other2 = 1
                    elif((place_tmp[2] == "1" and effect_user !=self.user) or (place_tmp[2] == "2" and effect_user ==self.user)):
                        mine_or_other2 = 2
                    else:
                        mine_or_other2 = 3
                    if self.user ==1:
                        mine_or_other3 = mine_or_other2
                    else:
                        if mine_or_other2 == 1:
                            mine_or_other3 = 2
                        elif mine_or_other2 == 2:
                            mine_or_other3 = 1
                        else:
                            mine_or_other3 = 3
                    if(place_tmp[0] == "deck" ):
                        if user_decks2 is None:
                            if mine_or_other2 ==1:
                                deck = self.decks[deck_id]["mydeck"]
                            elif mine_or_other2 ==2:
                                deck = self.decks[deck_id]["otherdeck"]
                            elif mine_or_other2 ==3:
                                deck = self.decks[deck_id]["commondeck"]
                            user_decks2 = deck
                        if len(user_decks2) == 0:
                            return return_value
                        if cost == 0:
                            if(monster_effect_text["move_how"] == 0):
                                user_deck =self.copy_monster_from_deck(user_decks2[0])
                                del user_decks2[0]
                            elif(monster_effect_text["move_how"] == 1):
                                user_deck =self.copy_monster_from_deck(user_decks2[-1])
                                user_decks2.pop()
                            else:
                                range_i = random.randrange(len(user_decks2))
                                user_deck =self.copy_monster_from_deck(user_decks2[range_i])
                                user_decks2.pop(range_i)
                            if mine_or_other2 ==1:
                                self.decks[deck_id]["mydeck"] = user_decks2
                            elif mine_or_other2 ==2:
                                self.decks[deck_id]["otherdeck"] = user_decks2
                            elif mine_or_other2 ==3:
                                self.decks[deck_id]["commondeck"] = user_decks2
                            user_deck["kind"] = effect_kind
                            user_deck["user"] = mine_or_other3
                            user_deck["user_det"] = effect_user
                            return_tmp = {}
                            return_tmp["x"] = 0
                            return_tmp["y"] = 0
                            return_tmp["place"] = "deck"
                            return_tmp["mine_or_other"] = mine_or_other3
                            return_tmp["deck_id"] = deck_id
                            return_tmp["det"] = user_deck
                            return_value.append( return_tmp)
                        else:
                            cost_result = self.cost_result
                            if(monster_effect_text["move_how"] == 0):
                                user_deck =self.copy_monster_from_deck(user_decks2[0])
                                del user_decks2[0]
                            elif(monster_effect_text["move_how"] == 1):
                                user_deck =self.copy_monster_from_deck(-1)
                                user_decks2.pop()
                            else:
                                range_i = random.randrange(len(user_decks2))
                                user_deck =self.copy_monster_from_deck(user_decks2[range_i])
                                user_decks2.pop(range_i)
                            if not "remove" in cost_result:
                                cost_result["remove"] = {}
                            if not "deck" in cost_result["remove"]:
                                cost_result["remove"]["deck"] = []
                            place_id=user_deck["place_unique_id"]
                            cost_result_tmp = {}
                            cost_result_tmp["place_id"]= place_id
                            cost_result_tmp["user"]=mine_or_other3
                            cost_result_tmp["user_det"]=self.duel.cost_user
                            cost_result_tmp["deck_id"]= deck_id
                            cost_result["remove"]["deck"].append(cost_result_tmp)
                            self.cost_result = cost_result
                            return_tmp = {}
                            return_tmp["x"] = 0
                            return_tmp["y"] = 0
                            return_tmp["place"] = "deck"
                            return_tmp["deck_id"] = deck_id
                            return_tmp["mine_or_other"] = mine_or_other3
                            return_tmp["det"] = user_deck
                            return_value.append( return_tmp)
                    elif(place_tmp[0] == "grave" ):
                        if user_graves2 is None:
                            if mine_or_other2 ==1:
                                tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["mygrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                                grave = self.graves[deck_id]["mygrave"]
                            elif mine_or_other2 ==2:
                                tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["othergrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                                grave = self.graves[deck_id]["othergrave"]
                            elif mine_or_other2 ==3:
                                tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["commongrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                                grave = self.graves[deck_id]["commongrave"]

                            user_graves2 = grave
                        if len(user_graves2) == 0:
                            return return_value
                        if cost == 0:
                            if(monster_effect_text["move_how"] == 0):
                                user_grave =self.copy_monster_from_grave(user_graves2[0])
                                del user_graves2[0]
                            elif(monster_effect_text["move_how"] == 1):
                                user_grave =self.copy_monster_from_grave(user_graves2[-1])
                                user_graves2.pop()
                            else:
                                range_i = random.randrange(len(user_graves2))
                                user_grave =self.copy_monster_from_grave(user_graves2[range_i])
                                user_graves2.pop(range_i)
                            if mine_or_other2 ==1:
                                self.graves[deck_id]["mygrave"] = user_graves2
                            elif mine_or_other2 ==2:
                                self.graves[deck_id]["othergrave"] = user_graves2
                            elif mine_or_other2 ==3:
                                self.graves[deck_id]["commongrave"] = user_graves2
                            user_grave["kind"] = effect_kind
                            user_grave["user"] = mine_or_other3
                            user_grave["user_det"] = effect_user
                            return_tmp = {}
                            return_tmp["x"] = 0
                            return_tmp["y"] = 0
                            return_tmp["place"] = "grave"
                            return_tmp["deck_id"] = deck_id
                            return_tmp["det"] = user_grave
                            return_tmp["mine_or_other"] = mine_or_other3
                            return_value.append( return_tmp)
                        else:
                            cost_result = self.cost_result
                            if(monster_effect_text["move_how"] == 0):
                                user_grave =self.copy_monster_from_grave(user_graves2[0])
                                del user_graves2[0]
                            elif(monster_effect_text["move_how"] == 1):
                                user_grave =self.copy_monster_from_grave(user_graves2[-1])
                                user_graves2.pop()
                            else:
                                range_i = random.randrange(len(user_graves2))
                                user_graves2.pop(range_i)
                            if not "remove" in cost_result:
                                cost_result["remove"] = {}
                            if not "grave" in cost_result["remove"]:
                                cost_result["remove"]["grave"] = []
                            place_id=user_grave["place_unique_id"]
                            cost_result_tmp = {}
                            cost_result_tmp["place_id"]= place_id
                            cost_result_tmp["user"]=mine_or_other3
                            cost_result_tmp["user_det"]=self.duel.cost_user
                            cost_result_tmp["grave_id"]= deck_id
                            cost_result["remove"]["grave"].append(cost_result_tmp)
                            self.cost_result = cost_result
                            return_tmp = {}
                            return_tmp["x"] = 0
                            return_tmp["y"] = 0
                            return_tmp["place"] = "grave"
                            return_tmp["deck_id"] = deck_id
                            return_tmp["det"] = user_grave
                            return_tmp["mine_or_other"] = mine_or_other3
                            return_value.append( return_tmp)
                    elif(place_tmp[0] == "hand" ):
                        if user_hands2 is None:
                            if mine_or_other2 ==1:
                                hand = self.hands[deck_id]["myhand"]
                            elif mine_or_other2 ==2:
                                hand = self.hands[deck_id]["otherhand"]
                            elif mine_or_other2 ==3:
                                hand = self.hands[deck_id]["commonhand"]
                            user_hands2 = hand
                        if len(user_hands2) == 0:
                            return return_value
                        if cost == 0:
                            if(monster_effect_text["move_how"] == 0):
                                user_hand =self.copy_monster_from_hand(user_hands2[0])
                                del user_hands2[0]
                            elif(monster_effect_text["move_how"] == 1):
                                user_hand =self.copy_monster_from_hand(user_hands2[-1])
                                user_hands2.pop()
                            else:
                                range_i =random.randrange(len(user_hands2))
                                user_hand =self.copy_monster_from_hand(user_hands2[range_i])
                                user_hands2.pop(range_i)
                            if mine_or_other2 ==1:
                                self.hands[deck_id]["myhand"] = user_hands2
                            elif mine_or_other2 ==2:
                                self.hands[deck_id]["otherhand"] = user_hands2
                            elif mine_or_other2 ==3:
                                self.hands[deck_id]["commonhand"] = user_hands2
                            user_hand["kind"] = effect_kind
                            user_hand["user"] = mine_or_other3
                            user_hand["user_det"] = effect_user
                            return_tmp = {}
                            return_tmp["x"] = 0
                            return_tmp["y"] = 0
                            return_tmp["place"] = "hand"
                            return_tmp["deck_id"] = deck_id
                            return_tmp["det"] = user_hand
                            return_tmp["mine_or_other"] = mine_or_other3
                            return_value.append( return_tmp)
                        else:
                            cost_result = self.cost_result
                            if(monster_effect_text["move_how"] == 0):
                                user_hand =self.copy_monster_from_hand(user_hands2[0])
                                del user_hands2[0]
                            elif(monster_effect_text["move_how"] == 1):
                                user_hand =self.copy_monster_from_hand(user_hands2[-1])
                                user_hands2.pop(-1)
                                tmp_deck.pop()
                            else:
                                range_i =random.randrange(len(user_hands2))

                                user_hand =self.copy_monster_from_hand(user_hands2[range_i])
                                user_hands2.pop(range_i)
                            if not "remove" in cost_result:
                                cost_result["remove"] = {}
                            if not "hand" in cost_result["remove"]:
                                cost_result["remove"]["hand"] = []
                            place_id=user_hand["place_unique_id"]
                            cost_result_tmp= {}
                            cost_result_tmp["place_id"]= place_id
                            cost_result_tmp["user"]=mine_or_other3
                            cost_result_tmp["user_det"]=self.duel.cost_user
                            cost_result_tmp["hand_id"]= deck_id
                            cost_result["remove"]["hand"].append(cost_result_tmp)
                            self.cost_result = cost_result
                            return_tmp = {}
                            return_tmp["x"] = 0
                            return_tmp["y"] = 0
                            return_tmp["place"] = "hand"
                            return_tmp["deck_id"] = deck_id
                            return_tmp["det"] = user_hand
                            return_tmp["mine_or_other"] = mine_or_other3
                            return_value.append( return_tmp)
                    elif(place_tmp[0] == "field" ):
                        field_size = FieldSize.objects.get(id=1);
                        field = self.field
                        flag_field_place = True
                        current_and_or = "and"
                        for x in range(field_size.field_x):
                            for y in range(field_size.field_y):
                                for place_tmp2 in place_array:
                                    and_or = place_tmp2["and_or"]
                                    det = place_tmp2["det"]
                                    splitted_det = det.split("_")
                                    kind = splitted_det[1]
                                    if  field[x][y]["kind"] != "":
                                        tmp=  field[x][y]["kind"].split("_")
                                    else:
                                        tmp=  []
                                    if(current_and_or == "and"):
                                        if kind in tmp:
                                            if flag_field_place == True:
                                                flag_field_place = True
                                        else:
                                            flag_field_place = False
                                    elif(current_and_or == "or"):
                                        if(kind in tmp):
                                            flag_field_place = True
                                        else:
                                            if flag_field_place == False:
                                                flag_field_place = False
                                    mine_or_other = int(splitted_det[2])
                                    current_and_or = and_or
                                if flag_field_place == False:
                                    continue
                                if mine_or_other == 1 and user == 1 or  mine_or_other == 2 and user == 2:
                                    mine_or_other = 1
                                elif mine_or_other == 1 and user == 2 or  mine_or_other == 2 and user == 1:
                                    mine_or_other = 2
                                else:
                                    mine_or_other = 3
                                if field[x][y]["mine_or_other"] != mine_or_other:
                                    continue
                                effect_flag = False
                                if not self.check_not_effected(field[x][y]["det"],effect_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                    continue

                                if not self.validate_answer(field[x][y]["det"],monster_effect_det["monster"],exclude,duel):

                                    continue
                                if cost == 0:
                                    if(field[x][y]["det"] is not None):
                                        det = field[x][y]["det"].copy();
                                        field[x][y]["det"] = None
                                        det =self.copy_monster_from_field(det)
                                        self.field = field
                                        det["kind"] = effect_kind
                                        det["user"] = int(field[x][y]["mine_or_other"])
                                        det["user_det"] = effect_user
                                    else:
                                        field[x][y]["det"] = None
                                        self.field = field
                                        det = None
                                    return_tmp = {}
                                    return_tmp["x"] = x
                                    return_tmp["y"] = y
                                    return_tmp["place"] = "field"
                                    return_tmp["deck_id"] = 0
                                    return_tmp["det"] =det
                                    return_tmp["mine_or_other"] = field[x][y]["mine_or_other"]
                                    return_value.append( return_tmp)
                                else:
                                    cost_result_tmp = {}
                                    cost_result_tmp["x"]= x
                                    cost_result_tmp["y"]= y
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result["remove"]["field"].append(cost_result_tmp)
                                    self.cost_result = cost_result
                                    det =self.copy_monster_from_field(det)
                                    return_tmp = {}
                                    return_tmp["x"] = x
                                    return_tmp["y"] = y
                                    return_tmp["place"] = "field"
                                    return_tmp["deck_id"] = 0
                                    return_tmp["det"] =det
                                    return_tmp["mine_or_other"] = field[x][y]["mine_or_other"]
                                    return_value.append( return_tmp)

        return return_value
    def move_from_monster_cost(self,cost_kind):
        return self.move_from_monster(self,cost_kind,1)
    def move_from_monster(self,effect_kind,cost=0):
        duel = self.duel
        room_number = self.room_number
        chain_det = json.loads(self.duel.chain_det)
        chain_user = json.loads(duel.chain_user)
        effect_user = chain_user[str(duel.chain-1)]
        if cost == 0:
            pprint(effect_user)
            monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
            pprint(monster_effect_wrapper)
            monster_effect = monster_effect_wrapper.monster_effect
            monster_effect_text = json.loads(monster_effect.monster_effect)
            monster_effect_text_monster = monster_effect_text["monster"]
        else:
            cost_wrapper = CostWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
            cost = cost_wrapper.cost
            monster_effect_text = json.loads(cost.cost)
            monster_effect_text_monster = monster_effect_text["monster"]
        return_value = []
        exclude = monster_effect_text["exclude"]
        for monster_effect_det in monster_effect_text_monster:
                if "as_monster_condition" in monster_effect_det and monster_effect_det["as_monster_condition"] != "":
                    as_monster_effects = monster_effect_det["as_monster_condition"]
                    as_monster_effects = as_monster_effects.split(",")
                    for as_monster_effect in as_monster_effects:
                        tmp_mess = self.mess
                        cost_tmp = self.cost
                        timing_tmp = self.timing_mess
                        if as_monster_effect[0]== "~":
                            if as_monster_effect[1:] not in cost_tmp[str(duel.chain)]:
                                continue
                            else:
                                place1 = cost_tmp[str(duel.chain)][as_monster_effect[1:]]
                        elif as_monster_effect[0]== "%":
                            if as_monster_effect[1:] not in timing_tmp:
                                continue
                            else:
                                place1 = timing_tmp[as_monster_effect[1:]]
                        elif(as_monster_effect not in tmp_mess[str(duel.chain-1)]):
                            continue
                        else:
                            place1 = tmp_mess[str(duel.chain-1)][as_monster_effect]
                        for place2 in place1:
                            place = place2["place"]
                            if place == "field":
                                x = int(place2["x"])
                                y = int(place2["y"])
                                field = self.field
                                if( "place_id" in place2):
                                    place_id = place2["place_id"]
                                    if cost == 0:
                                        if(field[x][y]["det"]["place_unique_id"] != place_id):
                                            return "error"
                                        effect_flag = False
                                        if self.check_not_effected(field[x][y]["det"],effect_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                            continue
                                        field[x][y]["det"]["kind"] = effect_kind
                                        field[x][y]["det"]["user"] = int(field[x][y]["mine_or_other"])
                                        field[x][y]["det"]["user_det"] = effect_user
                                        return_tmp={}
                                        return_tmp["x"] = x
                                        return_tmp["y"] = y
                                        return_tmp["place"] = "field"
                                        return_tmp["deck_id"] = 0
                                        return_tmp["det"] = self.copy_monster_from_field(field[x][y]["det"])
                                        return_value.append(return_tmp)
                                        field[x][y]["det"] = None
                                        self.field = field
                                        continue
                                    else:
                                        cost_result = self.cost_result
                                        if not "remove" in cost_result:
                                            cost_result["remove"] = {}
        
                                        if not "field" in cost_result["remove"]:
                                            cost_result["remove"]["field"] = []
                                        cost_result_tmp = {}
                                        cost_result_tmp["x"]= x
                                        cost_result_tmp["y"]= y
                                        cost_result_tmp["place_id"]= place_id
        
                                        cost_result["remove"]["field"].append(cost_result_tmp)
                                        self.cost_result = cost_result
                                        continue

                            mine_or_other2=int( place2["mine_or_other"]  )
                            mine_or_other3 = mine_or_other2
                            user=int( place2["user"]  )
                            if self.user == 2:
                                if mine_or_other2 == 1:
                                    mine_or_other2 = 2
                                elif mine_or_other2 == 2:
                                    mine_or_other2 = 1
                                else:
                                    pass
                            deck_id = place2["deck_id"]
                            place_id = place2["place_id"]
                            if place == "deck":
                                if mine_or_other2 ==1:
                                    deck = self.decks[deck_id]["mydeck"]
                                elif mine_or_other2 ==2:
                                    deck = self.decks[deck_id]["otherdeck"]
                                elif mine_or_other2 ==3:
                                    deck = self.decks[deck_id]["commondeck"]
                                user_decks = deck
                                for user_deck in user_decks:
                                    if place_id== user_deck["place_unique_id"]:
                                        if not self.check_not_effected(user_deck,effect_user,effect_kind,"deck",deck_id,0,0,mine_or_other3):
                                            if cost == 0:
                                                user_decks.remove(user_deck);
                                                user_deck["kind"] = effect_kind
                                                user_deck["user"] = mine_or_other2
                                                user_deck["user_det"] = effect_user
                                                return_tmp={}
                                                return_tmp["x"] = 0
                                                return_tmp["y"] = 0
                                                return_tmp["place"] = "deck"
                                                return_tmp["deck_id"] = deck_id
                                                return_tmp["det"] = self.copy_monster_from_deck(user_deck)
                                                return_value.append(return_tmp)
                                                if mine_or_other2 ==1:
                                                    self.decks[deck_id]["mydeck"] = user_decks
                                                elif mine_or_other2 ==2:
                                                    self.decks[deck_id]["otherdeck"]= user_decks
                                                elif mine_or_other2 ==3:
                                                    self.decks[deck_id]["commondeck"] = user_decks
                                            else:
                                                if not "remove" in cost_result:
                                                    cost_result["remove"] = {}
                                                if not "deck" in cost_result["remove"]:
                                                    cost_result["remove"]["deck"] = []
                                                    place_id=user_deck["place_unique_id"]
                                                    cost_result_tmp = {}
                                                    cost_result_tmp["place_id"]= place_id
                                                    cost_result_tmp["user"]=mine_or_other3
                                                    cost_result_tmp["user_det"]=self.duel.cost_user
                                                    cost_result_tmp["deck_id"]= deck_id
                                                    cost_result["remove"]["deck"].append(cost_result_tmp)
                                                    self.cost_result = cost_result
                                                    return_tmp={}
                                                    return_tmp["x"] = 0
                                                    return_tmp["y"] = 0
                                                    return_tmp["place"] = "deck"
                                                    return_tmp["deck_id"] = deck_id
                                                    return_tmp["det"] = self.copy_monster_from_deck(user_deck)
                                                    return_value.append(return_tmp)
                            if place == "grave":
                                if mine_or_other2 ==1:
                                    grave = self.graves[deck_id]["mygrave"]
                                elif mine_or_other2 ==2:
                                    grave = self.graves[deck_id]["othergrave"]
                                elif mine_or_other2 ==3:
                                    grave = self.graves[deck_id]["commongrave"]
                                user_graves = grave
                                for user_grave in user_graves:
                                    if place_id== user_grave["place_unique_id"]:
                                        effect_flag = False
                                        if not self.check_not_effected(user_grave,effect_user,effect_kind,"grave",deck_id,0,0,mine_or_other3):
                                            if cost == 0:
                                                user_graves.remove(user_grave);
                                                user_grave["kind"] = effect_kind
                                                user_grave["user"] = mine_or_other3
                                                user_grave["user_det"] = effect_user
                                                return_tmp={}
                                                return_tmp["x"] = 0
                                                return_tmp["y"] = 0
                                                return_tmp["place"] = "grave"
                                                return_tmp["deck_id"] = deck_id
                                                return_tmp["det"] = self.copy_monster_from_grave(user_grave)
                                                return_value.append(return_tmp)
                                                if mine_or_other2 ==1:
                                                    self.graves[deck_id]["mygrave"] = user_graves
                                                elif mine_or_other2 ==2:
                                                    self.graves[deck_id]["othergrave"]= user_graves
                                                elif mine_or_other2 ==3:
                                                    self.graves[deck_id]["commongrave"] = user_graves
                                            else:
                                                if not "remove" in cost_result:
                                                    cost_result["remove"] = {}
                                                if not "grave" in cost_result["remove"]:
                                                    cost_result["remove"]["grave"] = []
                                                place_id=user_grave["place_unique_id"]
                                                cost_result_tmp = {}
                                                cost_result_tmp["place_id"]= place_id
                                                cost_result_tmp["user"]=mine_or_other3
                                                cost_result_tmp["user_det"]=self.duel.cost_user
                                                cost_result_tmp["grave_id"]= deck_id
                                                cost_result["remove"]["grave"].append(cost_result_tmp)
                                                self.cost_result = cost_result
                                                return_tmp={}
                                                return_tmp["x"] = 0
                                                return_tmp["y"] = 0
                                                return_tmp["place"] = "grave"
                                                return_tmp["deck_id"] = deck_id
                                                return_tmp["det"] = self.copy_monster_from_grave(user_grave)
                                                return_value.append(return_tmp)
                            if place == "hand":
                                if mine_or_other2 ==1:
                                    hand = self.hands[deck_id]["myhand"]
                                elif mine_or_other2 ==2:
                                    hand = self.hands[deck_id]["otherhand"]
                                elif mine_or_other2 ==3:
                                    hand = self.hands[deck_id]["commonhand"]
                                user_hands = hand
                                for user_hand in user_hands:
                                    if place_id== user_hand["place_unique_id"]:
                                        effect_flag = False
                                        if not self.check_not_effected(user_hand,effect_user,effect_kind,"hand",deck_id,0,0,mine_or_other3):
                                            if cost == 0:
                                                user_hands.remove(user_hand);
                                                user_hand["kind"] = effect_kind
                                                user_hand["user"] = mine_or_other3
                                                user_hand["user_det"] = effect_user
                                                return_tmp={}
                                                return_tmp["x"] = 0
                                                return_tmp["y"] = 0
                                                return_tmp["place"] = "hand"
                                                return_tmp["deck_id"] = deck_id
                                                return_tmp["det"] = self.copy_monster_from_hand(user_hand)
                                                return_value.append(return_tmp)
                                                if mine_or_other2 ==1:
                                                    self.hands[deck_id]["myhand"] = user_hands
                                                elif mine_or_other2 ==2:
                                                    self.hands[deck_id]["otherhand"]= user_hands
                                                elif mine_or_other2 ==3:
                                                    self.hands[deck_id]["commonhand"] = user_hands
                                            else:
                                                if not "remove" in cost_result:
                                                    cost_result["remove"] = {}
                                                if not "hand" in cost_result["remove"]:
                                                    cost_result["remove"]["hand"] = []
                                                place_id=user_hand["place_unique_id"]
                                                cost_result_tmp = {}
                                                cost_result_tmp["place_id"]= place_id
                                                cost_result_tmp["user"]=mine_or_other3
                                                cost_result_tmp["user_det"]=self.duel.cost_user
                                                cost_result_tmp["hand_id"]= deck_id
                                                cost_result["remove"]["hand"].append(cost_result_tmp)
                                                self.cost_result = cost_result
                                                return_tmp={}
                                                return_tmp["x"] = 0
                                                return_tmp["y"] = 0
                                                return_tmp["place"] = "hand"
                                                return_tmp["deck_id"] = deck_id
                                                return_tmp["det"] = self.copy_monster_from_hand(user_hand)
                                                return_value.append(return_tmp)

                place_array_tmp = []
                for place in monster_effect_det["monster"]["place"]:
                    place_tmp = place["det"].split("_")
                    if place["det"] == "":
                        continue
                    if place["and_or"] != "" and place_tmp[0] == "field":
                        tmptmp["and_or"]=place["and_or"]
                        tmptmp["det"]=place["det"]
                        place_array_tmp.append(tmptmp)
                        continue
                    else:
                        place_array = place_array_tmp
                        place_array_tmp = []
                    deck_id = int(place_tmp[1])
                    tmp_deck = None
                    for tmp_i in range(self.calculate_boland(monster_effect_det["min_equation_number"])):
                        tmp_i2 = 0
                        if monster_effect_text["field_x"]:
                            field = self.field
                            for str_x in monster_effect_text["field_x"]:
                                x  = int(str_x)
                                y = int(monster_effect_text["field_y"][tmp_i2])
                                if cost == 0:
                                    if(field[x][y]["det"] is not None):
                                        effect_flag = False
                                        place_id = field[x][y]["det"]["place_unique_id"]
                                        if not self.check_not_effected(field[x][y]["det"],effect_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                            det = field[x][y]["det"].copy();
                                            field[x][y]["det"] = None
                                            det =self.copy_monster_from_field(det)
                                            self.field = field
                                            det["kind"] = effect_kind
                                            det["user"] = int(field[x][y]["mine_or_other"])
                                            det["user_det"] = effect_user
                                    else:
                                        field[x][y]["det"] = None
                                        self.field = field
                                        det = None
                                    return_tmp={}
                                    return_tmp["x"] = x
                                    return_tmp["y"] = y
                                    return_tmp["place"] = "field"
                                    return_tmp["deck_id"] = 0
                                    return_tmp["det"] = det
                                    return_value.append(return_tmp)
                                else:
                                    cost_result_tmp = {}
                                    cost_result_tmp["x"]= x
                                    cost_result_tmp["y"]= y
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result["remove"]["field"].append(cost_result_tmp)
                                    self.cost_result = cost_result
                                    det =self.copy_monster_from_field(det)
                                    return_tmp={}
                                    return_tmp["x"] = x
                                    return_tmp["y"] = y
                                    return_tmp["place"] = "field"
                                    return_tmp["deck_id"] = 0
                                    return_tmp["det"] = det
                                    return_value.append( return_tmp)
                            continue
                        if((place_tmp[2] == "1" and effect_user ==self.user) or (place_tmp[2] == "2" and effect_user !=self.user)):
                            mine_or_other2 = 1
                        elif((place_tmp[2] == "1" and effect_user !=self.user) or (place_tmp[2] == "2" and effect_user ==self.user)):
                            mine_or_other2 = 2
                        else:
                            mine_or_other2 = 3
                        if self.user == 1:
                            mine_or_other3 = mine_or_other2
                        else:
                            if mine_or_other2 == 1:
                                mine_or_other3 = 2
                            elif mine_or_other2 == 2:
                                mine_or_other3 = 1
                            else:
                                mine_or_other3 = 3

                        if(place_tmp[0] == "deck" ):
                            if tmp_deck is None:
                                if mine_or_other2 == 1:
                                    tmp_deck = self.get_deck_with_effect(self.decks[deck_id]["mydeck"],monster_effect_det,effect_kind,exclude,effect_user,"deck",deck_id,0,0,mine_or_other3)
                                    deck = self.decks[deck_id]["mydeck"]
                                elif mine_or_other2 == 2:
                                    tmp_deck = self.get_deck_with_effect(self.decks[deck_id]["otherdeck"],monster_effect_det,effect_kind,exclude,effect_user,"deck",deck_id,0,0,mine_or_other3)
                                    deck = self.decks[deck_id]["otherdeck"]
                                elif mine_or_other2 == 3:
                                    tmp_deck = self.get_deck_with_effect(self.decks[deck_id]["commondeck"],monster_effect_det,effect_kind,exclude,effect_user,"deck",deck_id,0,0,mine_or_other3)
                                    deck = self.decks[deck_id]["commondeck"]
                                user_decks = deck
                            if not tmp_deck:
                                return return_value
                            if cost == 0:
                                move_flag = False
                                if(monster_effect_text["move_how"] == 0):
                                    user_deck =self.copy_monster_from_deck(user_decks[tmp_deck[0]])
                                    if not self.check_not_effected(user_deck,effect_user,effect_kind,"deck",deck_id,0,0,mine_or_other3):
                                        del user_decks[tmp_deck[0]]
                                        del tmp_deck[0]
                                        for tmpdecktmp in range(len(tmp_deck)):
                                            tmp_deck[tmpdecktmp]-=1
                                        move_flag = True
                                elif(monster_effect_text["move_how"] == 1):
                                    user_deck =self.copy_monster_from_deck(user_decks[tmp_deck[-1]])
                                    if not self.check_not_effected(user_deck,effect_user,effect_kind,"deck",deck_id,0,0,mine_or_other3):
                                        user_decks.pop(tmp_deck[-1])
                                        tmp_deck.pop()
                                        move_flag = True
                                else:
                                    rand_i = random.randrange(len(tmp_deck))
                                    range_i =tmp_deck[rand_i]
                                    user_deck =self.copy_monster_from_deck(user_decks[range_i])
                                    if not self.check_not_effected(user_deck,effect_user,effect_kind,"deck",deck_id,0,0,mine_or_other3):
                                        user_decks.pop(range_i)
                                        tmp_deck.pop(rand_i)
                                        for tmpdecktmp in range(len(tmp_deck)-rand_i):
                                            tmp_deck[tmpdecktmp+rand_i]-=1
                                        move_flag = True
                                if move_flag ==True:
                                    if mine_or_other2 == 1:
                                        self.decks[deck_id]["mydeck"] = user_decks
                                    elif mine_or_other2 == 2:
                                        self.decks[deck_id]["otherdeck"] = user_decks
                                    elif mine_or_other2 == 3:
                                        self.decks[deck_id]["commondeck"] = user_decks
                                    user_deck["kind"] = effect_kind
                                    user_deck["user"] = mine_or_other3
                                    user_deck["user_det"] = effect_user
                                    return_tmp={}
                                    return_tmp["x"] = 0
                                    return_tmp["y"] = 0
                                    return_tmp["place"] = "deck"
                                    return_tmp["deck_id"] = deck_id
                                    return_tmp["det"] = user_deck
                                    return_value.append( return_tmp)
                            else:
                                cost_result = self.cost_result
                                if(monster_effect_text["move_how"] == 0):
                                    user_deck =self.copy_monster_from_deck(user_decks[tmp_deck[0]])
                                    del user_decks[tmp_deck[0]]
                                    del tmp_deck[0]
                                    for tmpdecktmp in range(len(tmp_deck)):
                                        tmp_deck[tmpdecktmp]-=1
                                elif(monster_effect_text["move_how"] == 1):
                                    user_deck =self.copy_monster_from_deck(user_decks[tmp_deck[-1]])
                                    user_decks.pop(tmp_deck[-1])
                                    tmp_deck.pop()
                                else:
                                    rand_i = random.randrange(len(tmp_deck))
                                    range_i =tmp_deck[rand_i]
                                    user_deck =self.copy_monster_from_deck(user_decks[range_i])
                                    user_decks.pop(range_i)
                                    tmp_deck.pop(rand_i)
                                    for tmpdecktmp in range(len(tmp_deck)-rand_i):
                                        tmp_deck[tmpdecktmp+rand_i]-=1
                                effect_flag = False
                                if not self.check_not_effected(user_deck,effect_user,effect_kind,"deck",deck_id,0,0,mine_or_other3):
                                    if not "remove" in cost_result:
                                        cost_result["remove"] = {}
                                    if not "deck" in cost_result["remove"]:
                                        cost_result["remove"]["deck"] = []
                                    place_id=user_deck["place_unique_id"]
                                    cost_result_tmp = {}
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result_tmp["user"]=mine_or_other3
                                    cost_result_tmp["user"]=self.duel.cost_user
                                    cost_result_tmp["deck_id"]= deck_id
                                    cost_result["remove"]["deck"].append(cost_result_tmp)
                                    self.cost_result = cost_result
                                    return_tmp={}
                                    return_tmp["x"] = 0
                                    return_tmp["y"] = 0
                                    return_tmp["place"] = "deck"
                                    return_tmp["deck_id"] = deck_id
                                    return_tmp["det"] = user_deck
                                    return_value.append( return_tmp)
                        elif(place_tmp[0] == "grave" ):
                            if tmp_deck is None:
                                if mine_or_other2 == 1:
                                    tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["mygrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                                    grave = self.graves[deck_id]["mygrave"]
                                elif place_tmp[2] =="2":
                                    tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["othergrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                                    grave = self.graves[deck_id]["othergrave"]
                                elif place_tmp[2] =="0":
                                    tmp_deck = self.get_grave_with_effect(self.graves[deck_id]["commongrave"],monster_effect_det,effect_kind,exclude,effect_user,"grave",deck_id,0,0,mine_or_other3)
                                    grave = self.graves[deck_id]["commongrave"]

                            user_graves = grave
                            if not tmp_deck:
                                return return_value
                            if cost == 0:
                                move_flag = False
                                if(monster_effect_text["move_how"] == 0):
                                    user_grave =self.copy_monster_from_grave(user_graves[tmp_deck[0]])
                                    if not self.check_not_effected(user_grave,effect_user,effect_kind,"grave",deck_id,0,0,mine_or_other3):
                                        del user_graves[tmp_deck[0]]
                                        del tmp_deck[0]
                                        for tmpdecktmp in range(len(tmp_deck)):
                                            tmp_deck[tmpdecktmp]-=1
                                        move_flag = True
                                elif(monster_effect_text["move_how"] == 1):
                                    user_grave =self.copy_monster_from_grave(user_graves[tmp_deck[-1]])
                                    if not self.check_not_effected(user_grave,effect_user,effect_kind,"grave",deck_id,0,0,mine_or_other3):
                                        user_graves.pop(tmp_deck[-1])
                                        tmp_deck.pop()
                                else:
                                    rand_i = random.randrange(len(tmp_deck))
                                    range_i =tmp_deck[rand_i]

                                    user_grave =self.copy_monster_from_grave(user_graves[range_i])
                                    if not self.check_not_effected(user_grave,effect_user,effect_kind,"grave",deck_id,0,0,mine_or_other3):
                                        user_graves.pop(range_i)
                                        tmp_deck.pop(rand_i)
                                        for tmpdecktmp in range(len(tmp_deck)-rand_i):
                                            tmp_deck[tmpdecktmp+rand_i]-=1
                                        move_flag = True
                                effect_flag = False
                                if move_flag == True:
                                    if mine_or_other2 ==1:
                                        self.graves[deck_id]["mygrave"] = user_graves
                                    elif mine_or_other2 ==2:
                                        self.graves[deck_id]["othergrave"] = user_graves
                                    elif mine_or_other2 ==3:
                                        self.graves[deck_id]["commongrave"] = user_graves
                                    user_grave["kind"] = effect_kind
                                    user_grave["user"] = mine_or_other3
                                    user_grave["user_det"] = effect_user
                                    return_tmp={}
                                    return_tmp["x"] = 0
                                    return_tmp["y"] = 0
                                    return_tmp["place"] = "grave"
                                    return_tmp["deck_id"] = deck_id
                                    return_tmp["det"] = user_grave
                                    return_value.append( return_tmp)
                            else:
                                cost_result = self.cost_result
                                if(monster_effect_text["move_how"] == 0):
                                    user_grave =self.copy_monster_from_grave(user_graves[tmp_deck[0]])
                                    del user_graves[tmp_deck[0]]
                                    del tmp_deck[0]
                                    for tmpdecktmp in range(len(tmp_deck)):
                                        tmp_deck[tmpdecktmp]-=1
                                elif(monster_effect_text["move_how"] == 1):
                                    user_grave =self.copy_monster_from_grave(user_graves[tmp_deck[-1]])
                                    user_graves.pop(tmp_deck[-1])
                                    tmp_deck.pop[-1]
                                else:
                                    rand_i = random.randrange(len(tmp_deck))
                                    range_i =tmp_deck[rand_i]
                                    user_grave =self.copy_monster_from_grave(user_graves[range_i])
                                    user_graves.pop(range_i)
                                    tmp_deck.pop[rand_i]
                                    for tmpdecktmp in range(len(tmp_deck)-rand_i):
                                        tmp_deck[tmpdecktmp+rand_i]-=1
                                effect_flag = False
                                if not self.check_not_effected(user_grave,effect_user,effect_kind,"grave",deck_id,0,0,mine_or_other3):
                                    if not "remove" in cost_result:
                                        cost_result["remove"] = {}
                                    if not "grave" in cost_result["remove"]:
                                        cost_result["remove"]["grave"] = []
                                    place_id=user_grave["place_unique_id"]
                                    cost_result_tmp = {}
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result_tmp["user"]=mine_or_other3
                                    cost_result_tmp["user_det"]=self.duel.cost_user
                                    cost_result_tmp["grave_id"]= deck_id
                                    cost_result["remove"]["grave"].append(cost_result_tmp)
                                    self.cost_result = cost_result
                                    return_tmp={}
                                    return_tmp["x"] = 0
                                    return_tmp["y"] = 0
                                    return_tmp["place"] = "grave"
                                    return_tmp["deck_id"] = deck_id
                                    return_tmp["det"] = self.copy_monster_from_deck(user_grave)
                                    return_value.append( return_tmp)
                        elif(place_tmp[0] == "hand" ):
                            if tmp_deck is None:
                                if mine_or_other2 == 1:
                                    tmp_deck = self.get_hand_with_effect(self.hands[deck_id]["myhand"],monster_effect_det,effect_kind,exclude,effect_user,"hand",deck_id,0,0,mine_or_other3)
                                    hand = self.hands[deck_id]["myhand"]
                                elif mine_or_other2 == 2:
                                    tmp_deck = self.get_hand_with_effect(self.hands[deck_id]["otherhand"],monster_effect_det,effect_kind,exclude,effect_user,"hand",deck_id,0,0,mine_or_other3)
                                    hand = self.hands[deck_id]["otherhand"]
                                elif mine_or_other2 == 3:
                                    tmp_deck = self.get_hand_with_effect(self.hands[deck_id]["commonhand"],monster_effect_det,effect_kind,exclude,effect_user,"hand",deck_id,0,0,mine_or_other3)
                                    hand = self.hands[deck_id]["commonhand"]
                                user_hands = hand
                            if not tmp_deck:
                                return return_value
                            if cost == 0:
                                move_flag = False
                                if(monster_effect_text["move_how"] == 0):
                                    user_hand =self.copy_monster_from_hand(user_hands[tmp_deck[0]])
                                    if not self.check_not_effected(user_hand,effect_user,effect_kind,"hand",deck_id,0,0,mine_or_other3):
                                        del user_hands[tmp_deck[0]]
                                        del tmp_deck[0]
                                        for tmpdecktmp in range(len(tmp_deck)):
                                            tmp_deck[tmpdecktmp]-=1
                                        move_flag = True
                                elif(monster_effect_text["move_how"] == 1):
                                    user_hand =self.copy_monster_from_hand(user_hands[tmp_deck[-1]])
                                    if not self.check_not_effected(user_hand,effect_user,effect_kind,"hand",deck_id,0,0,mine_or_other3):
                                        user_hands.pop(tmp_deck[-1])
                                        tmp_deck.pop()
                                        move_flag = True
                                else:

                                    rand_i =random.randrange(len(tmp_deck))
                                    range_i =tmp_deck[rand_i]
                                    user_hand =self.copy_monster_from_hand(user_hands[range_i])
                                    if not self.check_not_effected(user_hand,effect_user,effect_kind,"hand",deck_id,0,0,mine_or_other3):
                                        user_hands.pop(range_i)
                                        tmp_deck.pop(rand_i)
                                        move_flag = True
                                        for tmpdecktmp in range(len(tmp_deck)-rand_i):
                                            tmp_deck[tmpdecktmp+rand_i]-=1
                                if move_flag == True:
                                    if mine_or_other2 == 1:
                                        self.hands[deck_id]["myhand"] = user_hands
                                    elif mine_or_other2 ==2:
                                        self.hands[deck_id]["otherhand"] = user_hands
                                    elif mine_or_other2 == 3:
                                        self.hands[deck_id]["commonhand"] = user_hands
                                    user_hand["kind"] = effect_kind
                                    user_hand["user"] = mine_or_other3
                                    user_hand["user_det"] = effect_user
                                    return_tmp={}
                                    return_tmp["x"] = 0
                                    return_tmp["y"] = 0
                                    return_tmp["place"] = "hand"
                                    return_tmp["deck_id"] = deck_id
                                    return_tmp["det"] = self.copy_monster_from_deck(user_hand)
                                    return_value.append( return_tmp)
                            else:
                                cost_result = self.cost_result
                                if(monster_effect_text["move_how"] == 0):
                                    user_hand =self.copy_monster_from_hand(user_hands[tmp_deck[0]])
                                    del user_hands[tmp_deck[0]]
                                    del tmp_deck[0]
                                    for tmpdecktmp in range(len(tmp_deck)):
                                        tmp_deck[tmpdecktmp]-=1
                                elif(monster_effect_text["move_how"] == 1):
                                    user_hand =self.copy_monster_from_hand(user_hands[tmp_deck[-1]])
                                    user_hands.pop(tmp_deck[-1])
                                    tmp_deck.pop()
                                else:
                                    rand_i =random.randrange(len(tmp_deck))
                                    range_i =tmp_deck[rand_i]

                                    user_hand =self.copy_monster_from_hand(user_hands[range_i])
                                    user_hands.pop(range_i)
                                    tmp_deck.pop(rand_i)
                                    for tmpdecktmp in range(len(tmp_deck)-rand_i):
                                        tmp_deck[tmpdecktmp+rand_i]-=1
                                if not self.check_not_effected(user_hand,effect_user,effect_kind,"hand",deck_id,0,0,mine_or_other3):
                                    if not "remove" in cost_result:
                                        cost_result["remove"] = {}
                                    if not "hand" in cost_result["remove"]:
                                        cost_result["remove"]["hand"] = []
                                    place_id=user_hand["place_unique_id"]
                                    cost_result_tmp= {}
                                    cost_result_tmp["place_id"]= place_id
                                    cost_result_tmp["user"]=mine_or_other3
                                    cost_result_tmp["user_det"]=self.duel.cost_user
                                    cost_result_tmp["hand_id"]= deck_id
                                    cost_result["remove"]["hand"].append(cost_result_tmp)
                                    self.cost_result = cost_result
                                    return_tmp={}
                                    return_tmp["x"] = 0
                                    return_tmp["y"] = 0
                                    return_tmp["place"] = "hand"
                                    return_tmp["deck_id"] = deck_id
                                    return_tmp["det"] = self.copy_monster_from_deck(user_hand)
                                    return_value.append( return_tmp)
                        elif(place_tmp[0] == "field" ):
                            field_size = FieldSize.objects.get(id=1);
                            field = self.field
                            flag_field_place = True
                            current_and_or = "and"
                            for x in range(field_size.field_x):
                                for y in range(field_size.field_y):
                                    for place_tmp2 in place_array:
                                        and_or = place_tmp2["and_or"]
                                        det = place_tmp2["det"]
                                        splitted_det = det.split("_")
                                        kind = splitted_det[1]
                                        tmp = field[x][y]["kind"].split("_")
                                        if(current_and_or == "and"):
                                            if kind in tmp:
                                                if flag_field_place == True:
                                                    flag_field_place = True
                                            else:
                                                flag_field_place = False
                                        elif(current_and_or == "or"):
                                            if kind in tmp:
                                                flag_field_place = True
                                            else:
                                                if flag_field_place == False:
                                                    flag_field_place = False
                                        current_and_or = and_or
                                    if flag_field_place == False:
                                        continue
                                    effect_flag = False
                                    if field[x][y]["det"] is None:
                                        continue
                                    if not self.check_not_effected(field[x][y]["det"],effect_user,effect_kind,"field",0,x,y,field[x][y]["mine_or_other"]):
                                        continue

                                    if not self.validate_answer(field[x][y]["det"],monster_effect_det["monster"],exclude,duel):

                                        continue
                                    if cost == 0:
                                        if(field[x][y]["det"] is not None):
                                            det = field[x][y]["det"].copy();
                                            field[x][y]["det"] = None
                                            det =self.copy_monster_from_field(det)
                                            self.field = field
                                            det["kind"] = effect_kind
                                            det["user"] = int(field[x][y]["mine_or_other"])
                                            det["user_det"] = effect_user
                                        else:
                                            field[x][y]["det"] = None
                                            self.field = field
                                            det = None
                                        return_tmp={}
                                        return_tmp["x"] = x
                                        return_tmp["y"] = y
                                        return_tmp["place"] = "field"
                                        return_tmp["deck_id"] = 0
                                        return_tmp["det"] = det
                                        return_value.append( return_tmp)
                                    else:
                                        cost_result_tmp = {}
                                        cost_result_tmp["x"]= x
                                        cost_result_tmp["y"]= y
                                        cost_result_tmp["place_id"]= place_id
                                        cost_result["remove"]["field"].append(cost_result_tmp)
                                        self.cost_result = cost_result
                                        det =self.copy_monster_from_field(det)
                                        return_tmp={}
                                        return_tmp["x"] = x
                                        return_tmp["y"] = y
                                        return_tmp["place"] = "field"
                                        return_tmp["deck_id"] = 0
                                        return_tmp["det"] = det
                                        return_value.append( return_tmp)

        return return_value
    def move_to_monster_cost(self,move_tos,cost_kind):
        duel = self.duel
        room_number = self.room_number
        cost_det = self.cost_det
        cost_wrapper = CostWrapper.objects.get(id = cost_det)
        cost = cost_wrapper.cost
        cost_text = json.loads(cost.cost)
        cost_user = duel.cost_user
        i=0
        for cost_det in cost_text:
            if("flag_add" in cost_text[0] and cost_text[0]["flag_add"] == True):
                flag_add = True
            else:
                flag_add = False
            if "as_cost_to" in cost_text[0] and cost_text[0]["as_cost_to"] != "":
                as_cost = cost_text[0]["as_cost_to"]
                tmp = self.cost
                tmp = tmp[str(duel.chain)]
                place1 = tmp[as_cost]
                for place2 in place1:
                    move_to = move_tos[i]["det"]

                    if move_to is None:
                        continue
                    i+=1
                    if(flag_add ==True):
                        move_to["flag"] = 1
                    else:
                        move_to["flag"] =0
                    if place2["place"] == "field":
                        x = int(place2["x"])
                        y = int(place2["y"])
                        field = self.field
                        if("det" in field[x][y] and field[x][y]["det"] is not None):
                            return "error"
                        cost_result = self.cost_result
                        if not "add" in cost_result:
                            cost_result["add"] = {}

                        if not "field" in cost_result["add"]:
                            cost_result["add"]["field"] =[]
                        cost_result_tmp = {}
                        cost_result_tmp["user_det"] = field[x][y]["mine_or_other"]
                        cost_result_tmp["x"]= x
                        cost_result_tmp["y"]= y
                        cost_result_tmp["kind"]= cost_kind
                        cost_result_tmp["det"]= json.dumps(move_to)
                        cost_result["add"]["field"].append(cost_result_tmp)
                        self.cost_result = cost_result
            if "place_to"  in cost_det:
                for place in cost_det["place_to"].values():
                    place_tmp = place.split("_")
                    deck_id = int(place_tmp[1])
                    mine_or_other = int(place_tmp[2])
                    if cost_user == 2:
                        if mine_or_other == 1:
                            mine_or_other == 2
                        else:
                            mine_or_other == 1
                    for move_to in move_tos:
                        move_to_org = move_to
                        move_to = move_to["det"]
                        if move_to is None:
                            continue
                        if(flag_add ==True):
                            move_to["flag"] = 1
                        else:
                            move_to["flag"] =0
                        if place_tmp[0] == "deck":
                            cost_result = self.cost_result
                            if not "add" in cost_result:
                                cost_result["add"] = {}

                            if not "deck" in cost_result["add"]:
                                cost_result["add"]["deck"] = []
                            cost_result_tmp = {}
                            cost_result_tmp["det"]= json.dumps(move_to)
                            cost_result_tmp["user"]=cost_user
                            cost_result_tmp["user_det"] = mine_or_other
                            cost_result_tmp["deck_id"]= deck_id
                            cost_result_tmp["kind"]= cost_kind
                            cost_result_tmp["how"]= cost_det["move_how_to"]
                            cost_result["add"]["deck"].append(cost_result_tmp)
                            self.cost_result = cost_result
                        if(place_tmp[0] == "grave"):
                            cost_result = self.cost_result
                            if not "add" in cost_result:
                                cost_result["add"] = {}

                            if not "grave" in cost_result["add"]:
                                cost_result["add"]["grave"] = []
                            cost_result_tmp = {}
                            cost_result_tmp["det"]= json.dumps(move_to)
                            cost_result_tmp["user"]= cost_user
                            cost_result_tmp["user_det"] = mine_or_other
                            cost_result_tmp["grave_id"]= deck_id
                            cost_result_tmp["kind"]= cost_kind
                            cost_result_tmp["how"]= cost_det["move_how_to"]
                            cost_result["add"]["grave"].append(cost_result_tmp)
                            self.cost_result = cost_result
                        if(place_tmp[0] == "hand"):
                            cost_result = self.cost_result
                            if not "add" in cost_result:
                                cost_result["add"] = {}

                            if not "hand" in cost_result["add"]:
                                cost_result["add"]["hand"] = []
                            cost_result_tmp = {}
                            cost_result_tmp["det"]= json.dumps(move_to)
                            cost_result_tmp["user"]= cost_user
                            cost_result_tmp["user_det"] = mine_or_other
                            cost_result_tmp["kind"]= cost_kind
                            cost_result_tmp["hand_id"]= deck_id
                            cost_result_tmmp["how"]= cost_det["move_how_to"]
                            cost_result["add"]["hand"].append(cost_result_tmp)
                            self.cost_result = cost_result








    def move_to_monster(self,move_tos,effect_kind,cost = 0):
        duel = self.duel
        room_number = self.room_number
        chain_det = json.loads(duel.chain_det)
        chain_user = json.loads(duel.chain_user)
        user = chain_user[str(duel.chain-1)]
        pprint(user)
        pprint(duel.user_turn)
        monster_effect_wrapper = MonsterEffectWrapper.objects.get(id = int(chain_det[str(duel.chain-1)]))
        pprint(monster_effect_wrapper)
        monster_effect = monster_effect_wrapper.monster_effect
        monster_effect_det = json.loads(monster_effect.monster_effect)

        i=0
        flag_change_how = monster_effect_det["flag_change_how"]
        flag_change_val = monster_effect_det["flag_change_val"]
        variable_names = []
        if "monster_variable_change_how" in monster_effect_det and monster_effect_det["monster_variable_change_how"] != []:
            for index in range(len(monster_effect_det["monster_variable_change_how"])):
                variable_names.append (monster_effect_det["monster_variable_change_name"][index])
        if "as_monster_condition_to" in monster_effect_det and monster_effect_det["as_monster_condition_to"] != "":
            as_monster_effect = monster_effect_det["as_monster_condition_to"]
            tmp = self.mess
            cost_tmp = self.cost
            timing_tmp = self.timing_mess
            if str(duel.chain-1) not in tmp:
                tmp[str(duel.chain-1)] = {}
            if as_monster_effect[0]== "~":
                place1 = cost_tmp[str(duel.chain)][as_monster_effect[1:]]
            elif as_monster_effect[0]== "%":
                place1 = timing_tmp[as_monster_effect[1:]]
            else:
                place1 = tmp[str(duel.chain-1)][as_monster_effect]
            for place2 in place1:
                move_to = move_tos[i]
                move_to_org = move_to
                move_to = move_to["det"]
                if move_to is None:
                    continue
                if "monster_variable_change_how" in monster_effect_det and monster_effect_det["monster_variable_change_how"] != []:
                    for index in range(len(monster_effect_det["monster_variable_change_how"])):
                        variable_name = monster_effect_det["monster_variable_change_name"][index]
                        if monster_effect_det["monster_variable_change_how"][index] == 0:
                            move_to["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect_det["monster_variable_change_val"][index]) + int( field[x][y]["det"]["variables"][variable_name]["value"] ))
                        elif monster_effect_det["monster_variable_change_how"][index] == 1:
                            move_to["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect_det["monster_variable_change_val"][index]) - int( field[x][y]["det"]["variables"][variable_name]["value"] ))
                        elif monster_effect_det["monster_variable_change_how"][index] == 2:
                            move_to["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect_det["monster_variable_change_val"][index]) )
                if(flag_change_how != "0"):
                    if(not "flag" in move_to):
                        move_to["flag"] =0
                    if(flag_change_how == "1"):
                        move_to["flag"] += int(flag_change_val)
                    elif(flag_change_how == "2"):
                        move_to["flag"] -= int(flag_change_val)
                    elif(flag_change_how == "3"):
                        move_to["flag"] = int(flag_change_val)
                i+=1
                if place2["place"] == "field":
                    x = int(place2["x"])
                    y = int(place2["y"])
                    field = self.field
                    if("det" in field[x][y] and field[x][y]["det"] is not None):
                        return "error"
                    if cost == 1:
                        cost_result = self.cost_result
                        if not "add" in cost_result:
                            cost_result["add"] = {}

                        if not "field" in cost_result["add"]:
                            cost_result["add"]["field"] =[]
                        cost_result_tmp = {}
                        cost_result_tmp["user_det"] = cost_user
                        cost_result_tmp["x"]= x
                        cost_result_tmp["y"]= y
                        cost_result_tmp["kind"]= cost_kind
                        cost_result_tmp["det"]= json.dumps(move_to)
                        cost_result["add"]["field"].append(cost_result_tmp)
                        self.cost_result = cost_result
                    else:
                        move_to_tmp = move_to.copy()
                        if("trigger" in tmp[str(duel.chain-1)] and move_to["place_unique_id"] == tmp[str(duel.chain-1)]["trigger"][0]["place_id"]):
                            check_cost = self.cost
                            tmp2 = {}
                            org_trigger = tmp[str(duel.chain-1)]["trigger"]
                            if org_trigger["det_from"] != None:
                                tmp2["from_x"] = org_trigger["from_x"]
                                tmp2["from_y"] = org_trigger["from_y"]
                                tmp2["det_from"] = org_trigger["det_from"]
                                tmp2["place_id_from"] = org_trigger["place_id_from"]
                                tmp2["place_from"] = org_trigger["place_from"]
                                tmp2["deck_id_from"] = org_trigger["deck_id_from"]
                            else:
                                tmp2["from_x"] = move_to_org["x"]
                                tmp2["from_y"] = move_to_org["y"]
                                tmp2["det_from"] = move_to_org["det"]
                                tmp2["place_id_from"] = move_to_org["det"]["place_id"]
                                tmp2["place_from"] = move_to_org["place"]
                                tmp2["deck_id_from"] = move_to_org["deck_id_from"]
                            tmp2["x"] = x
                            tmp2["y"] = y
                            tmp2["det"] = move_to
                            tmp2["det"]["place_id"] = move_to_tmp["place_unique_id"]
                            tmp2["place_id"] = move_to_tmp["place_unique_id"]
                            tmp2["mine_or_other"]  = field[x][y]["mine_or_other"]
                            tmp2["user"] = field[x][y]["mine_or_other"]
                            tmp2["place"] = "field"
                            tmp2["deck_id"] =0
                            check_cost[str(duel.chain-1)]["trigger"] = []
                            check_cost[str(duel.chain-1)]["trigger"].append = tmp2
                            tmp[str(duel.chain-1)]["trigger"] = []
                            tmp[str(duel.chain-1)]["trigger"].append = tmp2
                            self.cost = check_cost
                            self.mess =tmp
                        field[x][y]["det"] = self.copy_monster_to_field(move_to,x,y,field[x][y]["mine_or_other"],variable_names)
                        self.raise_trigger(field[x][y]["det"],move_to_tmp,"effect","field",user,field[x][y]["mine_or_other"],None,effect_kind,x,y)
                        self.field = field
        if "place_to"  in monster_effect_det and monster_effect_det["place_to"]["0"] != "":
            place = monster_effect_det["place_to"]["0"]
            tmp= self.mess
            if str(duel.chain-1) not in tmp:
                tmp[str(duel.chain-1)] = {}
            for move_to in move_tos:
                move_to_org = move_to
                move_to = move_to["det"]
                if move_to is None:
                    continue
                if "monster_variable_change_how" in monster_effect_det and monster_effect_det["monster_variable_change_how"] != []:
                    for index in range(len(monster_effect_det["monster_variable_change_how"])):
                        variable_name = monster_effect_det["monster_variable_change_name"][index]
                        if monster_effect_det["monster_variable_change_how"][index] == 0:
                            move_to["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect_det["monster_variable_change_val"][index]) + int( field[x][y]["det"]["variables"][variable_name]["value"] ))
                        elif monster_effect_det["monster_variable_change_how"][index] == 1:
                            move_to["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect_det["monster_variable_change_val"][index]) - int( field[x][y]["det"]["variables"][variable_name]["value"] ))
                        elif monster_effect_det["monster_variable_change_how"][index] == 2:
                            move_to["variables"][variable_name]["value"] = str(self.calculate_boland(monster_effect_det["monster_variable_change_val"][index]) )
                if(flag_change_how != "0"):
                    if(not "flag" in move_to):
                        move_to["flag"] =0
                    if(flag_change_how == "1"):
                        move_to["flag"] += int(flag_change_val)
                    elif(flag_change_how == "2"):
                        move_to["flag"] -= int(flag_change_val)
                    elif(flag_change_how == "3"):
                        move_to["flag"] = int(flag_change_val)
                place_tmp = place.split("_")
                deck_id = int(place_tmp[1])
                if(place_tmp[2] == "1" and user== self.user) or (place_tmp[2] == "2" and user != self.user):
                    mine_or_other2 = 1
                elif(place_tmp[2] == "1" and user!=self.user) or (place_tmp[2] == "2" and user == self.user):
                    mine_or_other2 = 2
                else:
                    mine_or_other2 = 3
                if(place_tmp[2] == "1" and user== 1) or (place_tmp[2] == "2" and user == 2):
                    mine_or_other3 = 1
                elif(place_tmp[2] == "1" and user==2) or (place_tmp[2] == "2" and user == 1):
                    mine_or_other3 = 2
                else:
                    mine_or_other3 = 3
                if self.user == 1:
                    mine_or_other4 = mine_or_other2
                else:
                    if(mine_or_other2 == 1):
                        mine_or_other4 = 2
                    elif(mine_or_other2 == 2):
                        mine_or_other4 = 1
                    else:
                        mine_or_other4 = 3
                if place_tmp[0] == "deck":
                    if mine_or_other2 == 1:
                        deck = self.decks[deck_id]["mydeck"]
                    elif mine_or_other2 == 2:
                        deck = self.decks[deck_id]["otherdeck"]
                    elif mine_or_other2 == 3:
                        deck = self.decks[deck_id]["commondeck"]
                    user_decks = deck
                    move_to_tmp = move_to.copy()
                    move_to = self.copy_monster_to_deck(move_to,deck_id,mine_or_other3,variable_names)
                    if cost == 1:
                        cost_result = self.cost_result
                        if not "add" in cost_result:
                            cost_result["add"] = {}
    
                        if not "deck" in cost_result["add"]:
                            cost_result["add"]["deck"] = []
                        cost_result_tmp = {}
                        cost_result_tmp["det"]= json.dumps(move_to)
                        cost_result_tmp["user"]= mine_or_other4
                        cost_result_tmp["user_det"] = cost_user
                        cost_result_tmp["deck_id"]= deck_id
                        cost_result_tmp["kind"]= cost_kind
                        cost_result_tmp["how"]= cost_det["move_how_to"]
                        cost_result["add"]["deck"].append(cost_result_tmp)
                        self.cost_result = cost_result
                    else:
                        if(move_to["place_unique_id"] == tmp[str(duel.chain-1)]["trigger"][0]["place_id"]):
                            check_cost = self.cost
                            tmp2 = {}
                            if org_trigger["det_from"] != None:
                                tmp2["from_x"] = org_trigger["from_x"]
                                tmp2["from_y"] = org_trigger["from_y"]
                                tmp2["det_from"] = org_trigger["det_from"]
                                tmp2["place_id_from"] = org_trigger["place_id_from"]
                                tmp2["place_from"] = org_trigger["place_from"]
                                tmp2["deck_id_from"] = org_trigger["deck_id_from"]
                            else:
                                tmp2["from_x"] = move_to_org["x"]
                                tmp2["from_y"] = move_to_org["y"]
                                tmp2["det_from"] = move_to_org["det"]
                                tmp2["place_id_from"] = move_to_org["det"]["place_id"]
                                tmp2["place_from"] = move_to_org["place"]
                                tmp2["deck_id_from"] = move_to_org["deck_id_from"]
                            tmp2["x"] = 0
                            tmp2["y"] = 0
                            tmp2["det"] = move_to
                            tmp2["det"]["place_id"] = move_to_tmp["place_id"]
                            tmp2["place_id"] = move_to_tmp["place_unique_id"]
                            tmp2["mine_or_other"] =mine_or_other3
                            tmp2["user"] = mine_or_other4
                            tmp2["place"] = "deck"
                            tmp2["deck_id"] =  deck_id
                            check_cost[str(duel.chain-1)]["trigger"] = []
                            check_cost[str(duel.chain-1)]["trigger"].append = tmp2
                            tmp[str(duel.chain-1)]["trigger"] = []
                            tmp[str(duel.chain-1)]["trigger"].append = tmp2
                            self.cost = check_cost
                            self.mess = tmp
                        self.raise_trigger(move_to,move_to_tmp,"effect","deck",user,mine_or_other4,deck_id,effect_kind,None,None)
                        if(monster_effect_det["move_how_to"] == 0 or len(user_decks) == 0):
                            user_decks.insert(0,move_to)
                        elif(monster_effect_det["move_how_to"] == 1):
                            user_decks.append(move_to)
                        else:
                            range_i =random.randrange(len(user_decks))
                            user_decks.insert(range_i,move_to)
                        if mine_or_other2 == 1:
                            self.decks[deck_id]["mydeck"] = user_decks
                        elif mine_or_other2 == 2:
                            self.decks[deck_id]["otherdeck"] = user_decks
                        elif mine_or_other2 == 3:
                            self.decks[deck_id]["commondeck"] = user_decks
                if(place_tmp[0] == "grave"):
                    if mine_or_other2 == 1:
                        grave = self.graves[deck_id]["mygrave"]
                    elif mine_or_other2 == 2:
                        grave = self.graves[deck_id]["othergrave"]
                    elif mine_or_other2 == 3:
                        grave = self.graves[deck_id]["commongrave"]
                    user_graves = grave
                    move_to_tmp = move_to.copy()
                    move_to = self.copy_monster_to_grave(move_to,deck_id,mine_or_other3,variable_names)
                    if cost == 1:
                        cost_result = self.cost_result
                        if not "add" in cost_result:
                            cost_result["add"] = {}
    
                            if not "grave" in cost_result["add"]:
                                cost_result["add"]["grave"] = []
                            cost_result_tmp = {}
                            cost_result_tmp["det"]= json.dumps(move_to)
                            cost_result_tmp["user"]= mine_or_other4
                            cost_result_tmp["user_det"] = cost_user
                            cost_result_tmp["grave_id"]= grave_id
                            cost_result_tmp["how"]= cost_det["move_how_to"]
                            cost_result_tmp["kind"]= cost_kind
                            cost_result["add"]["grave"].append(cost_result_tmp)
                            self.cost_result = cost_result
                    else:
                        if(move_to["place_id"] == tmp[str(duel.chain-1)]["trigger"][0]["place_id"]):
                            check_cost = self.cost
                            tmp2 = {}
                            if org_trigger["det_from"] != None:
                                tmp2["from_x"] = org_trigger["from_x"]
                                tmp2["from_y"] = org_trigger["from_y"]
                                tmp2["det_from"] = org_trigger["det_from"]
                                tmp2["place_id_from"] = org_trigger["place_id_from"]
                                tmp2["place_from"] = org_trigger["place_from"]
                                tmp2["deck_id_from"] = org_trigger["deck_id_from"]
                            else:
                                tmp2["from_x"] = move_to_org["x"]
                                tmp2["from_y"] = move_to_org["y"]
                                tmp2["det_from"] = move_to_org["det"]
                                tmp2["place_id_from"] = move_to_org["det"]["place_id"]
                                tmp2["place_from"] = move_to_org["place"]
                                tmp2["deck_id_from"] = move_to_org["deck_id_from"]
                            tmp2["x"] = 0
                            tmp2["y"] = 0
                            tmp2["det"] = move_to
                            tmp2["det"]["place_id"] = move_to_tmp["place_unique_id"]
                            tmp2["place_id"] = move_to_tmp["place_unique_id"]
                            tmp2["mine_or_other"] =mine_or_other3
                            tmp2["user"] = mine_or_other4
                            tmp2["place"] = "grave"
                            tmp2["deck_id"] =  deck_id
                            check_cost[str(duel.chain-1)]["trigger"] = []
                            check_cost[str(duel.chain-1)]["trigger"].append = tmp2
                            tmp[str(duel.chain-1)]["trigger"] = []
                            tmp[str(duel.chain-1)]["trigger"].append = tmp2
                            self.cost = check_cost
                            self.mess = tmp
                        self.raise_trigger(move_to,move_to_tmp,"effect","grave",user,mine_or_other4,deck_id,effect_kind,None,None)
                        if(monster_effect_det["move_how_to"] == 0 or len(user_graves) == 0):
                            user_graves.insert(0,move_to)
                        elif(monster_effect_det["move_how_to"] == 1):
                            user_graves.append(move_to)
                        else:
                            range_i =random.randrange(len(user_graves))
                            user_graves.insert(range_i,move_to)
                        if mine_or_other2 == 1:
                            self.graves[deck_id]["mygrave"] = user_graves
                        elif mine_or_other2 == 2:
                            self.graves[deck_id]["othergrave"] = user_graves
                        elif mine_or_other2 == 3:
                            self.graves[deck_id]["commongrave"] = user_graves
                if(place_tmp[0] == "hand"):
                    if mine_or_other2 == 1:
                        hand = self.hands[deck_id]["myhand"]
                    elif mine_or_other2 == 2:
                        hand = self.hands[deck_id]["otherhand"]
                    elif mine_or_other2 == 3:
                        hand = self.hands[deck_id]["commonhand"]
                    user_hands = hand
                    move_to_tmp = move_to.copy()
                    move_to = self.copy_monster_to_hand(move_to,deck_id,mine_or_other3,variable_names)
                    if cost == 1:
                        if(move_to["place_unique_id"] == tmp[str(duel.chain-1)]["trigger"][0]["place_unique_id"]):
                            check_cost = self.cost
                            tmp2 = {}
                            if org_trigger["det_from"] != None:
                                tmp2["from_x"] = org_trigger["from_x"]
                                tmp2["from_y"] = org_trigger["from_y"]
                                tmp2["det_from"] = org_trigger["det_from"]
                                tmp2["place_id_from"] = org_trigger["place_id_from"]
                                tmp2["place_from"] = org_trigger["place_from"]
                                tmp2["deck_id_from"] = org_trigger["deck_id_from"]
                            else:
                                tmp2["from_x"] = move_to_org["x"]
                                tmp2["from_y"] = move_to_org["y"]
                                tmp2["det_from"] = move_to_org["det"]
                                tmp2["place_id_from"] = move_to_org["det"]["place_id"]
                                tmp2["place_from"] = move_to_org["place"]
                                tmp2["deck_id_from"] = move_to_org["deck_id_from"]
                            tmp2["x"] = 0
                            tmp2["y"] = 0
                            tmp2["det"] = move_to
                            tmp2["place_id"] = move_to_tmp["place_unique_id"]
                            tmp2["det"]["place_id"] = move_to_tmp["place_unique_id"]
                            tmp2["mine_or_other"] =mine_or_other3
                            tmp2["user"] = mine_or_other4
                            tmp2["place"] = "hand"
                            tmp2["deck_id"] =  deck_id
                            check_cost[str(duel.chain-1)]["trigger"] = []
                            check_cost[str(duel.chain-1)]["trigger"].append = tmp2
                            tmp[str(duel.chain-1)]["trigger"] = []
                            tmp[str(duel.chain-1)]["trigger"].append = tmp2
                            self.cost = check_cost
                            self.mess = tmp
                        cost_result = self.cost_result
                        if not "add" in cost_result:
                            cost_result["add"] = {}
    
                        if not "hand" in cost_result["add"]:
                            cost_result["add"]["hand"] = []
                        cost_result_tmp = {}
                        cost_result_tmp["det"]= json.dumps(move_to)
                        cost_result_tmp["user"]= mine_or_other4
                        cost_result_tmp["user_det"] = cost_user
                        cost_result_tmp["kind"]= cost_kind
                        cost_result_tmp["hand_id"]= deck_id
                        cost_result_tmmp["how"]= cost_det["move_how_to"]
                        cost_result["add"]["hand"].append(cost_result_tmp)
                        self.cost_result = cost_result
                    if cost == 0:
                        if(monster_effect_det["move_how_to"] == 0 or len(user_hands) == 0):
                            user_hands.insert(0,move_to)
                        elif(monster_effect_det["move_how_to"] == 1):
                            user_hands.append(move_to)
                        else:
                            range_i =random.randrange(len(user_hands))
                            user_hands.insert(range_i,move_to)
                        if mine_or_other2 == 1:
                            self.hands[deck_id]["myhand"] = user_hands
                        elif mine_or_other2 == 2:
                            self.hands[deck_id]["otherhand"] = user_hands
                        elif mine_or_other2 == 3:
                            self.hands[deck_id]["commonhand"] = user_hands
                        self.raise_trigger(move_to,move_to_tmp,"effect","hand",user,mine_or_other4,deck_id,effect_kind,None,None)
                if(place_tmp[0] == "field"):
                    if "field_x_to" in monster_effect_det:
                        field = self.field
                        x = int(monster_effect_det["field_x_to"])
                        y = int(monster_effect_det["field_y_to"])
                        move_to_tmp = move_to.copy()
                        if cost == 1:
                            if(move_to["place_unique_id"] == tmp[str(duel.chain-1)]["trigger"][0]["place_unique_id"]):
                                check_cost = self.cost
                                tmp2 = {}
                                if org_trigger["det_from"] != None:
                                    tmp2["from_x"] = org_trigger["from_x"]
                                    tmp2["from_y"] = org_trigger["from_y"]
                                    tmp2["det_from"] = org_trigger["det_from"]
                                    tmp2["place_id_from"] = org_trigger["place_id_from"]
                                    tmp2["place_from"] = org_trigger["place_from"]
                                    tmp2["deck_id_from"] = org_trigger["deck_id_from"]
                                else:
                                    tmp2["from_x"] = move_to_org["x"]
                                    tmp2["from_y"] = move_to_org["y"]
                                    tmp2["det_from"] = move_to_org["det"]
                                    tmp2["place_id_from"] = move_to_org["det"]["place_id"]
                                    tmp2["place_from"] = move_to_org["place"]
                                    tmp2["deck_id_from"] = move_to_org["deck_id_from"]
                                tmp2["x"] = x
                                tmp2["y"] = y
                                tmp2["det"] = move_to
                                tmp2["det"]["place_id"] = move_to_tmp["place_unique_id"]
                                tmp2["place_id"] = move_to_tmp["place_unique_id"]
                                tmp2["mine_or_other"] =field[x][y]["mine_or_other"]
                                tmp2["user"] = field[x][y]["mine_or_other"]
                                tmp2["user_det"] = effect_user
                                tmp2["place"] = "field"
                                tmp2["deck_id"] =  0
                                check_cost[str(duel.chain-1)]["trigger"] = []
                                check_cost[str(duel.chain-1)]["trigger"].append = tmp2
                                tmp[str(duel.chain-1)]["trigger"] = []
                                tmp[str(duel.chain-1)]["trigger"].append = tmp2
                                self.cost = check_cost
                                self.mess = tmp
                            cost_result = self.cost_result
                            if not "add" in cost_result:
                                cost_result["add"] = {}
    
                            if not "field" in cost_result["add"]:
                                cost_result["add"]["field"] = []
                            if "field_x_to" in monster_effect_det:
                                field = self.field
                            x = int(monster_effect_det["field_x_to"])
                            y = int(monster_effect_det["field_y_to"])
                            cost_result_tmp = {}
                            cost_result_tmp["x"]= x
                            cost_result_tmp["y"]= y
                            cost_result_tmp["kind"]= cost_kind
                            cost_result_tmp["det"]= json.dumps(move_to)
                            cost_result["add"]["field"].append(cost_result_tmp)
                            self.cost_result = cost_result
                        else:
                            field[x][y]["det"]= self.copy_monster_to_field(move_to,x,y,field[x][y]["mine_or_other"],variable_names)
                            self.raise_trigger(field[x][y]["det"],move_to_tmp,"effect","field",user,field[x][y]["mine_or_other"],None,effect_kind,x,y)
                            self.field = field
                    else:
                        self.move_to_field(place_tmp,move_to,cost,variable_names,effect_kind)
    
    

    def move_to_field(self,place_tmp,move_to,cost,variable_names,effect_kind):
        duel = self.duel
        field = self.field
        deck_id = place_tmp[1]
        chain_user = json.loads(duel.chain_user)
        user = chain_user[str(duel.chain-1)]
        mess = self.mess
        if(place_tmp[2] == "1" and user == 1) or (place_tmp[2] == "2" and user == 2):
            mine_or_other = 1
        elif(place_tmp[2] == "1" and user ==2) or (place_tmp[2] == "2" and user == 1):
            mine_or_other = 2
        else:
            mine_or_other = 3
        for x in range(len(field)):
            for y in range(len(field[x])):
                kind = field[x][y]["kind"]
                mine_or_other_field = field[x][y]["mine_or_other"]
                if kind.find(deck_id) > -1 and mine_or_other == mine_or_other_field:
                    if "det" in field[x][y] and field[x][y]["det"] == None:
                        if cost == 1:
                            cost_result = self.cost_result
                            if not "add" in cost_result:
                                cost_result["add"] = {}

                            if not "field" in cost_result["add"]:
                                cost_result["add"]["field"] = []
                            cost_result_tmp = {}
                            cost_result_tmp["x"]= x
                            cost_result_tmp["y"]= y
                            cost_result_tmp["det"]= json.dumps(move_to)
                            cost_result_tmp["kind"]= cost_kind
                            cost_result["add"]["field"].append(cost_result_tmp)
                            self.cost_result = cost_result
                            return
                        else:
                            field[x][y]["det"]= self.copy_monster_to_field(move_to,x,y,field[x][y]["mine_or_other"],variable_names)
                            self.field = field
                            move_to_tmp = move_to.copy()
                            self.raise_trigger(field[x][y]["det"],move_to_tmp,"effect","field",user,field[x][y]["mine_or_other"],None,effect_kind,x,y)
                            if( "trigger" in mess[str(duel.chain-1)] and move_to["place_unique_id"] == mess[str(duel.chain-1)]["trigger"][0]["place_unique_id"]):
                                   check_cost = self.cost
                                   tmp2 = {}
                                   if org_trigger["det_from"] != None:
                                       tmp2["from_x"] = org_trigger["from_x"]
                                       tmp2["from_y"] = org_trigger["from_y"]
                                       tmp2["det_from"] = org_trigger["det_from"]
                                       tmp2["place_id_from"] = org_trigger["place_id_from"]
                                       tmp2["place_from"] = org_trigger["place_from"]
                                       tmp2["deck_id_from"] = org_trigger["deck_id_from"]
                                   else:
                                       tmp2["from_x"] = move_to_org["x"]
                                       tmp2["from_y"] = move_to_org["y"]
                                       tmp2["det_from"] = move_to_org["det"]
                                       tmp2["place_id_from"] = move_to_org["det"]["place_id"]
                                       tmp2["place_from"] = move_to_org["place"]
                                       tmp2["deck_id_from"] = move_to_org["deck_id_from"]
                                   tmp2["x"] = x
                                   tmp2["y"] = y
                                   tmp2["det"] = move_to
                                   tmp2["det"]["place_id"] = move_to_tmp["place_unique_id"]
                                   tmp2["place_id"] = move_to_tmp["place_unique_id"]
                                   tmp2["mine_or_other"] = field[x][y]["mine_or_other"]
                                   tmp2["user"] =  field[x][y]["mine_or_other"]
                                   tmp2["user_det"] = effect_user
                                   tmp2["place"] = "field"
                                   tmp2["deck_id"] =  0
                                   check_cost[str(duel.chain-1)]["trigger"] = []
                                   check_cost[str(duel.chain-1)]["trigger"].append = tmp2
                                   tmp[str(duel.chain-1)]["trigger"] = []
                                   tmp[str(duel.chain-1)]["trigger"].append = tmp2
                                   self.cost = check_cost
                                   self.mess = mess
                            return

    def watch_field(self,field):
        for x in range(len(field)):
            for y in range(len(field[x])):
                if(field[x][y]["det"] is None):
                    field[x][y]["hide"] = False
                    continue
                if int(field[x][y]["det"]["variables"]["show"]["value"]) == 1:
                        field[x][y]["det"] = None
                        field[x][y]["hide"] = True
        return field
    def modify_field_info(self,field,user,other_user,priority,mode=0):
        for x in range(len(field)):
            for y in range(len(field[x])):
                if int(field[x][y]["mine_or_other"]) == 1:

                    mine_or_other = 1
                elif field[x][y]["mine_or_other"] == 2:
                    mine_or_other = 2
                else:
                    mine_or_other = 0
                if(field[x][y]["det"] is None):
                    field[x][y]["hide"] = False
                    continue
                if(int(field[x][y]["mine_or_other"]) == other_user ):
                    if int(field[x][y]["det"]["variables"]["show"]["value"]) == 1:
                        field[x][y]["det"] = None
                        field[x][y]["hide"] = True
                if(field[x][y])["det"] is not None:
                    result_triggers = self.check_field_trigger(field[x][y]["det"],x,y,user,other_user,mine_or_other,priority,mode)
                    if mode == 1 and result_triggers == True:
                        return True
                    field[x][y]["det"]["trigger"] = result_triggers
        if mode == 1 :
            return False

        return field
    def check_hand_eternal(self,hand_info,count,user,other_user):
        result_hand_eternal = []
        for i in range(count):
            if hand_info[i]["eternal"] == False:
                continue
            result_hand_eternal += self.check_hand_eternal_det(hand_info[i],i,user,other_user)
        return result_hand_eternal
    def check_hand_eternal_det(self,hand_info,hand_number,user,other_user):
        result_hand_eternal = []

        if("myhand" in hand_info):
            if(user ==1):
                mine_or_other = 1
            else:
                mine_or_other = 2
            for i in range(hand_info["myhandnum"]):
                result_hand_eternal+= self.check_hand_eternal_det_det(hand_info["myhand"][i],hand_number,user,other_user,mine_or_other,hand_number+1,i)
        if("otherhand" in hand_info):
            if(user ==1):
                mine_or_other = 2
            else:
                mine_or_other = 1
            for i in range(hand_info["otherhandnum"]):
                result_hand_eternal += self.check_hand_eternal_det_det(hand_info["otherhand"][i],hand_number,user,other_user,mine_or_other,hand_number+1,i)
        if("commonhand" in hand_info):
            for i in range(hand_info["commonhandnum"]):
                result_hand_eternal += self.check_hand_eternal_det_det(hand_info["commonhand"][i],hand_number,user,other_user,3,hand_number+1,i)
        return result_hand_eternal
    def check_hand_eternal_det_det(self,monster,hand_number,user,other_user,mine_or_other,hand_id,index):
        duel = self.duel
        room_number = self.room_number
        return_eternal = []
        monster_det = Monster.objects.get(id=monster["id"])
        eternals = monster_det.eternal_effect.all()
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for eternal in eternals:
            tmp["eternal"] = eternal.id
            tmp["effect_val"] = eternal.eternal_effect_val
            tmp["kind"] = eternal.eternal_kind
            tmp["priority"] = eternal.priority
            tmp["user"] = mine_or_other
            if "already" in monster:
                tmp["already"] = monster["already"]
            else:
                tmp["already"] = 0
            tmp["place"] =  "hand"
            tmp["place_id"] = place_id
            tmp["hand_id"] =  hand_id
            tmp["index"] =   index
            tmp["mine_or_other"] =   mine_or_other
            return_eternal.append(tmp)

        return return_eternal
    def check_grave_eternal(self,grave_info,count,user,other_user):
        result_grave_eternal = []
        for i in range(count):
            if grave_info[i]["eternal"] == False:
                continue
            result_grave_eternal += self.check_grave_eternal_det(grave_info[i],i,user,other_user)
        return result_grave_eternal
    def check_grave_eternal_det(self,grave_info,grave_number,user,other_user):
        result_grave_eternal = []
        if grave_info["eternal"] == False:
            return []
        if("mygrave" in grave_info):
            if(user == 1):
                mine_or_other = 1
            else:
                mine_or_other = 2
            for i in range(grave_info["mygravenum"]):
                result_grave_eternal += self.check_grave_eternal_det_det(grave_info["mygrave"][i],grave_number,user,other_user,mine_or_other,grave_number+1,i)
        if("othergrave" in grave_info):
            if user == 2:
                mine_or_other = 2
            else:
                mine_or_other = 1
            for i in range(grave_info["othergravenum"]):
                result_grave_eternal += self.check_grave_eternal_det_det(grave_info["othergrave"][i],grave_number,user,other_user,mine_or_other,grave_number+1,i)
        if("commongrave" in grave_info):
            for i in range(grave_info["commongravenum"]):
                result_grave_eternal += self.check_grave_eternal_det_det(grave_info["commongrave"][i],grave_number,user,other_user,3,grave_number+1,i)
        return result_grave_eternal
    def check_grave_eternal_det_det(self,monster,grave_number,user,other_user,mine_or_other,grave_id,i):
        duel = self.duel
        room_number = self.room_number
        return_eternal = []
        monster_det = Monster.objects.get(id=monster["id"])
        eternals = monster_det.eternal_effect.all()
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for eternal in eternals:
            kind = eternal.kind
            tmp["eternal"] = eternal.id
            tmp["effect_val"] = eternal.eternal_effect_val
            tmp["kind"] = eternal.eternal_kind
            tmp["priority"] = eternal.priority
            tmp["user"] = mine_or_other
            if "already" in monster:
                tmp["already"] = monster["already"]
            else:
                tmp["already"] = 0
            tmp["place"] =  "grave"
            tmp["grave_id"] =  grave_id
            tmp["index"] =   index
            tmp["place_id"] =   place_id
            tmp["mine_or_other"] =   mine_or_other

        return return_eternal
    def check_field_eternal(self,field,user,other_user):
        result_field_eternal = []
        for x in range(len(field)):
            for y in range(len(field[x])):
                if(field[x][y]["det"] is None):
                    continue
                if(field[x][y])["det"] is not None:
                    result_field_eternal += self.check_field_eternal_det(field[x][y]["det"],x,y,user,other_user,int(field[x][y]["mine_or_other"]))
        return result_field_eternal
    def check_deck_eternal(self,deck_info,count,user,other_user):
        result_deck_eternal =[]
        for i in range(count):
            if deck_info[i]["eternal"] == False:
                continue
            result_deck_eternal += self.check_deck_eternal_det(deck_info[i],i,user,other_user)
        return result_deck_eternal
    def check_deck_eternal_det(self,deck_info,deck_number,user,other_user):
        result_deck_eternal = []
        if("mydeck" in deck_info):
            if(user == 1):
                mine_or_other = 1
            else:
                mine_or_other = 2
            for i in range(deck_info["mydecknum"]):
                result_deck_eternal += self.check_deck_eternal_det_det(deck_info["mydeck"][i],deck_number,user,other_user,mine_or_other,deck_number+1,i)
        if("otherdeck" in deck_info):
            if(user ==1):
                mine_or_other = 2
            else:
                mine_or_other = 1
            for i in range(deck_info["otherdecknum"]):
                result_deck_eternal += self.check_deck_eternal_det_det(deck_info["otherdeck"][i],deck_number,user,other_user,mine_or_other,deck_number+1,i)
        if("commondeck" in deck_info):
            for i in range(deck_info["commondecknum"]):
                result_deck_eternal += self.check_deck_eternal_det_det(deck_info["commondeck"][i],deck_number,user,other_user,3,deck_number+1,i)
        return result_deck_eternal
    def check_deck_eternal_det_det(self,monster,deck_number,user,other_user,mine_or_other,deck_id,index):
        duel = self.duel
        room_number = self.room_number
        return_eternal = []
        monster_det = Monster.objects.get(id=monster["id"])
        eternals = monster_det.eternal_effect.all()
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for eternal in eternals:
            tmps = json.loads(eternal.eternal_monster)
            kind = eternal.eternal_kind
            tmps = tmps["monster"]
            tmp ={}
            tmp["eternal"] = eternal.id
            tmp["effect_val"] = eternal.eternal_effect_val
            tmp["kind"] = eternal.eternal_kind
            tmp["priority"] = eternal.priority
            tmp["user"] = mine_or_other
            if "already" in monster:
                tmp["already"] = monster["already"]
            else:
                tmp["already"] = 0
            tmp["place"] =  "deck"
            tmp["deck_id"] =  deck_id
            tmp["place_id"] =  place_id
            tmp["index"] =   index
            tmp["mine_or_other"] =   mine_or_other
            return_eternal.append(tmp)

        return return_eternal
    def modify_deck_info(self,deck_info,count,user,other_user,priority,mode = 0):
        for i in range(count):
            flag = self.modify_deck_info_det(deck_info[i],i,user,other_user,priority,mode)
            if(mode == 1 and flag):
                return True
        if(mode == 1):
            return False
        return deck_info
    def modify_deck_info_det(self,deck_info,deck_number,user,other_user,priority,mode = 0):
        if(deck_info["invoke"]== False):
            if mode == 1:
                return False
            else:
                return deck_info
        if("mydeck" in deck_info):
            if(self.user ==1):
                mine_or_other = 1
            else:
                mine_or_other = 2
            for i in range(deck_info["mydecknum"]):
                tmp = self.check_deck_trigger(deck_info["mydeck"][i],deck_number,user,other_user,mine_or_other,deck_number+1,priority,mode)
                if(mode == 1 and tmp == True):
                    return True
                elif(mode == 0):
                    deck_info["mydeck"][i] = tmp
        if("otherdeck" in deck_info):
            if(self.user ==1):
                mine_or_other = 2
            else:
                mine_or_other = 1
            for i in range(deck_info["otherdecknum"]):
                tmp= self.check_deck_trigger(deck_info["otherdeck"][i],deck_number,user,other_user,mine_or_other,deck_number+1,priority,mode)
                if(mode == 1 and tmp == True):
                    return True
                elif(mode == 0):
                    deck_info["otherdeck"][i] = tmp

        if("commondeck" in deck_info):
            for i in range(deck_info["commondecknum"]):
                tmp = self.check_deck_trigger(deck_info["commondeck"][i],deck_number,user,other_user,'0',deck_number+1,priority,mode)
                if(mode == 1 and tmp == True):
                    return True
                elif(mode == 0):
                    deck_info["commondeck"][i] = tmp
        if(mode == 1):
            return False

        return deck_info
    def modify_hand_info(self,hand_info,count,user,other_user,priority,mode=0):
        for i in range(count):
            tmp = self.modify_hand_info_det(hand_info[i],i,user,other_user,priority,mode)
            if mode == 1:
                if tmp == True:
                    return True
                else:
                    return False
            else:
                hand_info[i]  = tmp
        return hand_info
    def modify_hand_info_det(self,hand_info,hand_number,user,other_user,priority,mode=0):
        if(hand_info["invoke"]== False):
            if mode == 1:
                return False
            else:
                return hand_info
        if("myhand" in hand_info):
            if(self.user ==1):
                mine_or_other = 1
            else:
                mine_or_other = 2
            for i in range(hand_info["myhandnum"]):
                tmp = self.check_hand_trigger(hand_info["myhand"][i],hand_number,user,other_user,mine_or_other,hand_number+1,priority,mode)
                if mode == 1 and tmp == True:
                    return True
                else:
                    hand_info["myhand"][i] = tmp
        if("otherhand" in hand_info):
            if(self.user ==1):
                mine_or_other = 2
            else:
                mine_or_other = 1
            for i in range(hand_info["otherhandnum"]):
                tmp = self.check_hand_trigger(hand_info["otherhand"][i],hand_number,user,other_user,mine_or_other,hand_number+1,priority,mode)
                if mode == 1 and tmp == True:
                    return True
                else:
                    hand_info["otherhand"][i] = tmp
        if("commonhand" in hand_info):
            for i in range(hand_info["commonhandnum"]):
                tmp = self.check_hand_trigger(hand_info["commonhand"][i],hand_number,user,other_user,'0',hand_number+1,priority,mode)
                if mode == 1 and tmp == True:
                    return True
                else:
                    hand_info["commonhand"][i] = tmp
        if mode == 1:
            return False
        return hand_info
    def check_field_eternal_det(self,monster,x,y,user,other_user,mine_or_other):
        duel = self.duel
        monster_det = Monster.objects.get(id=monster["id"])
        eternals  = monster_det.eternal_effect.all()
        return_eternal = []
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for eternal in eternals:
            tmps = json.loads(eternal.eternal_monster)
            kind = eternal.eternal_kind
            tmps = tmps["monster"]
            tmp ={}
            tmp["monster"] = monster
            tmp["effect_val"] = eternal.eternal_effect_val
            tmp["priority"] = eternal.priority
            tmp["place"] = "field"
            tmp["user"] = mine_or_other
            tmp["x"] = "x"
            tmp["y"] = "y"
            tmp["place_id"] = place_id
            if "already" in monster:
                tmp["already"] = monster["already"]
            else:
                tmp["already"] = 0
            return_eternal.append(tmp)
        return return_eternal
    def check_field_trigger(self,monster,x,y,user,other_user,mine_or_other,priority,mode=0):
        duel = self.duel
        monster_det = Monster.objects.get(id=monster["id"])
        triggers  = monster_det.trigger.filter(priority = priority).all()
        return_trigger = []
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for trigger in triggers:
            if self.check_launch_trigger(trigger,phase,turn,user,other_user,mine_or_other,"field",place_id,0,x,y):
                if mode == 1:
                    return True
                tmp ={}
                tmp["id"] = trigger.id
                tmp["name"] = trigger.trigger_sentence
                return_trigger.append(tmp)
        if mode == 1:
            return False

        return return_trigger
    def check_deck_trigger(self,monster,deck_number,user,other_user,mine_or_other,deck_id,priority,mode = 0):
        duel = self.duel
        room_number = self.room_number
        return_trigger = []
        monster_det = Monster.objects.get(id=monster["id"])
        triggers  = monster_det.trigger.filter(priority = priority).all()
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for trigger in triggers:
            if self.check_launch_trigger(trigger,phase,turn,user,other_user,mine_or_other,"deck",place_id,deck_id):
                if mode == 1:
                    return True
                tmp ={}
                tmp["id"] = trigger.id
                tmp["name"] = trigger.trigger_sentence
                return_trigger.append(tmp)

        if mode == 1:
            return False
        monster["trigger"] = return_trigger
        return monster

    def check_hand_trigger(self,monster,hand_number,user,other_user,mine_or_other,deck_id,priority,mode=0):
        duel = self.duel
        room_number = self.room_number
        return_trigger = []
        monster_det = Monster.objects.get(id=monster["id"])
        triggers  = monster_det.trigger.filter(priority = priority).all()
        phase = duel.phase
        turn = duel.user_turn
        place_id = monster["place_unique_id"]
        for trigger in triggers:
            if self.check_launch_trigger(trigger,phase,turn,user,other_user,mine_or_other,"hand",place_id,deck_id):
                if mode == 1:
                    return True
                tmp ={}
                tmp["id"] = trigger.id
                tmp["name"] = trigger.trigger_sentence
                return_trigger.append(tmp)

        if mode == 1:
            return False
        monster["trigger"] = return_trigger
        return monster

    def check_launch_trigger(self,trigger,phase,turn,user,other_user,mine_or_other,place="",place_id="",deck_id=0,x=0,y=0,timing=False,move_from=None,place_from=None,deck_id_from=0,from_x=0,from_y=0):
        duel=self.duel
        chain = duel.chain
        mine_or_other = int(mine_or_other)
        mine_or_other2 = mine_or_other
        if user == 2:
            if mine_or_other == 1:
                mine_or_other2  = 2
            elif mine_or_other == 2:
                mine_or_other2  = 1
        if(trigger is None):
            return None
        effect_kind = trigger.trigger_kind
        if trigger.phase is not None and trigger.phase != phase:
            return None
        if trigger.mine_or_other == 2:
            if  mine_or_other2 != 2:
                return False;
        elif trigger.mine_or_other == 1:
            if  mine_or_other2 != 1:
                return False;

        if trigger.chain_kind == 0:
            if chain < trigger.chain:
                return None
        elif trigger.chain_kind == 1:
            if chain > trigger.chain:
                return None
        elif trigger.chain_kind == 2:
            if chain != trigger.chain:
                return None
        if move_from != None:
            if self.check_no_invoke(move_from,user,effect_kind,place_from,deck_id_from,from_x,from_y,1,1):
                return False
        if place != "":
            monster = self.get_monster(place,place_id,mine_or_other,user,deck_id,x,y)
            if self.check_no_invoke(monster["det"],user,effect_kind,place,deck_id,x,y,1,0):
                return False
        else:
            monster = None
        if self.check_trigger_monster(trigger,user,monster) == False:
            return False
        if trigger.trigger_timing == True and timing==False:
            return False
        if duel.timing != None:
            if not duel.timing in trigger.timing.all():
                return False
        elif trigger.none_timing == False:
                return False

        if self.check_trigger_condition(trigger,user,monster):
            return True
        else:
            return False

        return False

    def get_monster(self,place,place_id,mine_or_other,user,deck_id,x,y):
        duel = self.duel
        tmp2={}
        room_number = self.room_number
        if place == "field":
            field = self.field
            if(field[x][y]["det"]["place_unique_id"] != place_id):
                return "error"
            monster = field[x][y]["det"]
            tmp2["det"] = monster
            tmp2["place_id"] = monster["place_unique_id"]
            tmp2["mine_or_other"] =field[x][y]["mine_or_other"]
            tmp2["user"] = user
            tmp2["place"] = place
            tmp2["x"] = x
            tmp2["y"] = y
            tmp2["deck_id"] = field[x][y]["kind"]
            monster = tmp2
            return monster

        mine_or_other = int(mine_or_other)
        if (mine_or_other == 1 and self.user==1) or (mine_or_other == 2 and self.user != 1):
            mine_or_other2 = 1
        elif (mine_or_other == 2 and 1==self.user) or (mine_or_other == 1 and 2==self.user):
            mine_or_other2 = 2
        else:
            mine_or_other2 = 3
        mine_or_other = user

        if place == "deck":
            if mine_or_other2 == 1:
                deck = self.decks[deck_id]["mydeck"]
            elif mine_or_other2 == 2:
                deck = self.decks[deck_id]["otherdeck"]
            elif mine_or_other2 == 3:
                deck = self.decks[deck_id]["commondeck"]
            user_decks = deck
            for user_deck in user_decks:
                if place_id== user_deck["place_unique_id"]:
                    monster = user_deck
                    tmp2["det"] = monster
                    tmp2["place_id"] = monster["place_unique_id"]
                    tmp2["mine_or_other"] =mine_or_other
                    tmp2["user"] = user
                    tmp2["place"] = place
                    tmp2["deck_id"] = deck_id
                    tmp2["x"] = 0
                    tmp2["y"] = 0
                    monster = tmp2
                    return monster
        if place == "grave":
            if mine_or_other2 == 1:
                grave = self.graves[deck_id]["mygrave"]
            elif mine_or_other2 == 2:
                grave = self.graves[deck_id]["othergrave"]
            elif mine_or_other2 == 3:
                grave = self.graves[deck_id]["commongrave"]
            user_graves = grave
            for user_grave in user_graves:
                if place_id== user_grave["place_unique_id"]:
                    monster = user_grave
                    tmp2["det"] = monster
                    tmp2["place_id"] = monster["place_unique_id"]
                    tmp2["mine_or_other"] =mine_or_other
                    tmp2["user"] = user
                    tmp2["place"] = place
                    tmp2["deck_id"] = deck_id
                    tmp2["x"] = 0
                    tmp2["y"] = 0
                    monster = tmp2
                    return monster
        if place == "hand":
            if mine_or_other2 == 1:
                hand = self.hands[deck_id]["myhand"]
            elif mine_or_other2 == 2:
                hand = self.hands[deck_id]["otherhand"]
            elif mine_or_other2 == 3:
                hand = self.hands[deck_id]["commonhand"]
            user_hands = hand
            for user_hand in user_hands:
                if place_id== user_hand["place_unique_id"]:
                    monster = user_hand
                    tmp2["det"] = monster
                    tmp2["place_id"] = monster["place_unique_id"]
                    tmp2["mine_or_other"] =mine_or_other
                    tmp2["user"] = user
                    tmp2["place"] = place
                    tmp2["deck_id"] = deck_id
                    tmp2["x"] = 0
                    tmp2["y"] = 0
                    monster = tmp2
                    return monster
    def validate_answer(self,monster,effect_det,exclude,duel):
        cost =self.cost
        mess =self.mess
        if str(duel.chain) in cost:
            cost = cost[str(duel.chain)]
        else:
            cost = []
        if str(duel.chain) in mess:
            mess = mess[str(duel.chain-1)]
        else:
            mess= []

        timing_mess = self.timing_mess
        if(exclude !=""):
            excludes = exclude.split(",")
            for exclude_det in excludes:

                if exclude_det[0] == "~":
                    if exclude_det[1:] in cost:
                        for cost_det in cost[exclude_det[1:]]:
                            if(user_decks[index]["place_unique_id"] == cost_det["place_id"]):
                                continue
                if exclude_det[0] == "%":
                    if exclude_det[1:] in timing_mess:
                        for timing_det in timing_mess[exclude_det[1:]]:
                            if(user_decks[index]["place_unique_id"] == timing_det["place_id"]):
                                continue
                if exclude_det in mess:
                    for mess_det in mess[exclude_det]:
                        if(monster["place_unique_id"] == mess_det["place_id"]):
                            return False
        current_and_or = "and"
        monster_name_kind = effect_det["monster_name_kind"]
        for name_kind in monster_name_kind:
            if name_kind != "":
                if(name_kind["operator"] == "="):
                    if(monster["monster_name"] != self.get_name(name_kind["monster_name"])):
                        if(current_and_or == "and"):
                            name_flag = False
                    else:
                        if(current_and_or == "or"):
                            name_flag = True
                    current_and_or = name_kind["and_or"]


                elif(name_kind["operator"] == "like"):
                    if(monster["monster_name"].find(self.get_name(name_kind["monster_name"])) >-1):
                        if(current_and_or == "and"):
                            name_flag = False
                    else:
                        if(current_and_or == "or"):
                            name_flag = True
                    current_and_or = name_kind["and_or"]

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
                    if int(value) != self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "<="):
                    if int(value) > self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == ">="):
                    if int(value) < self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                elif(cond_val["operator"] == "!="):
                    if int(value) == self.calculate_boland(cond_val["num"]):
                        tmp_flag= False
                if current_and_or == "and":
                    if(cond_flag == True):
                        cond_flag = tmp_flag

                else:
                    if(cond_flag == False):
                        cond_flag = tmp_flag
            if(cond_flag == False):
                return False
        return True



    def check_trigger_timing_sql(self,trigger_timing_table,owner,chain_user,from_mine_or_other,to_mine_or_other):
        relative_owner = []
        relative_chain_user = []
        relative_from_mine_or_other = []
        relative_to_mine_or_other = []
        for type in range(5):
            if type == 0:
                user = owner
            elif type == 3:
                user = from_mine_or_other
            elif type == 4:
                user = to_mine_or_other
            elif type == 1:
                user = chain_user
            elif type == 2:
                if chain_user == 1:
                    user = 2
                elif chain_user == 2:
                    user = 1
            relative_from_mine_or_other.append(from_mine_or_other)
            if(user == 2 and from_mine_or_other == 2):
                relative_from_mine_or_other[type] = 1
            elif(user == 2 and from_mine_or_other == 1):
                relative_from_mine_or_other[type] = 2
            relative_to_mine_or_other.append(to_mine_or_other)
            if(user == 2 and to_mine_or_other == 2):
                relative_to_mine_or_other[type] = 1
            elif(user == 2 and to_mine_or_other == 1):
                relative_to_mine_or_other[type] = 2
            relative_chain_user.append(chain_user)
            if(user == 2 and chain_user == 2):
                relative_chain_user[type] = 1
            elif(user == 2 and chain_user == 1):
                relative_chain_user[type] = 2
        return_value= trigger_timing_table.filter( \
            ((Q(from_mine_or_other=relative_from_mine_or_other[0]) | Q(from_mine_or_other=0) & Q(to_mine_or_other=relative_to_mine_or_other[0]) | Q(to_mine_or_other=0)) & Q(who=0)) \
            | ((Q(from_mine_or_other=relative_from_mine_or_other[1]) | Q(from_mine_or_other=0) & Q(to_mine_or_other=relative_to_mine_or_other[1]) | Q(to_mine_or_other=0)) & Q(who=1)) \
            | ((Q(from_mine_or_other=relative_from_mine_or_other[2]) | Q(from_mine_or_other=0) & Q(to_mine_or_other=relative_to_mine_or_other[2]) | Q(to_mine_or_other=0)) & Q(who=2)) \
            | ((Q(from_mine_or_other=relative_from_mine_or_other[3]) | Q(from_mine_or_other=0) & Q(to_mine_or_other=relative_to_mine_or_other[3]) | Q(to_mine_or_other=0)) & Q(who=3)) \
            | ((Q(from_mine_or_other=relative_from_mine_or_other[4]) | Q(from_mine_or_other=0) & Q(to_mine_or_other=relative_to_mine_or_other[4]) | Q(to_mine_or_other=0)) & Q(who=4)))
        return return_value
    def raise_trigger(self,move_to,move_from,cost_or_effect,place_to,chain_user,to_mine_or_other,to_deck_id,effect_kind,x=None,y=None):
        duel = self.duel
        if cost_or_effect == "effect":
            cost_or_effect = 2
        elif cost_or_effect == "cost":
            cost_or_effect = 1
        else:
            cost_or_effect = 0
        place_from = move_from["place"]
        owner = move_from["owner"]
        from_mine_or_other = move_from["user"]
        if place_from == "deck" :
            from_place_kind = 1
        elif place_from == "grave" :
            from_place_kind = 2
        elif place_from == "hand" :
            from_place_kind = 3
        elif place_from == "field" :
            from_place_kind = 4
        else:
            from_place_kind = 0
        timing = TriggerTiming.objects.filter(Q(from_place_kind = from_place_kind) | Q(from_place_kind = 0))
        monster_id = move_to["id"]
        timing = timing.filter(monster__id = monster_id)
        timing = self.check_trigger_timing_sql(timing,owner,chain_user,from_mine_or_other,to_mine_or_other)
        timing = timing.filter(Q(cost_or_effect= cost_or_effect) | Q(cost_or_effect = 0))
        if(place_from == "deck"):
            from_x = 0
            from_y = 0
            from_deck_id = move_from["deck_id"]
            timing = timing.filter(Q(from_deck__id = from_deck_id) | Q(from_place_kind=0))
        elif(place_from == "grave"):
            from_x = 0
            from_y = 0
            from_grave_id = move_from["grave_id"]
            from_deck_id = from_grave_id
            timing = timing.filter(Q(from_grave__id = from_grave_id) | Q(from_place_kind=0))
        elif(place_from == "hand"):
            from_x = 0
            from_y = 0
            from_hand_id = move_from["hand_id"]
            from_deck_id = from_hand_id
            timing = timing.filter(Q(from_hand__id = from_hand_id) | Q(from_place_kind=0))
        elif(place_from == "field"):
            from_x = move_from["x"]
            from_y = move_from["y"]
            field = self.field
            from_deck_id = 0
            kinds = field[from_x][from_y]["kind"]
            kinds = kinds.split("_")
            queries = [Q(from_field__id = int(from_field)) for from_field in kinds]
            query = queries.pop()
            for item in queries:
                query |= item
            timing.filter(query)
        if place_to == "deck" :
            to_place_kind = 1
        elif place_to == "grave" :
            to_place_kind = 2
        elif place_to == "hand" :
            to_place_kind = 3
        elif place_to == "field" :
            to_place_kind = 4
        else:
            to_place_kind = 0
        timing = timing.filter(Q(to_place_kind = to_place_kind) | Q(to_place_kind = 0))
        if(place_to == "deck"):
            to_deck_id = to_deck_id
            timing = timing.filter(Q(to_deck__id = to_deck_id) | Q(to_place_kind=0))
        elif(place_to == "grave"):
            to_grave_id =  to_deck_id
            timing = timing.filter(Q(to_grave__id = to_grave_id) | Q(to_place_kind=0))
        elif(place_to == "hand"):
            to_hand_id =  to_deck_id
            timing = timing.filter(Q(to_hand__id = to_hand_id) | Q(to_place_kind=0))
        elif(place_to == "field"):
            field = self.field
            kinds = field[x][y]["kind"]
            kinds = kinds.split("_")
            queries = [Q(to_field__id = int(to_field)) for to_field in kinds]
            query = queries.pop()
            for item in queries:
                query |= item
            timing.filter(query)
        timings = timing.all()

        if(duel.trigger_waiting == ""):
            trigger_waiting = []
        else:
            trigger_waiting = json.loads(duel.trigger_waiting)
        if effect_kind:
            from_kinds = effect_kind
        else:
            from_kinds = []
        for timing in timings:
            timing_kinds = timing.kinds
            if timing_kinds != "":
                timing_kinds = timing_kinds.split("_")
                kind_flag = True
                for timing_kind in timing_kinds:
                    if timing_kind not in from_kinds:
                        kind_flag = False
                        break
                if kind_flag == False:
                    continue
            if timing.who == 0:
                user = owner
            elif timing.who == 1:
                user = chain_user
            elif timing.who == 2:
                if chain_user == 1:
                    user = 2
                elif chain_user == 2:
                    user = 1
            elif timing.who == 3:
                user = from_mine_or_other
            elif timing.who == 4:
                user = to_mine_or_other
            tmp = {}
            tmp["monster"] = move_to
            tmp["move_from"] = move_from
            tmp["trigger"] = timing.trigger.id
            tmp["priority"] = timing.trigger.priority
            tmp["mine_or_other"] = to_mine_or_other
            tmp["user"] = user
            tmp["place"] = place_to
            tmp["deck_id"] = to_deck_id
            tmp["x"] = x
            tmp["y"] = y
            tmp["from_x"] = from_x
            tmp["from_y"] = from_y
            tmp["place_from"] = place_from
            tmp["deck_id_from"] = from_deck_id
            trigger_waiting.append(tmp)
        duel.trigger_waiting = json.dumps(trigger_waiting)
    def invoke_trigger_waiting(self,trigger_waiting):
        duel = self.duel
        duel.in_trigger_waiting = True
        flag = True
        trigger_waitings = json.loads(trigger_waiting)
        trigger_waitings.sort(key=lambda x:x["priority"],reverse=True)

        count = 0
        for  trigger_waiting in trigger_waitings:
            trigger = Trigger.objects.get(id = trigger_waiting["trigger"])
            monster = trigger_waiting["monster"]
            if "move_from" in trigger_waiting:
                move_from = trigger_waiting["move_from"]
            else:
                move_from = None
            if monster:
                place_id = monster["place_unique_id"]
            else:
                place_id= None
            user = trigger_waiting["user"]
            mine_or_other = str(trigger_waiting["mine_or_other"])
            place = trigger_waiting["place"]
            deck_id = trigger_waiting["deck_id"]
            place_from = trigger_waiting["place_from"]
            deck_id_from = trigger_waiting["deck_id_from"]
            x = trigger_waiting["x"]
            y = trigger_waiting["y"]
            from_x= trigger_waiting["x"]
            from_y= trigger_waiting["y"]
            if user == 1:
                other_user =2
            else:
                other_user =1

            count+=1
            if self.check_launch_trigger(trigger,duel.phase,duel.user_turn,user,other_user,mine_or_other,place,place_id,deck_id,x,y,True,move_from,place_from,deck_id_from,from_x,from_y):
                self.invoke_trigger(trigger,place,monster,mine_or_other,user,deck_id )
        duel.trigger_waiting = "[]"
        if flag == True:
            duel.in_trigger_waiting = False
    def get_variables(self):
        duel = self.duel
        global_variables = json.loads(duel.global_variable)
        virtual_variables = self.virtual_variables
        global_variables.update(virtual_variables)
        return global_variables

