
from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,Deck,UserDeck,UserDeckGroup,UserDeckChoice,Duel,Phase,Trigger,Grave,DuelGrave
from django.http import HttpResponse,HttpResponseRedirect
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_user_deck_det
from django.db.models import Q
from django.shortcuts import render
import json
def explain_grave(request):
	room_number = int(request.GET["room_number"])
	grave_number = int(request.GET["grave"])
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
	graves = Grave.objects.all()
	for grave in graves:
		if(grave_number == i):
			if(grave.mine_or_other == 1):
				if(grave.show >= 1):
					tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = 3,grave_id = (i+1)).first()
					tmp = json.loads(tmp.grave_content)
				else:
					return HttpResponse("error")
			else:
				if(grave.show >= 1  and int(request.GET["user_number"])==user):
					tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = 1,grave_id = (i+1)).first()
					tmp = json.loads(tmp.grave_content)
				elif(grave.show >= 2  ):
					tmp = DuelGrave.objects.filter(room_number = room_number,mine_or_other = 2,grave_id = (i+1)).first()
					tmp = json.loads(tmp.grave_content)
				else:
					return HttpResponse("error")
		i+=1;
			
	return render(request,'tcgcreator/explain_grave.html',{'graves_obj':tmp})
