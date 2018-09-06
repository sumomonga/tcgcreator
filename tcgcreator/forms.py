from django.forms import ModelForm
from django import forms
from django.forms import ModelChoiceField
from django.contrib.auth.models import  User,AbstractBaseUser,BaseUserManager, PermissionsMixin
from .models import MonsterVariables,MonsterVariablesKind,Monster,MonsterItem,Field
from django.contrib.auth.forms import UserCreationForm
class FieldForm(forms.ModelForm):
	class Meta:
		model = Field
		exclude = ['x','y']
class CustomChoiceField(ModelChoiceField):
	def label_from_instance(self,obj):
		return '%s' % obj.monster_variable_name
class EditMonsterVariablesForm(ModelForm):
	monster_variable_kind_id = CustomChoiceField(queryset = MonsterVariablesKind.objects.all())
	class Meta:
		model = MonsterVariables
		fields = ['id','monster_variable_kind_id','monster_variable_name','monster_variable_label','monster_variable_show','priority','default_value' ]
		

class EditMonsterVariablesKindForm(ModelForm):
	class Meta:
		model = MonsterVariablesKind
		fields = ['monster_variable_name','monster_variable_sentence' ]
class EditMonsterForm(ModelForm):
	class Meta:
		model = Monster
		fields = ['monster_name','monster_sentence' ]
class EditMonsterItemForm(ModelForm):
	class Meta:
		model = MonsterItem
		fields = ['monster_item_text','monster_variables_id','monster_id' ]

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','password1','password2','first_name' ]
