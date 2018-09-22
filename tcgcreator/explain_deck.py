
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,Deck,UserDeck,UserDeckGroup,UserDeckChoice,Duel,Phase,Trigger,Grave,DuelDeck
from django.http import HttpResponse,HttpResponseRedirect
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_user_deck_det
from django.db.models import Q
from django.shortcuts import render
import json
from pprint import pprint
def explain_deck(request):
	room_number = int(request.GET["room_number"])
	deck_number = int(request.GET["deck"])
	duel=Duel.objects.all().get(id=room_number);
	user_1 = duel.user_1
	user_2 = duel.user_2
	if(request.user != user_1 and request.user != user_2):
		return HttpResponse("error")
	if(request.user == user_1):
		user = 1
		other_user = 2
	if(request.user == user_2):
		user = 2
		other_user = 1
	i=0
	decks = Deck.objects.all()
	for deck in decks:
		if(deck_number == i):
			if(deck.mine_or_other == 1):
				if(deck.show >= 1):
					tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = 3,deck_id = (i+1)).first()
					tmp = json.loads(tmp.deck_content)
				else:
					return HttpResponse("error")
			else:
				if(deck.show >= 1  and int(request.GET["user_number"])==user):
					tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other =user,deck_id = (i+1)).first()
					tmp = json.loads(tmp.deck_content)
				elif(deck.show >= 2  ):
					tmp = DuelDeck.objects.filter(room_number = room_number,mine_or_other = other_user,deck_id = (i+1)).first()
					tmp = json.loads(tmp.deck_content)
				else:
					return HttpResponse("error")
		i+=1;
			
	return render(request,'tcgcreator/explain_deck.html',{'decks_obj':tmp})
