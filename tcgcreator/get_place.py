from .models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,Field,UserDeck,UserDeckGroup,Deck,UserDeck,UserDeckGroup,UserDeckChoice,Duel,Phase,Trigger,Grave
from django.http import HttpResponse,HttpResponseRedirect
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_user_deck_det
from django.db.models import Q
from django.shortcuts import render
import json

