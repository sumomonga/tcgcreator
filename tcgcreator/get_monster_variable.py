from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.template.response import TemplateResponse
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.views.generic import View
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Duel,Phase,UserDeck,UserDeckGroup,Config,GlobalVariable,MonsterEffect,MonsterEffectWrapper
from .forms import EditMonsterVariablesForm,EditMonsterForm,EditMonsterItemForm
from .forms import EditMonsterVariablesKindForm,forms
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck
from pprint import pprint
from django.db.models import Prefetch,Max
import json

def get_monster_variable(request):
	result = [];
	monster_variables = MonsterVariables.objects.order_by('-priority')
	for monster_variable in monster_variables:
		tmp={}
		monster_variable_kind = monster_variable.monster_variable_kind_id
		tmp["variable_id"] = monster_variable_kind.id
		tmp["variable_name"] = monster_variable_kind.monster_variable_name;
		if(monster_variable_kind.id != 1):
			variable_sentence = monster_variable_kind.monster_variable_sentence
			tmp["sentence"] = variable_sentence.split("_")
		result.append(tmp)
				
	return HttpResponse(json.dumps(result))

