from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.views.generic import View
from tcgcreator.models import MonsterVariables,MonsterVariablesKind,MonsterItem,Monster,FieldKind,MonsterEffectKind,FieldSize,Field,Deck,Grave,Hand,FieldKind,Phase,UserDeck,UserDeckGroup,Duel,UserDeckChoice,GlobalVariable,DuelDeck,DuelGrave,DuelHand,DefaultDeckGroup,DefaultDeckChoice,DefaultDeck,Trigger,Timing,Pac,Config
from .forms import EditMonsterVariablesForm,EditMonsterForm,EditMonsterItemForm,UserForm
from .forms import EditMonsterVariablesKindForm,forms
from .custom_functions  import init_monster_item,create_user_deck,create_user_deck_group,copy_to_deck,create_user_deck_choice,create_default_deck,create_default_deck_group,copy_to_default_deck,create_default_deck_choice
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .battle_functions  import init_duel,check_user_deck,check_in_other_room
from pprint import pprint
from django.db.models import Prefetch,Max
from time import time
from django.db.models import Q

import json
# Create your views here.
def monster(request):
    monster = Monster.objects.all()
    monster_item = MonsterItem()
    monster_variables = MonsterVariables.objects.order_by('-priority')
    tmps_val = {}
    tmps_sentence = {}
    tmps = {}
#	for tmp_val in monster_variables:
#		tmps_val[tmp_val.id]=(tmp_val.monster_variable_label)
    monster_variables_kind = MonsterVariablesKind.objects.all()
    for tmp_val in monster_variables_kind:
        tmps_sentence[tmp_val.id]=(tmp_val.monster_variable_sentence)
        tmps[tmp_val.id]=(tmp_val.monster_variable_name)
    return render(request,'tcgcreator/monster.html',{'Monster':monster,'MonsterItem':monster_item,'MonsterVariables':monster_variables,'MonsterVariablesSentences':tmps_sentence,'monster_variable_kind':tmps})

def monster_variables(request):
    monster_variables = MonsterVariables.objects.all()
    monster_variables_kind = MonsterVariablesKind.objects.all()
    tmps = {}
    tmps_sentence = {}
    for tmp in monster_variables_kind:
        tmps[tmp.id]=(tmp.monster_variable_name)
    monster_variables_kind = MonsterVariablesKind.objects.all()
    for tmp_val in monster_variables_kind:
        tmps_sentence[tmp_val.id]=(tmp_val.monster_variable_sentence)
    return render(request,'tcgcreator/monster_variables.html',{'MonsterVariables':monster_variables,'monster_variable_kind':tmps,'MonsterVariablesSentences':tmps_sentence,})
def edit_monster_variables(request,monster_variables_id):
    monster_variable = get_object_or_404(MonsterVariables,id=monster_variables_id)
    if request.method == 'POST':
        form = EditMonsterVariablesForm(request.POST,instance=monster_variable)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('monster_variables'))
    else:
        form = EditMonsterVariablesForm(instance=monster_variable)
        context = {'form':form,'monster_variable':monster_variable}
        return TemplateResponse(request,'tcgcreator/edit_monster_variables.html',context=context)

def monster_variables_kind(request):
    monster_variables_kind = MonsterVariablesKind.objects.all()
    return render(request,'tcgcreator/monster_variables_kind.html',{'MonsterVariablesKind':monster_variables_kind})

def edit_monster_variables_kind(request,monster_variables_kind_id):
    monster_variables_kind = get_object_or_404(MonsterVariablesKind,id=monster_variables_kind_id)
    if request.method == 'POST':
        form = EditMonsterVariablesKindForm(request.POST,instance=monster_variables_kind)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('monster_variables_kind'))
    else:
        form = EditMonsterVariablesKindForm(instance=monster_variables_kind)
        context = {'form':form,'monster_variables_kind':monster_variables_kind}
        return TemplateResponse(request,'tcgcreator/edit_monster_variables_kind.html',context=context)

def new_monster_variables_kind(request):
    if request.method == 'POST':
        form = EditMonsterVariablesKindForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('monster_variables_kind'))
    else:
        form = EditMonsterVariablesKindForm()
        context = {'form':form}
        return TemplateResponse(request,'tcgcreator/new_monster_variables_kind.html',context=context)

def new_monster_variables(request):
    if request.method == 'POST':
        form = EditMonsterVariablesForm(request.POST)
        if form.is_valid():
            tmp = form.save()
            init_monster_item(request.POST,tmp)
            return HttpResponseRedirect(reverse('monster_variables'))
    else:
        form = EditMonsterVariablesForm()
        context = {'form':form}
        return TemplateResponse(request,'tcgcreator/new_monster_variables.html',context=context)

def new_monster(request):
    if request.method == 'POST':
        form = EditMonsterForm(request.POST)
        if form.is_valid():
            monster = form.save()
            monster_variables = MonsterVariables.objects.order_by('-priority')
            for tmp_val in monster_variables:
                formitem = EditMonsterItemForm(request.POST,prefix=tmp_val.id)
                monster_item = MonsterItem()
                monster_item.monster_item_text = request.POST[str(tmp_val.id)+"-monster_item_text"]
                monster_item.monster_variables_id = tmp_val
                monster_item.monster_id = monster;
                monster_item.save();
            return HttpResponseRedirect(reverse('monster'))

    else:
        form = EditMonsterForm()
        monster_variables = MonsterVariables.objects.order_by('-priority')
        formitems = []
        for tmp_val in monster_variables:
            formitem = EditMonsterItemForm(prefix=tmp_val.id,initial={"monster_variables_id" : tmp_val})
            formitem.fields['monster_item_text'].widget = forms.HiddenInput()
            formitem.fields['monster_variables_id'].widget = forms.HiddenInput()
            formitem.fields['monster_id'].widget = forms.HiddenInput()
            formitem.fields['monster_id'].widget.attrs['disabled']  = 'disabled'
            formitems.append(formitem)
        context = {'form':form,'formitems':formitems}
        return TemplateResponse(request,'tcgcreator/new_monster.html',context=context)

# MonsterItemの種類を取得
def get_monster_kind_type(req):
    monster_variable_kind_id = req.POST["monster_variable_kind_id"]
    if monster_variable_kind_id == "" or monster_variable_kind_id == "1":
        return HttpResponse('<input type="number" id="id_default_value" name="default_value" required>')
    monster_variable_kind = MonsterVariablesKind.objects.filter(id=monster_variable_kind_id)
    for tmp2 in monster_variable_kind:
        monster_variable_kind = tmp2
    tmp = monster_variable_kind.monster_variable_sentence.split("|")
    if(req.POST["delete_flag"]=="1"):
        result = '<select id="id_default_value" name="default_value" onchange="deleteItem('+req.POST["delete_num"]+')">'
    else:
        result = '<select id="id_default_value" name="default_value">'
    i=1
    for tmp_val in tmp:
        result += '<option value="' + str(i)+ '">'+tmp_val+'</option>'
        i+=1
    result+= '</select>'
    return HttpResponse(result)

def get_monster_kind_type_for_new_monster(req):
    prefix = req.POST["prefix"]
    tmp = int(prefix)+1
    monster_variable = MonsterVariables.objects.all().filter(id=tmp)
    if not monster_variable:
        return HttpResponse('<input type="number" id="id_'+prefix+'-monster_item_text" name="default_value" required>$1')

    monster_variable_kind_id = str(monster_variable[0].monster_variable_kind_id.id)
    variable_name = monster_variable[0].monster_variable_name;

    num = req.POST["num"]
    if monster_variable_kind_id == "" or monster_variable_kind_id == "1":
        return HttpResponse('<input type="number" id="id_'+prefix+'-monster_item_text" name="default_value" required>$1$'+variable_name)
    monster_variable_kind = MonsterVariablesKind.objects.filter(id=monster_variable_kind_id)

    for tmp2 in monster_variable_kind:
        monster_variable_kind = tmp2
    tmp = monster_variable_kind.monster_variable_sentence.split("|")
    if(req.POST["delete_flag"]=="0"):
        result = '<select id="'+prefix+'-monster_item_text_'+num+'" name="'+prefix+'-monster_item_text_'+num+'" onchange="changeItemNum('+prefix+')">'
    i=1
    for tmp_val in tmp:
        result += '<option value="' + str(i)+ '">'+tmp_val+'</option>'
        i+=1
    result+= '</select>'
    return HttpResponse(result+"$"+monster_variable_kind_id+"$"+variable_name)

def get_field_kind(req):
    field_kind = FieldKind.objects.all()
    if not field_kind:
        return HttpResponse('')
    num = req.POST["num"]
    tmp = []
    for tmp2 in field_kind:
        tmp.append(tmp2.field_kind_name)
    result = '<select id="field_kind-'+num+'" name="field_kind-'+num+'" onchange="changeFieldNum()">'
    i=1
    for tmp_val in tmp:
        result += '<option value="' + str(i)+ '">'+tmp_val+'</option>'
        i+=1
    result+= '</select>'
    return HttpResponse(result)

def get_invalid_monster_kind(req):

    monster_kind = MonsterEffectKind.objects.all()
    if not monster_kind:
        return HttpResponse('')
    num = req.POST["num"]
    tmp = []
    for tmp2 in monster_kind:
        tmp.append(tmp2.monster_effect_name)
    result = '<select id="invalid_monster_kind-'+num+'" name="invalid_monster_kind-'+num+'" onchange="changeInvalidMonsterKindNum()">'
    i=1
    for tmp_val in tmp:
        result += '<option value="' + str(i)+ '">'+tmp_val+'</option>'
        i+=1
    result+= '</select>'
    return HttpResponse(result)
def get_monster_kind(req):

    monster_kind = MonsterEffectKind.objects.all()
    if not monster_kind:
        return HttpResponse('')
    num = req.POST["num"]
    tmp = []
    for tmp2 in monster_kind:
        tmp.append(tmp2.monster_effect_name)
    result = '<select id="monster_kind-'+num+'" name="monster_kind-'+num+'" onchange="changeMonsterKindNum()">'
    i=1
    for tmp_val in tmp:
        result += '<option value="' + str(i)+ '">'+tmp_val+'</option>'
        i+=1
    result+= '</select>'
    return HttpResponse(result)
def get_monster_effect_kind(req):

    monster_kind = MonsterEffectKind.objects.all()
    if not monster_kind:
        return HttpResponse('')
    num = req.POST["num"]
    tmp = []
    for tmp2 in monster_kind:
        tmp.append(tmp2.monster_effect_name)
    result = '<select id="monster_kind-'+num+'" name="monster_effect_kind-'+num+'" onchange="changeMonsterEffectKindNum()">'
    i=1
    for tmp_val in tmp:
        result += '<option value="' + str(i)+ '">'+tmp_val+'</option>'
        i+=1
    result+= '</select>'
    return HttpResponse(result)

def get_field_kind2(req):
    field_kind = FieldKind.objects.all()
    if not field_kind:
        return HttpResponse('')
    num = req.POST["num"]
    tmp = []
    for tmp2 in field_kind:
        tmp.append(tmp2.field_kind_name)
    result = '<select id="field_kind-'+num+'" name="field_kind-'+num+'" onchange="changeCondtionFieldKind()">'
    i=1
    result += '<option value="' + str(0)+ '">全て</option>'
    for tmp_val in tmp:
        result += '<option value="' + str(i)+ '">'+tmp_val+'</option>'
        i+=1
    result+= '</select>'
    return HttpResponse(result)
def pac_diagram(request,pac_id):
    pac = Pac.objects.get(id=pac_id)
    effect = pac.pac_next
    effect_ary = []
    effect_id_ary = []
    pac_ary = []
    pac_id_ary = []
    effect_name = effect.monster_effect_name
    effect_name= effect_name.replace(" ","")
    effect_name = effect_name.replace("1","1")
    effect_name = effect_name.replace("２","2")
    effect_name = effect_name.replace("３","3")
    effect_name = effect_name.replace("４","4")
    effect_name = effect_name.replace("５","5")
    effect_name = effect_name.replace("６","6")
    effect_name = effect_name.replace("７","7")
    effect_name = effect_name.replace("８","8")
    effect_name = effect_name.replace("９","9")
    effect_name = effect_name.replace("０","0")
    effect_name = effect_name.replace("１","0")
    effect_ary.append(effect_name)
    effect_id_ary.append(effect.id)
    result_html2 = "graph TD\n";
    result_html = "";
    if effect is not None:
        result_html += pac_diagram_det(effect,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    result_html = result_html.replace("１","1",100)
    result_html = result_html.replace("２","2",100)
    result_html = result_html.replace("３","3",100)
    result_html = result_html.replace("４","4",100)
    result_html = result_html.replace("５","5",100)
    result_html = result_html.replace("６","6",100)
    result_html = result_html.replace("７","7",100)
    result_html = result_html.replace("８","8",100)
    result_html = result_html.replace("９","9",100)
    result_html = result_html.replace("０","0",100)
    result_html = result_html.replace(" ","",100)
    result_html = result_html2 + result_html

    context = {}
    context["effect_ary"] = effect_ary
    context["effect_id_ary"] = effect_id_ary
    context["pac_ary"] = pac_ary
    context["pac_id_ary"] = pac_id_ary
    context["result_html"] = result_html
    count = range(len(effect_id_ary))
    count_pac = range(len(pac_id_ary))
    context["count"] = count
    context["count_pac"] = count_pac

    return render(request,'admin/tcgcreator/pac_diagram.html',context=context)
def trigger_diagram(request,trigger_id):
    trigger = Trigger.objects.get(id=trigger_id)
    effect = trigger.next_effect
    result_html2 = "graph TD\n";
    result_html = "";
    effect_ary = []
    effect_id_ary = []
    pac_ary = []
    pac_id_ary = []
    if effect is not None:
        effect_ary.append(effect.monster_effect_name)
        effect_id_ary.append(effect.id)
        result_html += pac_diagram_det(effect,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    else:
        pac = trigger.pac
        pac_ary.append(pac.pac_name)
        pac_id_ary.append(pac.id)
        result_html += pac_diagram_det2(pac,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    result_html = result_html.replace("１","1")
    result_html = result_html.replace("２","2")
    result_html = result_html.replace("３","3")
    result_html = result_html.replace("４","4")
    result_html = result_html.replace("５","5")
    result_html = result_html.replace("６","6")
    result_html = result_html.replace("７","7")
    result_html = result_html.replace("８","8")
    result_html = result_html.replace("９","9")
    result_html = result_html.replace("０","0")
    result_html = result_html2 + result_html
    context = {}
    context["result_html"] = result_html
    context["effect_ary"] = effect_ary
    context["effect_id_ary"] = effect_id_ary
    context["pac_ary"] = pac_ary
    context["pac_id_ary"] = pac_id_ary
    count = range(len(effect_id_ary))
    count_pac = range(len(pac_id_ary))
    context["count"] = count
    context["count_pac"] = count_pac


    return render(request,'admin/tcgcreator/trigger_diagram.html',context=context)
def pac_diagram_det2(pac,effect_ary,effect_id_ary,pac_ary,pac_id_ary):
    pac_name = pac.pac_name
    pac_name = pac_name.replace(" ","")
    pac_name = pac_name.replace("1","1")
    pac_name = pac_name.replace("２","2")
    pac_name = pac_name.replace("３","3")
    pac_name = pac_name.replace("４","4")
    pac_name = pac_name.replace("５","5")
    pac_name = pac_name.replace("６","6")
    pac_name = pac_name.replace("７","7")
    pac_name = pac_name.replace("８","8")
    pac_name = pac_name.replace("９","9")
    pac_name = pac_name.replace("０","0")
    pac_name = pac_name.replace("１","1")
    result_html = ""

    if pac.pac_next is not None:
        pac_next = pac.pac_next
        pac_name1 = pac.pac_next.pac_name
        pac_name1 = pac_name1.replace(" ","")
        pac_name1 = pac_name1.replace("1","1")
        pac_name1 = pac_name1.replace("２","2")
        pac_name1 = pac_name1.replace("３","3")
        pac_name1 = pac_name1.replace("４","4")
        pac_name1 = pac_name1.replace("５","5")
        pac_name1 = pac_name1.replace("６","6")
        pac_name1 = pac_name1.replace("７","7")
        pac_name1 = pac_name1.replace("８","8")
        pac_name1 = pac_name1.replace("９","9")
        pac_name1 = pac_name1.replace("０","0")
        pac_name1 = pac_name1.replace("１","1")
        result_html += pac_name+"-->"+pac_name1 +"\n"
        if not pac_next.id in pac_id_ary:
            pac_ary.append(pac_name1)
            pac_id_ary.append(pac_next.id)
            result_html+=pac_diagram_det2(pac_next,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    else:
        next_effect1 = pac.monster_effect_next
        if next_effect1 is not None:
            next_effect_name1 = next_effect1.monster_effect_name
            next_effect_name1= next_effect_name1.replace(" ","")
            next_effect_name1 = next_effect_name1.replace("1","1")
            next_effect_name1 = next_effect_name1.replace("２","2")
            next_effect_name1 = next_effect_name1.replace("３","3")
            next_effect_name1 = next_effect_name1.replace("４","4")
            next_effect_name1 = next_effect_name1.replace("５","5")
            next_effect_name1 = next_effect_name1.replace("６","6")
            next_effect_name1 = next_effect_name1.replace("７","7")
            next_effect_name1 = next_effect_name1.replace("８","8")
            next_effect_name1 = next_effect_name1.replace("９","9")
            next_effect_name1 = next_effect_name1.replace("０","0")
            next_effect_name1 = next_effect_name1.replace("１","0")
            result_html += pac_name+"-->"+next_effect_name1 + "\n"
            if not next_effect1.id in effect_id_ary:
                effect_ary.append(next_effect_name1)
                effect_id_ary.append(next_effect1.id)
                result_html += pac_diagram_det(next_effect1,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    if pac.pac_next2 is not None:
        pac_next2 = pac.pac_next2
        pac_name2 = pac_next2.pac_name
        pac_name2 = pac_name2.replace("1","1")
        pac_name2 = pac_name2.replace("２","2")
        pac_name2 = pac_name2.replace("３","3")
        pac_name2 = pac_name2.replace("４","4")
        pac_name2 = pac_name2.replace("５","5")
        pac_name2 = pac_name2.replace("６","6")
        pac_name2 = pac_name2.replace("７","7")
        pac_name2 = pac_name2.replace("８","8")
        pac_name2 = pac_name2.replace("９","9")
        pac_name2 = pac_name2.replace("０","0")
        pac_name2 = pac_name2.replace("１","0")
        result_html += pac_name+"-->"+pac_name1 +"\n"
        if not pac_next2.id in pac_id_ary:
            pac_ary.append(pac_name1)
            pac_id_ary.append(pac_next.id)
            result_html+=pac_diagram_det2(pac_next2,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    else:
        next_effect2 = pac.monster_effect_next2
        if next_effect2 is not None:
            next_effect_name2 = next_effect2.monster_effect_name
            next_effect_name2= next_effect_name2.replace(" ","")
            next_effect_name2 = next_effect_name2.replace("1","1")
            next_effect_name2 = next_effect_name2.replace("２","2")
            next_effect_name2 = next_effect_name2.replace("３","3")
            next_effect_name2 = next_effect_name2.replace("４","4")
            next_effect_name2 = next_effect_name2.replace("５","5")
            next_effect_name2 = next_effect_name2.replace("６","6")
            next_effect_name2 = next_effect_name2.replace("７","7")
            next_effect_name2 = next_effect_name2.replace("８","8")
            next_effect_name2 = next_effect_name2.replace("９","9")
            next_effect_name2 = next_effect_name2.replace("０","0")
            next_effect_name2 = next_effect_name2.replace("１","0")
            result_html += pac_name+"-->"+next_effect_name2 + "\n"
            if not next_effect2.id in effect_id_ary:
                effect_ary.append(next_effect_name2)
                effect_id_ary.append(next_effect2.id)
                result_html += pac_diagram_det(next_effect2,effect_ary,effect_id_ary,pac_ary,pac_id_ary)

    return result_html

def pac_diagram_det(effect,effect_ary,effect_id_ary,pac_ary,pac_id_ary):
    effect_name = effect.monster_effect_name
    effect_name = effect_name.replace(" ","")
    effect_name = effect_name.replace("1","1")
    effect_name = effect_name.replace("２","2")
    effect_name = effect_name.replace("３","3")
    effect_name = effect_name.replace("４","4")
    effect_name = effect_name.replace("５","5")
    effect_name = effect_name.replace("６","6")
    effect_name = effect_name.replace("７","7")
    effect_name = effect_name.replace("８","8")
    effect_name = effect_name.replace("９","9")
    effect_name = effect_name.replace("０","0")
    effect_name = effect_name.replace("１","0")
    result_html = ""
  
    if effect.pac is not None:
        pac_next = effect.pac
        pac_name1 = pac_next.pac_name
        pac_name1 = pac_name1.replace(" ","")
        pac_name1 = pac_name1.replace("1","1")
        pac_name1 = pac_name1.replace("２","2")
        pac_name1 = pac_name1.replace("３","3")
        pac_name1 = pac_name1.replace("４","4")
        pac_name1 = pac_name1.replace("５","5")
        pac_name1 = pac_name1.replace("６","6")
        pac_name1 = pac_name1.replace("７","7")
        pac_name1 = pac_name1.replace("８","8")
        pac_name1 = pac_name1.replace("９","9")
        pac_name1 = pac_name1.replace("０","0")
        pac_name1 = pac_name1.replace("１","0")
        result_html += effect_name+"-->"+pac_name1 +"\n"
        if pac_next.id  not in pac_id_ary:
            pac_ary.append(pac_name1)
            pac_id_ary.append(pac_next.id)
            result_html+=pac_diagram_det2(effect.pac,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    else:
        next_effect1 = effect.monster_effect_next
        if next_effect1 is not None:
            next_effect_name1 = next_effect1.monster_effect_name
            next_effect_name1= next_effect_name1.replace(" ","")
            next_effect_name1 = next_effect_name1.replace("1","1")
            next_effect_name1 = next_effect_name1.replace("２","2")
            next_effect_name1 = next_effect_name1.replace("３","3")
            next_effect_name1 = next_effect_name1.replace("４","4")
            next_effect_name1 = next_effect_name1.replace("５","5")
            next_effect_name1 = next_effect_name1.replace("６","6")
            next_effect_name1 = next_effect_name1.replace("７","7")
            next_effect_name1 = next_effect_name1.replace("８","8")
            next_effect_name1 = next_effect_name1.replace("９","9")
            next_effect_name1 = next_effect_name1.replace("０","0")
            next_effect_name1 = next_effect_name1.replace("１","0")
            result_html += effect_name+"-->"+next_effect_name1 + "\n"
            if not next_effect1.id in effect_id_ary:
                effect_ary.append(next_effect_name1)
                effect_id_ary.append(next_effect1.id)
                result_html += pac_diagram_det(next_effect1,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    if effect.pac2 is not None:
        pac_next2 = effect.pac2
        pac_name2 = pac_next2.pac_name
        pac_name2 = pac_name2.replace("1","1")
        pac_name2 = pac_name2.replace("２","2")
        pac_name2 = pac_name2.replace("３","3")
        pac_name2 = pac_name2.replace("４","4")
        pac_name2 = pac_name2.replace("５","5")
        pac_name2 = pac_name2.replace("６","6")
        pac_name2 = pac_name2.replace("７","7")
        pac_name2 = pac_name2.replace("８","8")
        pac_name2 = pac_name2.replace("９","9")
        pac_name2 = pac_name2.replace("０","0")
        pac_name2 = pac_name2.replace("１","0")
        result_html += effect_name+"-->"+pac_name2 +"\n"
        if pac_next2.id  not in pac_id_ary:
            pac_ary.append(pac_name2)
            pac_id_ary.append(pac_next2.id)
            result_html+=pac_diagram_det2(effect.pac2,effect_ary,effect_id_ary,pac_ary,pac_id_ary)
    else:
        next_effect2 = effect.monster_effect_next2
        if next_effect2 is not None:
            next_effect_name2 = next_effect2.monster_effect_name
            next_effect_name2= next_effect_name2.replace(" ","")
            next_effect_name2 = next_effect_name2.replace("1","1")
            next_effect_name2 = next_effect_name2.replace("２","2")
            next_effect_name2 = next_effect_name2.replace("３","3")
            next_effect_name2 = next_effect_name2.replace("４","4")
            next_effect_name2 = next_effect_name2.replace("５","5")
            next_effect_name2 = next_effect_name2.replace("６","6")
            next_effect_name2 = next_effect_name2.replace("７","7")
            next_effect_name2 = next_effect_name2.replace("８","8")
            next_effect_name2 = next_effect_name2.replace("９","9")
            next_effect_name2 = next_effect_name2.replace("０","0")
            next_effect_name2 = next_effect_name2.replace("１","0")
            result_html += effect_name+"-->"+next_effect_name2 + "\n"
            if not next_effect2.id in effect_id_ary:
                effect_ary.append(next_effect_name2)
                effect_id_ary.append(next_effect2.id)
                result_html += pac_diagram_det(next_effect2,effect_ary,effect_id_ary,pac_ary,pac_id_ary)

    return result_html


def field_list_view(request):
    field_size = get_object_or_404(FieldSize)
    field_x = field_size.field_x;
    field_y = field_size.field_y;
    context = {};
    context["field_x"] = range(field_x);
    context["field_y"] = range(field_y);
    context["tmp_structure"] = {};
    for x in range(field_x):
        context["tmp_structure"][x] = {}
        for y in range(field_y):
            tmp_structure = {}
            field = Field.objects.filter(x=x,y=y)
            mine_or_other = field[0].mine_or_other
            kind = field[0].kind.split("_")
            kinds = ""
            i=0
            for tmp in kind:
                if(tmp == ""):
                    continue
                tmp2 = FieldKind.objects.filter(id=int(tmp))
                kinds += tmp2[0].field_kind_name+"<br>";
            if(kinds != ""):
                tmp_structure["kinds"] = kinds
            else:
                tmp_structure["kinds"] = "編集"

            tmp_structure["mine_or_other"] = mine_or_other;
            tmp_structure["id"] = field[0].id
            context["tmp_structure"][x][y]=tmp_structure

    return render(request,'admin/tcgcreator/field_list.html',context=context)
def get_variable_kind(req):
    variables = GlobalVariable.objects.order_by('-priority')
    result = "<option value=\"0\">なし</option>"
    for variable in variables:
        if variable.mine_or_other== 0:
            result += "<option value=\"variable_"+str(variable.variable_name)+"_1\">自分"+variable.variable_name+"</option>"
            result += "<option value=\"variable_"+str(variable.variable_name)+"_2\">相手"+variable.variable_name+"</option>"
        else:
            result += "<option value=\"variable_"+str(variable.variable_name)+"_0\">共通"+variable.variable_name+"</option>"

    return HttpResponse(result)
def get_place_kind_to(req):
    decks = Deck.objects.all()
    hands = Hand.objects.all()
    graves = Grave.objects.all()
    fields = FieldKind.objects.all()
    result = ""
    i=1;
    result = "<option value=\"\">なし</option>"
    for deck in decks:
        if deck.mine_or_other== 0:
            result += "<option value=\"deck_"+str(i)+"_1\">自分"+deck.deck_name+"</option>"
            result += "<option value=\"deck_"+str(i)+"_2\">相手"+deck.deck_name+"</option>"
            result += "<option value=\"deck_"+str(i)+"_4\">元々の持ち主"+deck.deck_name+"</option>"
        else:
            result += "<option value=\"deck_"+str(i)+"_0\">共通"+deck.deck_name+"</option>"
        i+=1
    i=1;
    for hand in hands:
        if hand.mine_or_other== 0:
            result += "<option value=\"hand_"+str(i)+"_1\">自分"+hand.hand_name+"</option>"
            result += "<option value=\"hand_"+str(i)+"_2\">相手"+hand.hand_name+"</option>"
            result += "<option value=\"hand_"+str(i)+"_4\">元々の持ち主"+hand.hand_name+"</option>"
        else:
            result += "<option value=\"hand_"+str(i)+"_0\">共通"+hand.hand_name+"</option>"
        i+=1
    i=1
    for grave in graves:
        if grave.mine_or_other== 0:
            result += "<option value=\"grave_"+str(i)+"_1\">自分"+grave.grave_name+"</option>"
            result += "<option value=\"grave_"+str(i)+"_2\">相手"+grave.grave_name+"</option>"
            result += "<option value=\"grave_"+str(i)+"_4\">元々の持ち主"+grave.grave_name+"</option>"
        else:
            result += "<option value=\"grave_"+str(i)+"_0\">共通"+grave.grave_name+"</option>"
        i+=1
    i=1
    for field in fields:
        if field.mine_or_other == 0:
            result += "<option value=\"field_"+str(i)+"_1\">自分"+field.field_kind_name+"</option>"
            result += "<option value=\"field_"+str(i)+"_2\">相手"+field.field_kind_name+"</option>"
            result += "<option value=\"field_"+str(i)+"_4\">元々の持ち主"+field.field_kind_name+"</option>"
        else:
            result += "<option value=\"field_"+str(i)+"_3\">共通"+field.field_kind_name+"</option>"
        i+=1
    return HttpResponse(result)
def get_place_kind(req):
    decks = Deck.objects.all()
    hands = Hand.objects.all()
    graves = Grave.objects.all()
    fields = FieldKind.objects.all()
    result = ""
    i=1;
    result = "<option value=\"\">なし</option>"
    for deck in decks:
        if deck.mine_or_other== 0:
            result += "<option value=\"deck_"+str(i)+"_1\">自分"+deck.deck_name+"</option>"
            result += "<option value=\"deck_"+str(i)+"_2\">相手"+deck.deck_name+"</option>"
        else:
            result += "<option value=\"deck_"+str(i)+"_0\">共通"+deck.deck_name+"</option>"
        i+=1
    i=1;
    for hand in hands:
        if hand.mine_or_other== 0:
            result += "<option value=\"hand_"+str(i)+"_1\">自分"+hand.hand_name+"</option>"
            result += "<option value=\"hand_"+str(i)+"_2\">相手"+hand.hand_name+"</option>"
        else:
            result += "<option value=\"hand_"+str(i)+"_0\">共通"+hand.hand_name+"</option>"
        i+=1
    i=1
    for grave in graves:
        if grave.mine_or_other== 0:
            result += "<option value=\"grave_"+str(i)+"_1\">自分"+grave.grave_name+"</option>"
            result += "<option value=\"grave_"+str(i)+"_2\">相手"+grave.grave_name+"</option>"
        else:
            result += "<option value=\"grave_"+str(i)+"_0\">共通"+grave.grave_name+"</option>"
        i+=1
    i=1
    for field in fields:
        if field.mine_or_other == 0:
            result += "<option value=\"field_"+str(i)+"_1\">自分"+field.field_kind_name+"</option>"
            result += "<option value=\"field_"+str(i)+"_2\">相手"+field.field_kind_name+"</option>"
        else:
            result += "<option value=\"field_"+str(i)+"_3\">共通"+field.field_kind_name+"</option>"
        i+=1
    return HttpResponse(result)
def get_monster_trigger_condition(req):

    result = ""
    monster_variables = MonsterVariables.objects.all()

    result+="フラグ <input type=\"text\" id=\"flag\">"
    result+='<select id="flag_equal"><option value="">全て</option><option value="=">=</option></select><br>'
    result+="モンスター名 <input type=\"text\" id=\"monster_name_0\" onfocus=\"showMonsterNameEqual('"+str(i)+"_0')\" >"
    result+='モンスター位置<input type=\"text\" id=\"monster_place_id_0_1_0\">'
    result+='モンスターユニーク<input type=\"text\" id=\"monster_unique_id_0_1_0\">'
    result+='<select id="get_monster_name_equal_0"><option value="">全て</option><option value="=">=</option><option value="like">含む</option></select>'
    result+='<select id="monster_name_and_or_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_name_add_0" type="button" value="追加"  onclick="addMonsterName(\''+str(i)+'_0\')"><br>'
    for monster_variable in monster_variables:
        if (monster_variable.monster_variable_kind_id.id == 0 or monster_variable.monster_variable_kind_id.id == 1):
            result+=monster_variable.monster_variable_name+"<input type=\"text\" onfocus=\"showMonsterEquation('get_monster_variable_"+str(monster_variable.id)+"_0')\" id=\"get_monster_variable_"+str(monster_variable.id)+"_0\">"
            result+='<input type="hidden" id="get_monster_variable_name_'+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+='<select id="get_monster_variable_equal_'+str(monster_variable.id)+'_0"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select>'
            result+='<select id="monster_variable_and_or_'+str(monster_variable.id)+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'
            result+='<select id="monster_variable_init_'+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

        else:
            result+='<input type="hidden" id="get_monster_variable_name_'+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+=monster_variable.monster_variable_name+"<select id=\"get_monster_variable"+"_"+str(monster_variable.id)+"_0\">"
            result+="<option value=\"0\">全て</option>"
            result+='<select id="monster_variable_init_'+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

            kinds = monster_variable.monster_variable_kind_id.monster_variable_sentence
            kinds_org = kinds
            kinds = kinds.split("|")
            k=1
            for kind in kinds:
                result+="<option value=\""+str(k)+"\">"+kind+"</option>"
                k+=1
            result+="</select>"
            result+='<select id="monster_variable_and_or_'+str(monster_variable.id)+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_variable_add'+"_"+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation2(\''+str(i)+'_'+str(monster_variable.id)+'_0\',\''+kinds_org+'\')"><br>'
    return HttpResponse(result)
def get_monster_move(req):

    if "i" in req.POST:
        i= req.POST["i"]
        add_i = "_"+i
    else:
        add_i = ""

    result = ""
    monster_variables = MonsterVariables.objects.all()

    result+="フラグ <input type=\"text\" id=\"flag"+add_i+"\">"
    result+='<select id="flag_equal'+add_i+'"><option value="">全て</option><option value="=">=</option></select><br>'
    result+="モンスター名 <input type=\"text\" id=\"monster_name"+add_i+"_0\" onfocus=\"showMonsterNameEqual('"+str(i)+"_0')\" >"
    result+='モンスター位置<input type=\"text\" id=\"monster_place_id_0\">'
    result+='モンスターユニーク<input type=\"text\" id=\"monster_unique_id_0\">'
    result+='<select id="get_monster_name_equal'+add_i+'_0"><option value="">全て</option><option value="=">=</option><option value="like">含む</option></select>'
    result+='<select id="monster_name_and_or'+add_i+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_name_add'+add_i+'_0" type="button" value="追加"  onclick="addMonsterName(\''+str(i)+'_0\')"><br>'
    for monster_variable in monster_variables:
        if (monster_variable.monster_variable_kind_id.id == 0 or monster_variable.monster_variable_kind_id.id == 1):
            result+='<input type="hidden" id="get_monster_variable_name'+add_i+"_"+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+=monster_variable.monster_variable_name+"<input type=\"text\" onfocus=\"showMonsterEquation('get_monster_variable"+add_i+"_"+str(monster_variable.id)+"_0')\" id=\"get_monster_variable"+add_i+"_"+str(monster_variable.id)+"_0\">"
            result+='<select id="get_monster_variable_equal'+add_i+'_'+str(monster_variable.id)+'_0"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select>'
            result+='<select id="monster_variable_and_or'+add_i+"_"+str(monster_variable.id)+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_variable_add'+add_i+"_"+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'
            result+='<select id="monster_variable_init'+add_i+"_"+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

        else:
            result+='<input type="hidden" id="get_monster_variable_name'+add_i+"_"+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+=monster_variable.monster_variable_name+"<select id=\"get_monster_variable"+add_i+"_"+str(monster_variable.id)+"_0\">"
            result+="<option value=\"0\">全て</option>"
            result+='<select id="monster_variable_init'+add_i+"_"+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

            kinds = monster_variable.monster_variable_kind_id.monster_variable_sentence
            kinds_org = kinds
            kinds = kinds.split("|")
            k=1
            for kind in kinds:
                result+="<option value=\""+str(k)+"\">"+kind+"</option>"
                k+=1
            result+="</select>"
            result+='<select id="monster_variable_and_or'+add_i+"_"+str(monster_variable.id)+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_variable_add'+add_i+"_"+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation2(\''+str(i)+'_'+str(monster_variable.id)+'_0\',\''+kinds_org+'\')"><br>'
    return HttpResponse(result)
def get_monster_condition(req):

    if "i" in req.POST:
        i= req.POST["i"]
        add_i = "_"+i
    else:
        add_i = ""
    if "j" in req.POST:
        j= req.POST["j"]
        add_j = "_"+j
    else:
        add_j = ""

    result = ""
    monster_variables = MonsterVariables.objects.all()

    result+="フラグ <input type=\"text\" id=\"flag"+add_j+add_i+"\">"
    result+='<select id="flag_equal'+add_j+add_i+'"><option value="">全て</option><option value="=">=</option></select><br>'
    result+="モンスター名 <input type=\"text\" id=\"monster_name"+add_j+add_i+"_0\" onfocus=\"showMonsterNameEqual('"+str(j)+"_"+str(i)+"_0')\" >"
    result+='モンスター位置<input type=\"text\" id=\"monster_place_id'+add_j+add_i+'\">'
    result+='モンスターユニーク<input type=\"text\" id=\"monster_unique_id'+add_j+add_i+'\">'
    result+='<select id="get_monster_name_equal'+add_j+add_i+'_0"><option value="">全て</option><option value="=">=</option><option value="like">含む</option></select>'
    result+='<select id="monster_name_and_or'+add_j+add_i+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_name_add'+add_j+add_i+'_0" type="button" value="追加"  onclick="addMonsterName(\''+str(j)+"_"+str(i)+'_0\')"><br>'
    for monster_variable in monster_variables:
        if (monster_variable.monster_variable_kind_id.id == 0 or monster_variable.monster_variable_kind_id.id == 1):
            result+='<input type="hidden" id="get_monster_variable_name'+add_j+add_i+"_"+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+=monster_variable.monster_variable_name+"<input type=\"text\" onfocus=\"showMonsterEquation('get_monster_variable"+add_j+add_i+"_"+str(monster_variable.id)+"_0')\" id=\"get_monster_variable"+add_j+add_i+"_"+str(monster_variable.id)+"_0\">"
            result+='<select id="get_monster_variable_equal'+add_j+add_i+'_'+str(monster_variable.id)+'_0"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select>'
            result+='<select id="monster_variable_and_or'+add_j+add_i+"_"+str(monster_variable.id)+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select>'
            result+='<select id="monster_variable_init'+add_j+add_i+"_"+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select>'
            result+='<input id="monster_variable_add_'+str(j)+"_"+str(i)+"_"+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(j)+'_'+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

        else:
            result+='<input type="hidden" id="get_monster_variable_name'+add_j+add_i+"_"+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+=monster_variable.monster_variable_name+"<select id=\"get_monster_variable"+add_j+add_i+"_"+str(monster_variable.id)+"_0\">"
            result+="<option value=\"0\">全て</option>"

            kinds = monster_variable.monster_variable_kind_id.monster_variable_sentence
            kinds_org = kinds
            kinds = kinds.split("|")
            k=1
            for kind in kinds:
                result+="<option value=\""+str(k)+"\">"+kind+"</option>"
                k+=1
            result+="</select>"
            result+='<select id="monster_variable_and_or'+add_j+add_i+"_"+str(monster_variable.id)+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select>'
            result+='<select id="monster_variable_init'+add_j+add_i+"_"+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select>'
            result+='<input id="monster_variable_add_'+str(j)+"_"+str(i)+"_"+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(j)+'_'+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'
    result+='<input type="button" value="カスタム追加" id="custom_add_'+str(j)+"_"+str(i)+'_0_0" class="custom_add" onclick="addCustomMonsterCondition(\''+str(j)+"_"+str(i)+'_0_0\')">'
    return HttpResponse(result)
def get_monster_to(req):

    result = ""
    monster_variables = MonsterVariables.objects.all()

    result+="モンスター名 <input type=\"text\" id=\"monster_name_to\">"
    result+='<select id="get_monster_name_equal_to"><option value="">全て</option><option value="=">=</option><option value="like">含む</option></select><br>'
    for monster_variable in monster_variables:
        if (monster_variable.monster_variable_kind_id.id == 0 or monster_variable.monster_variable_kind_id.id == 1):
            result+='<input type="hidden" id="get_monster_variable_name_'+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+=monster_variable.monster_variable_name+"<input type=\"number\" id=\"get_monster_variable_"+str(monster_variable.id)+"_to\">"
            result+='<select id="get_monster_variable_equal_'+str(monster_variable.id)+'_to"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>'
            result+='<select id="monster_variable_init_'+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

        else:
            result+='<input type="hidden" id="get_monster_variable_name_'+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+=monster_variable.monster_variable_name+"<select id=\"get_monster_variable_"+str(monster_variable.id)+"_to\">"
            result+="<option value=\"0\">全て</option>"
            result+='<select id="monster_variable_init_'+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

            kinds = monster_variable.monster_variable_kind_id.monster_variable_sentence
            kinds = kinds.split("|")
            i=1
            for kind in kinds:
                result+="<option value=\""+str(i)+"\">"+kind+"</option>"
                i+=1
            result+="</select><br>"
    return HttpResponse(result)
def get_timing(req):
    phases = Phase.objects.all()
    result=""
    for phase in phases:
        result+='<option value="'+str(phase.id)+'">'+phase.phase_name+'</option>'
    return HttpResponse(result)
'''
def get_monster_variable_change_condition(req):
    
    result = ""
    monster_variables = MonsterVariables.objects.all()
    
    for monster_variable in monster_variables:
        if (monster_variable.monster_variable_kind_id.id == 0 or monster_variable.monster_variable_kind_id.id == 1):
            result+=monster_variable.monster_variable_name+"<input type=\"number\" id=\"get_monster_variable_change_variable_"+str(monster_variable.id)+"\">"
            result+='<select id="get_monster_variable_variable_equal_'+str(monster_variable.id)+'"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>'

        else:
            result+=monster_variable.monster_variable_name+"<select id=\"get_monster_variable_variable_"+str(monster_variable.id)+"\">"
            result+="<option value=\"0\">全て</option>"

            kinds = monster_variable.monster_variable_kind_id.monster_variable_sentence
            kinds = kinds.split("|")
            i=1
            for kind in kinds:
                result+="<option value=\""+str(i)+"\">"+kind+"</option>"
                i+=1
            result+="</select><br>"
    return HttpResponse(result)
'''
def get_trigger(req):

    result = ""
    monster_variables = MonsterVariables.objects.all()

    for monster_variable in monster_variables:
        if (monster_variable.monster_variable_kind_id.id == 0 or monster_variable.monster_variable_kind_id.id == 1):
            result+=monster_variable.monster_variable_name+"<input type=\"number\" id=\"get_trigger_variable_"+str(monster_variable.id)+"\">"
            result+='<input type="hidden" id="get_trigger_variable_name_'+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+='<select id="get_trigger_variable_equal_'+str(monster_variable.id)+'"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>'
            result+='<select id="trigger_variable_init_'+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

        else:
            result+=monster_variable.monster_variable_name+"<select id=\"get_trigger_variable_"+str(monster_variable.id)+"\">"
            result+='<input type="hidden" id="get_trigger_variable_name_'+str(monster_variable.id)+'" value="'+monster_variable.monster_variable_name+'">'
            result+="<option value=\"0\">全て</option>"
            result+='<select id="trigger_variable_init_'+str(monster_variable.id)+'_0" > <option value="0">現在の値</option><option value="1">元々の値</option> <option value="2">元々の元々の値</option> </select><input id="monster_variable_add_'+str(monster_variable.id)+'_0" type="button" value="追加"  onclick="addMonsterEquation(\''+str(i)+'_'+str(monster_variable.id)+'_0\')"><br>'

            kinds = monster_variable.monster_variable_kind_id.monster_variable_sentence
            kinds = kinds.split("|")
            i=1
            for kind in kinds:
                result+="<option value=\""+str(i)+"\">"+kind+"</option>"
                i+=1
            result+="</select><br>"
    return HttpResponse(result)
def get_equation_0():
    monster_variables = MonsterVariables.objects.all()
    result = ""
    result+='種類<select id="get_equation_kind"><option value="number">数</option><option value="kind">種類</option><option value="x">x</option><option value="y">y</option>'
    for monster_variable in monster_variables:
        result+= "<option value=num_"+str(monster_variable.monster_variable_name)+">"+monster_variable.monster_variable_name+" 数</option>"
        result+= "<option value=kind_"+str(monster_variable.monster_variable_name)+">"+monster_variable.monster_variable_name+" 種類</option>"
    result+="</select><br>"
    return HttpResponse(result)
def get_equation_to(req):
    result = ""
    result+='種類<select id="get_equation_kind_to"><option value="number">数</option><option value="kind">種類</option></select><br>'
    result+='min<input type="text" id="min_equation_number_to" onfocus="showMinEquationTo()">';
    result+='max<input type="text" id="max_equation_number_to" onfocus="showMaxEquationTo()">';
    return HttpResponse(result)
def get_equation(req):
    if "c" in req.POST:
        c = req.POST["c"];
    monster_variables = MonsterVariables.objects.all()
    result_tmp=""
    for monster_variable in monster_variables:
        result_tmp += '<option value="'+str(monster_variable.monster_variable_name)+'">'+monster_variable.monster_variable_name+'</option>'
    result = ""
    result+='除外<input type="text" id="exclude_'+c+'" >'
    result+='演算子<select id="get_equation_det_'+c+'"><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>'
    result+='種類<select id="get_equation_kind_'+c+'"><option value="number">数</option><option value="kind">種類</option><option value="x">x</option><option value="y">y</option>'+result_tmp+'</select><br>'
    result+='数<input type="number" id="get_equation_number_'+c+'">';
    result+='min<input type="text" id="min_equation_number_'+c+'" onfocus="showMinEquation('+c+')">';
    result+='max<input type="text" id="max_equation_number_'+c+'" onfocus="showMaxEquation('+c+')">';
    return HttpResponse(result)
def get_field_x_and_y(req):
    if "c" in req.POST:
        c = req.POST["c"]
    if "id" in req.POST:
        field_id = req.POST["id"]

    result = 'フィールドx位置<input id="'+field_id+'_field_x_'+c+'_0" style="">'
    result+='演算子<select id="get_field_x_det_'+c+'_0"><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>'
    result+='<select id="get_field_x_and_or_'+c+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select>';
    result+='<input type="button" value="追加" id="add_field_x_'+c+'_0" onclick="addFieldX('+c+',1,\''+field_id+'\')"><br>'

    result+= 'フィールドy位置<input id="'+field_id+'_field_y_'+c+'_0" style="">'
    result+='演算子<select id="get_field_y_det_'+c+'_0"><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>'
    result+='<select id="get_field_y_and_or_'+c+'_0" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select>';
    result+='<input type="button" value="追加" id="add_field_y_'+c+'_0" onclick="addFieldY('+c+',1,\''+field_id+'\')"><br>'
    return HttpResponse(result)
def init_battle1(request):
    return init_battle(request,1)
def init_battle2(request):
    return init_battle(request,2)
def init_battle3(request):
    return init_battle(request,3)
def init_battle(request,room_number):
    if not request.user.is_authenticated():
        return HttpResponse("Please Login")
    duel = Duel.objects.filter(id=room_number).first();
    if duel.waiting == True and duel.user_2 != None:
        duel.winner = 0
        duel.user_1 = None
        duel.user_2 = None
    if(duel.user_1 == request.user):
        if room_number == 1:
            if(duel.user_2 ):
                return HttpResponseRedirect(reverse('battle1'))
            else:
                return HttpResponseRedirect(reverse('wait_battle1'))
        if room_number == 2:
            if(duel.user_2 ):
                return HttpResponseRedirect(reverse('battle2'))
            else:
                return HttpResponseRedirect(reverse('wait_battle2'))
        if room_number == 3:
            if(duel.user_2 ):
                return HttpResponseRedirect(reverse('battle3'))
            else:
                return HttpResponseRedirect(reverse('wait_battle3'))
    if(duel.user_2 == request.user):
        if room_number == 1:
            return HttpResponseRedirect(reverse('battle1'))
        if room_number == 2:
            return HttpResponseRedirect(reverse('battle2'))
        if room_number == 3:
            return HttpResponseRedirect(reverse('battle3'))
    if(not duel.user_1 ):
        if check_in_other_room(request.user,room_number):
            return HttpResponse("他の部屋に入室しています")
        tmp = check_user_deck(request.user)
        if(tmp):
            return HttpResponse(tmp)
        duel.user_1 = request.user
        duel.save()
        if room_number == 1:
            return HttpResponseRedirect(reverse('wait_battle1'))
        if room_number == 2:
            return HttpResponseRedirect(reverse('wait_battle2'))
        if room_number == 3:
            return HttpResponseRedirect(reverse('wait_battle3'))

    if(not duel.user_2 ):
        if check_in_other_room(request.user,room_number):
            return HttpResponse("他の部屋に入室しています")
        tmp = check_user_deck(request.user)
        if(tmp):
            return HttpResponse(tmp)
        tmp=init_duel(room_number,request.user);
        if(tmp):
            return HttpResponse(tmp)
        return HttpResponseRedirect(reverse('battle'+str(room_number)))
    else:
        return HttpResponseRedirect(reverse('watch_battle'))

def send_lose(request):
    room_number = request.POST["room_number"]
    duel = Duel.objects.filter(id=room_number).first()
    if duel.user_1 == request.user:
        duel.log += request.user.first_name+"は降参した"
        duel.log_turn += request.user.first_name+"は降参した"
        duel.winner = 2
        duel.save()
    if duel.user_2 == request.user:
        duel.log += request.user.first_name+"は降参した"
        duel.log_turn += request.user.first_name+"は降参した"
        duel.winner = 1
        duel.save()
    return HttpResponse("")


def leave_battle1(request):
    return leave_battle(request,1)
def leave_battle2(request):
    return leave_battle(request,2)
def leave_battle3(request):
    return leave_battle(request,3)
def wait_battle1(request):
    return wait_battle(request,1)
def wait_battle2(request):
    return wait_battle(request,2)
def wait_battle3(request):
    return wait_battle(request,3)
def wait_battle(request,room_number):
    return render(request,'tcgcreator/wait_battle.html',{'room_number':room_number})
def leave_battle(request,room_number):
    duel = Duel.objects.filter(id=room_number).first()
    if duel.waiting == True and duel.user_1 == request.user:
        duel.user_1 = None
        duel.save()
        return HttpResponseRedirect(reverse('choose'))
    else:
        return HttpResponse("エラーが発生しました。")
def battle(request):
    duel = Duel.objects.all();
    if request.user is None :
        return HttpResponse("Please Login")

    if(duel.user_1 == request.user):
        return HttpResponse("Success")

    if(duel.user_2 == request.user):
        return HttpResponse("Success")
    return HttpResponseRedirect(reverse('accounts:login'))

def default_deck(req):
    monster_variables = MonsterVariables.objects.all().filter(~Q(monster_variable_show = 0))
    decks = Deck.objects.all()
    deck_group = 1
    where_sql = "";
    join_sql = "";
    add_variable =[]
    deck_group = DefaultDeckChoice.objects.first()
    if not deck_group:
        create_default_deck_group(1,"デッキ")
        default_deck_group  = DefaultDeckGroup.objects.all().first();
        create_default_deck_choice(default_deck_group)
        deck_group  = DefaultDeckChoice.objects.all().filter().first()
    else:
        default_deck_group=deck_group.default_deck;
    #新規デッキ追加
    if "deck_name" in req.GET:
        default_deck_group_max = DefaultDeckGroup.objects.all().aggregate(Max('default_deck_id'))
        deck_group = default_deck_group_max["default_deck_id__max"]+1
        create_default_deck_group(deck_group,req.GET["deck_name"])
        default_deck_group  = DefaultDeckGroup.objects.all().filter(default_deck_id = deck_group).first()
    elif "deck_group" in req.GET:
        if "deck_group" in req.GET and req.GET["deck_group"] != "":
            deck_group_id = req.GET["deck_group"]
            default_deck_group  = DefaultDeckGroup.objects.all().filter(default_deck_id = int(deck_group_id)).first()
            deck_group.default_deck = default_deck_group
            deck_group.save()
    else:
    #デッキグループを選択
        if "deck_group" in req.POST and req.POST["deck_group"] != "":
            deck_group_id = req.POST["deck_group"]
            default_deck_group  = DefaultDeckGroup.objects.all().filter(default_deck_id = int(deck_group_id)).first()
            deck_group.default_deck = default_deck_group
            deck_group.save()
        elif "deck_name" in req.POST and req.POST["deck_name"] != "":
            default_deck_group = deck_group.default_deck
            deck_name = req.POST["deck_name"]
            default_deck_group.deck_name = deck_name
            default_deck_group.save()
        else:
            default_deck_group = deck_group.default_deck

    default_deck_groups = DefaultDeckGroup.objects.filter()

    for deck in decks:
        default_decks = DefaultDeck.objects.all().filter(deck_type__id = deck.id,deck_group = default_deck_group)
        if not default_decks :
            create_default_deck(deck,default_deck_group)

    if req.method == 'POST':
        check = copy_to_default_deck(req.POST,default_deck_group);
        if(check != ""):
            return HttpResponse(check)
        i = 0
        for monster_variable in monster_variables:
            if(req.POST["monster_variable"+str(monster_variable.id)] != ""):
                if(monster_variable.monster_variable_kind_id.id < 2):
                    join_sql += " left join tcgcreator_monsteritem as i"+str(i)+" on m.id = i"+str(i)+".monster_id_id"
                    if(req.POST[str(monster_variable.id)+"_how"] == "least"):
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text >= " + req.POST["monster_variable"+str(monster_variable.id)] + " and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                    elif(req.POST[str(monster_variable.id)+"_how"] == "same"):
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text = " + req.POST["monster_variable"+str(monster_variable.id)] + " and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                        #monster = monster.filter(monster_item__monster_item_text = int(req.POST["monster_variable"+str(monster_variable.id)]))
                    elif(req.POST[str(monster_variable.id)+"_how"] == "utmost"):
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text <= " + req.POST["monster_variable"+str(monster_variable.id)] + " and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                        #monster = monster.filter(monster_item__monster_item_text <= int(req.POST["monster_variable"+str(monster_variable.id)]))
                else:
                    if(req.POST["monster_variable"+str(monster_variable.id)] != "0"):
                        join_sql += " left join tcgcreator_monsteritem as i"+str(i)+" on m.id = i"+str(i)+".monster_id_id"
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text like %s and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                        add_variable.append("%"+req.POST["monster_variable"+str(monster_variable.id)]+"%");
                        #monster = monster.filter(monster_item__monster_item_text__contains = (req.POST["monster_variable"+str(monster_variable.id)]),monster_item__monster_variables_id = int(monster_variable.id))
            i+=1;
    if where_sql == "":
        where_sql = "1"
    monster = Monster.objects.raw("select * from tcgcreator_monster as m "+ join_sql + " where "+ where_sql,add_variable)
    default_deck = DefaultDeck.objects.all().filter(deck_group = default_deck_group)
    #sql = "select * from tcgcreator_monster as m "+ join_sql + " where "+ where_sql
    return render(req,'admin/tcgcreator/makedeck.html',{'MonsterVariables':monster_variables,'Monster':monster,'DefaultDeck':default_deck,'Deck':decks,'DefaultDeckGroup':default_deck_group,"DefaultDeckGroups":default_deck_groups})

def makedeck(req):
    monster_variables = MonsterVariables.objects.all().select_related('monster_variable_kind_id')
    decks = Deck.objects.all()
    deck_group = 1
    where_sql = "";
    join_sql = "";
    add_variable =[]
    if not req.user.is_authenticated():
        return HttpResponse("Please Login")
    deck_group = UserDeckChoice.objects.filter(user = req.user).first()
    if not deck_group:
        create_user_deck_group(1,req.user,"デッキ")
        user_deck_group  = UserDeckGroup.objects.all().filter(user_deck_id = 1,user=req.user).first();
        create_user_deck_choice(user_deck_group,req.user)
        deck_group  = UserDeckChoice.objects.all().filter(user=req.user).first()
        for deck in decks:
            create_user_deck(req.user,deck,user_deck_group,1)
    else:
        user_deck_group=deck_group.user_deck;
    #新規デッキ追加
    if "deck_name" in req.GET:
        user_deck_group_max = UserDeckGroup.objects.all().aggregate(Max('user_deck_id'))
        deck_group2 = user_deck_group_max["user_deck_id__max"]+1
        create_user_deck_group(deck_group2,req.user,req.GET["deck_name"])
        user_deck_group  = UserDeckGroup.objects.all().filter(user_deck_id = deck_group2,user=req.user).first()
        deck_group.user_deck = user_deck_group
        deck_group.save()
        for deck in decks:
            create_user_deck(req.user,deck,user_deck_group,req.GET["structure_deck"])
    elif "deck_group" in req.GET:
        if "deck_group" in req.GET and req.GET["deck_group"] != "":
            deck_group_id = req.GET["deck_group"]
            user_deck_group  = UserDeckGroup.objects.all().filter(user_deck_id = int(deck_group_id),user=req.user).first()
            deck_group.user_deck = user_deck_group
            deck_group.save()
    else:
    #デッキグループを選択
        if "deck_group" in req.POST and req.POST["deck_group"] != "":
            deck_group_id = req.POST["deck_group"]
            user_deck_group  = UserDeckGroup.objects.all().filter(user_deck_id = int(deck_group_id),user=req.user).first()
            deck_group.user_deck = user_deck_group
            deck_group.save()
        elif "deck_name" in req.POST and req.POST["deck_name"] != "":
            user_deck_group = deck_group.user_deck
            deck_name = req.POST["deck_name"]
            user_deck_group.deck_name = deck_name
            user_deck_group.save()
        else:
            user_deck_group = deck_group.user_deck

    user_deck_groups = UserDeckGroup.objects.filter(user_id=req.user)

    default_deck_groups = DefaultDeckGroup.objects.all()
    for deck in decks:
        user_decks = UserDeck.objects.all().filter(user = req.user,deck_type__id = deck.id,deck_group = user_deck_group)

    if req.method == 'POST':
        check = copy_to_deck(req.user,req.POST,user_deck_group);
        if(check != ""):
            return HttpResponse(check)

        i = 0
        for monster_variable in monster_variables:
            if("monster_variable"+str(monster_variable.id) in req.POST and req.POST["monster_variable"+str(monster_variable.id)] != ""):
                if(monster_variable.monster_variable_kind_id.id < 2):
                    join_sql += " left join tcgcreator_monsteritem as i"+str(i)+" on m.id = i"+str(i)+".monster_id_id"
                    if(req.POST[str(monster_variable.id)+"_how"] == "least"):
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text >= " + req.POST["monster_variable"+str(monster_variable.id)] + " and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                    elif(req.POST[str(monster_variable.id)+"_how"] == "same"):
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text = " + req.POST["monster_variable"+str(monster_variable.id)] + " and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                        #monster = monster.filter(monster_item__monster_item_text = int(req.POST["monster_variable"+str(monster_variable.id)]))
                    elif(req.POST[str(monster_variable.id)+"_how"] == "utmost"):
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text <= " + req.POST["monster_variable"+str(monster_variable.id)] + " and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                        #monster = monster.filter(monster_item__monster_item_text <= int(req.POST["monster_variable"+str(monster_variable.id)]))
                else:
                    if(req.POST["monster_variable"+str(monster_variable.id)] != "0"):
                        join_sql += " left join tcgcreator_monsteritem as i"+str(i)+" on m.id = i"+str(i)+".monster_id_id"
                        if where_sql != "":
                            where_sql +=  " and "
                        where_sql += "(i"+str(i)+".monster_item_text like %s and i"+str(i)+".monster_variables_id_id = "+ str(monster_variable.id)+")";
                        add_variable.append("%"+req.POST["monster_variable"+str(monster_variable.id)]+"%");
                        #monster = monster.filter(monster_item__monster_item_text__contains = (req.POST["monster_variable"+str(monster_variable.id)]),monster_item__monster_variables_id = int(monster_variable.id))
            i+=1;
    if where_sql == "":
        where_sql = "1"
    if "sort" not in req.POST or req.POST["sort"] == "0":
        sort = Config.objects.first().default_sort
        sort = sort.id
    else:
        sort = int(req.POST["sort"])
    if "desc" in req.POST and req.POST["desc"] == "1":
        desc = "desc"
    else:
        desc = ""
    if where_sql != "":
        where_sql +=  " and "
    where_sql += " for_order.monster_variables_id_id = "+ str(sort) +" ";
    join_sql += " left join tcgcreator_monsteritem as for_order on m.id = for_order.monster_id_id"
    order_by = " order by for_order.monster_item_text " + desc

    monster = Monster.objects.raw("select distinct m.id,m.*, for_order.monster_item_text from tcgcreator_monster as m "+ join_sql + " where "+ where_sql + order_by,add_variable)
    user_deck = UserDeck.objects.all().filter(user=req.user,deck_group = user_deck_group)
    #sql = "select * from tcgcreator_monster as m "+ join_sql + " where "+ where_sql
    return render(req,'tcgcreator/makedeck.html',{'MonsterVariables':monster_variables,'Monster':monster,'UserDeck':user_deck,'Deck':decks,'UserDeckGroup':user_deck_group,"UserDeckGroups":user_deck_groups,"DefaultDeckGroups":default_deck_groups,"sort":sort,"desc":desc})

def get_monster_deck_type(req):
    num = req.POST["num"]
    decks = Deck.objects.all();
    result = '<select id="monster_deck_text_'+num+'" name="monster_item_text_'+num+'" onchange="changeDeckNum()">'
    for deck in decks:
        result += '<option value="' + str(deck.id)+ '">'+deck.deck_name+'</option>'
    result+= "</select>"
    return HttpResponse(result)


def get_phase(req):
    phases = Phase.objects.all()
    return_html = ""
    for phase in phases:
        return_html += '<option value="'+str(phase.id)+'">'+phase.phase_name+'</option>'
    return HttpResponse(return_html)

def get_trigger(req):
    triggers = Trigger.objects.filter(trigger_none_monster = True)
    return_html = ""
    for trigger in triggers:
        return_html += '<option value="'+str(trigger.id)+'">'+trigger.trigger_name+'</option>'
    return HttpResponse(return_html)
def choose(request):
    reenter1 = 0
    reenter2 = 0
    reenter3 = 0
    duel_1 = Duel.objects.filter(id=1).get()
    if duel_1.user_2 is None:
        duel_1.winner = 0
        watch_1 = 0
    else:
        watch_1 = 1
    duel_2 = Duel.objects.filter(id=2).get()
    if duel_2.user_2 is None:
        duel_2.winner = 0
        watch_2 = 0
    else:
        watch_2 = 1
    duel_3 = Duel.objects.filter(id=3).get()
    if duel_3.user_2 is None:
        duel_3.winner = 0
        watch_3 = 0
    else:
        watch_3 = 1
    config = Config.objects.get()
    limit_time = config.limit_time
    room_text1 = ""
    room_text2 = ""
    room_text3 = ""
    if duel_1.winner != 0:
        room_text1 += duel_1.user_1.first_name +  "対" + duel_1.user_2.first_name+"\n"
        if duel_1.winner == 1:
            room_text1 += duel_1.user_1.first_name+ "の勝利\n"
        elif duel_1.winner == 2:
            room_text1 += duel_1.user_2.first_name+ "の勝利\n"
    if duel_2.winner != 0:
        room_text2 += duel_2.user_1.first_name +  "対" + duel_2.user_2.first_name+"\n"
    if duel_2.winner == 1:
        room_text2 += duel_2.user_1.first_name+ "の勝利\n"
    elif duel_2.winner == 2:
        room_text2 += duel_2.user_2.first_name+ "の勝利\n"
    if duel_3.winner != 0:
        room_text3 += duel_3.user_1.first_name +  "対" + duel_3.user_2.first_name+"\n"
    if duel_3.winner == 1:
        room_text3 += duel_3.user_1.first_name+ "の勝利\n"
    elif duel_3.winner == 2:
        room_text3 += duel_3.user_2.first_name+ "の勝利\n"
    if duel_1.waiting == True:
        wait_kind1 = 0
    elif duel_1.winner != 0 and time() - duel_1.end_time > limit_time:
        duel_1.waiting = True
        duel_1.save()
        wait_kind1  = 0
    elif duel_1.winner != 0:
        wait_kind1 = 1
    elif duel_1.winner == 0 and time() - duel_1.time_1 > limit_time * 2:
        duel_1.waiting = True
        duel_1.save()
        wait_kind1  = 0
    elif duel_1.winner == 0:
        room_text1 += "対戦中"+duel_1.user_1.first_name+"対"+duel_1.user_2.first_name
        if request.user == duel_1.user_1 or request.user == duel_1.user_2:
            reenter1 = 1

        wait_kind1 = 1
    if duel_2.waiting == True:
        wait_kind2 = 0
    elif duel_2.winner != 0 and time() - duel_2.end_time > limit_time:
        duel_2.waiting = True
        duel_2.save()
        wait_kind2 =  0
    elif duel_2.winner != 0:
        wait_kind2 = 1
    elif duel_2.winner == 0 and time() - duel_2.time_1 > limit_time * 2:
        duel_2.waiting = True
        duel_2.save()
        wait_kind2  = 0
    elif duel_2.winner == 0:
        room_text2 += "対戦中"+duel_2.user_1.first_name+"対"+duel_2.user_2.first_name
        if request.user == duel_2.user_1 or request.user == duel_2.user_2:
            reenter2 = 1
        wait_kind2 = 1
    if duel_3.waiting == True:
        wait_kind3 = 0
    elif duel_3.winner != 0 and time() - duel_3.end_time > limit_time:
        duel_3.waiting = True
        duel_3.save()
        wait_kind3 = 1
    elif duel_3.winner != 0:
        wait_kind3 = 0
    elif duel_3.winner == 0 and time() - duel_3.time_1 > limit_time * 2:
        duel_3.waiting = True
        duel_3.save()
        wait_kind3  = 1
    elif duel_3.winner == 0:
        room_text3 += "対戦中"+duel_3.user_1.first_name+"対"+duel_3.user_2.first_name
        if request.user == duel_3.user_1 or request.user == duel_3.user_2:
            reenter3 =1
        wait_kind3 = 0
    if duel_1.winner == 0 and duel_1.waiting == True and duel_1.user_1:
        room_text1 += "対戦募集中"+duel_1.user_1.first_name
    if duel_2.winner == 0 and duel_2.waiting == True and duel_2.user_1:
        room_text2 += "対戦募集中"+duel_2.user_1.first_name
    if duel_3.winner == 0 and duel_3.waiting == True and duel_3.user_1:
        room_text3 += "対戦募集中"+duel_3.user_1.first_name
    return render(request,'tcgcreator/choose.html',{'room_text1':room_text1,'room_text2':room_text2,'room_text3':room_text3,'wait_kind1':wait_kind1,'wait_kind2':wait_kind2,'wait_kind3':wait_kind3,'watch_1':watch_1,'watch_2':watch_2,'watch_3':watch_3,"reenter1":reenter1,"reenter2":reenter2,"reenter3":reenter3})

def get_tcg_timing(req):
    timings = Timing.objects.all()
    return_html = ""
    for timing in timings:
        return_html += '<option value="'+str(timing.id)+'">'+timing.timing_name+'</option>'
    return HttpResponse(return_html)
def index(request):
    return render(request, 'tcgcreator/index.html')
def howto(request):
    return render(request, 'tcgcreator/howto.html')
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'tcgcreator/signup.html', {'form': form})
