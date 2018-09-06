from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,UserDeckChoice,Deck,DefaultDeckGroup,DefaultDeckChoice,DefaultDeck
from django.http import HttpResponse,HttpResponseRedirect
import json
import uuid
import numpy as np
from pprint import pprint
def init_monster_item(monster_variable):
    monster = Monster.objects.all()
    for tmp in monster:
        monster_item = MonsterItem(monster_id = tmp,monster_variables_id=monster_variable,monster_item_text = monster_variable.default_value)

        monster_item.save();

def init_field(x,y):
    Field.objects.all().delete()
    for tmp_x in range(0,int(x)):
        for tmp_y in range(0,int(y)):
            field = Field(x = tmp_x,y = tmp_y,kind = "",mine_or_other = 0)
            field.save()
def create_user_deck(user_id,deck_id,deck_group,default_deck_group_id):
    default_deck_group_id = int(default_deck_group_id)
    default_deck = DefaultDeckGroup.objects.all().get(default_deck_id = default_deck_group_id)
    default_deck = DefaultDeck.objects.all().get(deck_type = deck_id,deck_group = default_deck)
    deck = default_deck.deck

    user_deck = UserDeck(user=user_id,deck_type = deck_id,deck=default_deck.deck,deck_group=deck_group)
    user_deck.save()
def create_user_deck_group(deck_group,user_id,deck_name):
    user_deck = UserDeckGroup(user_deck_id=deck_group,user=user_id,deck_name = deck_name)
    user_deck.save()
def create_user_deck_choice(deck_group,user_id):
    user_deck = UserDeckChoice(user=user_id,user_deck=deck_group)
    user_deck.save()
def create_default_deck(deck_id,deck_group):
    default_deck = DefaultDeck(deck_type = deck_id,deck="",deck_group=deck_group)
    default_deck.save()
def create_default_deck_group(deck_group,deck_name):
    default_deck = DefaultDeckGroup(default_deck_id=deck_group,deck_name = deck_name)
    default_deck.save()
def create_default_deck_choice(deck_group):
    default_deck = DefaultDeckChoice(default_deck=deck_group)
    default_deck.save()

def copy_to_default_deck(post,deck_group):
    decks = Deck.objects.all()
    all_decks=[]
    result_decks = []
    default_decks = DefaultDeck.objects.filter(deck_group=deck_group)
    for deck in decks:
        result_deck = []
        default_deck = default_decks.filter(deck_type_id=deck.id).first()
        exclude_deck = post.getlist("exclude_monster_deck_"+str(deck.id))
        default_deck_array = default_deck.deck.split("_")
        for exclude_deck_det in exclude_deck:
            try:
                default_deck_array.remove(exclude_deck_det)
            except ValueError:
                pass
        if(len(default_deck_array) != 0 and default_deck_array[0] != ""):
            result_deck.extend(default_deck_array)
            all_decks.extend(default_deck_array)
        add_deck = post.getlist("monster_deck_"+str(deck.id))
        if(len(add_deck) != 0):
            all_decks.extend(add_deck)
            result_deck.extend(add_deck)
        result_deck = sorted(result_deck)
        if(default_deck.deck== ""):

            default_deck_size = 0
        else:
            default_deck_size = len(default_deck_array)
        add_deck_size = len(add_deck)
        if(deck.max_deck_size < add_deck_size + default_deck_size):
            return "デッキ枚数が多すぎます"
        result_decks.append(result_deck)

    all_decks=sorted(all_decks)
    tmp=0
    for all_deck in all_decks:
        if all_deck != tmp:
            tmp = all_deck
            monster = Monster.objects.filter(id=int(all_deck)).first()
            if all_decks.count(all_deck)>monster.monster_limit:
                return monster.monster_name+"の制限を違反しています"

    i=0
    for deck in decks:
        default_deck = default_decks.filter(deck_type_id=deck.id).first()
        default_deck.deck = "_".join(result_decks[i])
        default_deck.save()
        i+=1;
    return ""
def copy_to_deck(user_id,post,deck_group):
    decks = Deck.objects.all()
    all_decks=[]
    result_decks = []
    user_decks = UserDeck.objects.filter(user=user_id,deck_group=deck_group)
    for deck in decks:
        result_deck = []
        user_deck = user_decks.filter(deck_type_id=deck.id).first()
        exclude_deck = post.getlist("exclude_monster_deck_"+str(deck.id))
        user_deck_array = user_deck.deck.split("_")
        for exclude_deck_det in exclude_deck:
            try:
                user_deck_array.remove(exclude_deck_det)
            except ValueError:
                pass
        if(len(user_deck_array) != 0 and user_deck_array[0] != ""):
            result_deck.extend(user_deck_array)
            all_decks.extend(user_deck_array)
        add_deck = post.getlist("monster_deck_"+str(deck.id))
        if(len(add_deck) != 0):
            all_decks.extend(add_deck)
            result_deck.extend(add_deck)
        result_deck = sorted(result_deck)
        if(user_deck.deck== ""):

            user_deck_size = 0
        else:
            user_deck_size = len(user_deck_array)
        add_deck_size = len(add_deck)
        if(deck.max_deck_size < add_deck_size + user_deck_size):
            return "デッキ枚数が多すぎます"
        result_decks.append(result_deck)

    all_decks=sorted(all_decks)
    tmp=0
    for all_deck in all_decks:
        if all_deck != tmp:
            tmp = all_deck
            monster = Monster.objects.filter(id=int(all_deck)).first()
            if all_decks.count(all_deck)>monster.monster_limit:
                return monster.monster_name+"の制限を違反しています"

    i=0
    for deck in decks:
        user_deck = user_decks.filter(deck_type_id=deck.id).first()
        user_deck.deck = "_".join(result_decks[i])
        user_deck.save()
        i+=1;
    return ""
def create_user_deck_det(user_deck,deck_id,owner):
    ids= user_deck.split("_")
    return_value = []
    if(user_deck == ""):
        return return_value
    for id in ids:
        tmp = {}
        tmp6 ={}
 
        monster = Monster.objects.filter(id = int(id)).first()
        tmp["flag"] = 0
        tmp["monster_name"] = monster.monster_name
        tmp["id"] = monster.id
        tmp["monster_sentence"] = monster.monster_sentence
        tmp["img"] = monster.img
        monsteritems = MonsterItem.objects.all().filter(monster_id__id = id).order_by('-monster_variables_id__priority').select_related('monster_variables_id').select_related('monster_variables_id__monster_variable_kind_id')

        for monsteritem in monsteritems:
            tmp5={}
            monster_variable= monsteritem.monster_variables_id
            tmp5["name"] = monster_variable.monster_variable_name
            tmp5["value"] = monsteritem.monster_item_text
            tmp5["i_val"] = monsteritem.monster_item_text
            tmp5["i_i_val"] = monsteritem.monster_item_text
            tmp2 = monsteritem.monster_item_text.split("_")
            if(monster_variable.monster_variable_kind_id.id <2):
                tmp5["str"] = tmp5["value"]
            else:
                tmp5["str"] = ""
                for tmp3 in tmp2:
                    tmp4 = monster_variable.monster_variable_kind_id.monster_variable_sentence.split("|")
                    tmp5["str"] += tmp4[int(tmp3)-1]
            tmp6[monster_variable.monster_variable_name] = tmp5
        tmp["variables"] = tmp6
        tmp["place"] = "deck";
        tmp["noeffect"] = "";
        tmp["nochoose"] = "";
        tmp["owner"] = owner;
        tmp["deck_id"] = deck_id;
        tmp["card_unique_id"] = str(uuid.uuid4())
        tmp["place_unique_id"] = str(uuid.uuid4())

        return_value.append(tmp)
    np.random.shuffle(return_value)
    return json.dumps(return_value)
