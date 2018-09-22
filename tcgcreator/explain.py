
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,Deck,UserDeck,UserDeckGroup,UserDeckChoice,Duel,Phase,Trigger,Grave,DuelDeck
from django.http import HttpResponse,HttpResponseRedirect
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_user_deck_det
from django.db.models import Q
from django.shortcuts import render
import json
from pprint import pprint
def explain(request):
	if "id" not in request.GET:
		HttpResponse("error")
	monster_id = request.GET["id"];
	monster = Monster.objects.get(id=monster_id)
	img_url = monster.img
			
	return render(request,'tcgcreator/explain.html',{'img_url':img_url})
