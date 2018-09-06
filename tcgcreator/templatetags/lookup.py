from django import template
from pprint import pprint
from django.utils.html import escape
from ..models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Duel,Phase,UserDeck,UserDeckGroup
register = template.Library()

@register.filter(name='monsteritem')
def monsteritem(id):
	monsteritems = MonsterItem.objects.all().filter(monster_id__id = id).order_by('-monster_variables_id__priority').select_related('monster_variables_id').select_related('monster_variables_id__monster_variable_kind_id')
	result_array = []
	for monsteritem in monsteritems:
		tmp = {}
		tmp["priority"] = monsteritem.monster_variables_id.priority
		if(monsteritem.monster_variables_id.monster_variable_kind_id.id <2):
			tmp["str"] = monsteritem.monster_item_text
		else:
			tmp2 = monsteritem.monster_item_text.split("_")
			tmp["str"] = ""
			for tmp3 in tmp2:
				tmp4 = monsteritem.monster_variables_id.monster_variable_kind_id.monster_variable_sentence.split("|")
				tmp["str"] += tmp4[int(tmp3)-1]
		result_array.append(tmp)
	sorted(result_array,key=lambda x:x["priority"])	
	return_value = ""
	for tmp5 in result_array:
		return_value += tmp5["str"]+"/"
	return return_value

@register.filter(name='split')
def split(value):
	return value.split('|')
@register.filter(name='split2')
def split_for_monster(value):
	tmp= value.split('_')
	tmp = sorted(tmp)
	return tmp

@register.filter(name='lookupmonstervariableint')
def lookupmonstervariableint(value, arg, default=0):
	tmp=value.get("monster_variable"+str(arg))
	if(tmp == None):
		return default
	else:
		return int(tmp)
@register.filter(name='lookupmonstervariable')
def lookupmonstervariable(value, arg, default=""):
	tmp=value.get("monster_variable"+str(arg))
	if(tmp == None):
		return default
	else:
		return tmp
	
@register.filter(name='lookuphow')
def lookuphow(value, arg, default=""):
    return value.get(str(arg)+"_how")
@register.filter(name='lookup')
def lookup(value, arg, default=""):
    if arg in value:
        return value[arg]
    else:
        return default
@register.filter(name='lookuplist')
def lookuplist(value, arg, default=""):
	return value[arg]
@register.filter(name='joincomma')
def joincomma(arg, value, default=""):
	return arg,value
@register.filter(name='lookup2')
def lookup2(arg, value, default=""):
	arg1,arg2 = arg
	tmp2 = arg2.split(",")
	tmp = value[int(arg1)].split("|")
	return_value = ""
	for tmp3 in tmp2:
		return_value += tmp[int(tmp3)-1];
	return return_value
@register.filter(name='lookup3')
def lookup3(arg, value, default=""):
	arg1,arg2 = arg
	tmp2 = arg2.split(",")
	tmp = value[arg1].split("|")
	return_value = ""
	for tmp3 in tmp2:
		return_value += tmp[int(tmp3)-1];
	return return_value
@register.filter(name='get_user_deck')
def get_user_deck(user_deck,arg):
	user_deck=user_deck.filter(deck_type=arg).first()
	if(user_deck.deck == ""):
		return "</div>"
	deck_det = user_deck.deck.split("_")
	return_value= "現在枚数"+str(len(deck_det))+"枚</div>"
	for deck_det_det in deck_det:
		monster = Monster.objects.filter(id = int(deck_det_det)).first()
		monster_items = MonsterItem.objects.filter(monster_id = monster).select_related('monster_variables_id').select_related('monster_variables_id__monster_variable_kind_id')

		return_value += '''
		<input type="checkbox" value="{monster_id}" name="exclude_monster_deck_{arg}">
	<a target="_blank"  title="" href="/tcgcreator/explain?id={monster_id}">{monster_name}
'''.format(monster_id=monster.id,monster_name=escape(monster.monster_name),arg=arg.id)
		for monster_item in monster_items:
				
			if monster_item.monster_variables_id.monster_variable_kind_id.id < 2:
				show = escape(monster_item.monster_item_text)
			else:
				monster_item_text =int(monster_item.monster_item_text)
				tmp = monster_item.monster_variables_id.monster_variable_kind_id.monster_variable_sentence
				tmp = tmp.split("|")
				show = tmp[int(monster_item_text)-1]
			return_value += '/'+show
				
		return_value += '''
		</a><span style="color:red"></span><br>
'''
	return return_value
@register.filter(name='get_field')
def get_field(y,x):
	field = Field.objects.filter(x=x,y=y).first()
	return_value=field.kind.split("_")
	return return_value
	

