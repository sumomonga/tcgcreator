from django.contrib import admin
from .forms import FieldForm
from .models import MonsterVariablesKind, MonsterVariables,Monster,MonsterItem,FieldSize,Field,FieldKind,MonsterEffectKind,MonsterEffect,Deck,Hand,Grave,Trigger,Phase,Duel,UserDeckGroup,Config,GlobalVariable,MonsterEffectWrapper,Cost,CostWrapper,DefaultDeck,TriggerTiming,Timing,Pac,PacWrapper,EternalEffect,PacCost,PacCostWrapper,DuelHand,VirtualVariable,EternalWrapper,DuelDeck,DuelGrave,Flag,EternalTrigger
from .custom_functions  import init_monster_item,init_field
# Register your models here.
#class MyModelAdmin(admin.ModelAdmin):
admin.site.register(Flag)
class DeckAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	def has_add_permission(self, request):
		if Deck.objects.count() >= 10:
			return False
		else:
			return True
admin.site.register(Deck,DeckAdmin)
class HandAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	def has_add_permission(self, request):
		if Hand.objects.count() >= 10:
			return False
		else:
			return True
admin.site.register(Hand,HandAdmin)
class GraveAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	def has_add_permission(self, request):
		if Grave.objects.count() >= 10:
			return False
		else:
			return True
admin.site.register(Grave,GraveAdmin)
class FieldSizeAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		if FieldSize.objects.count() != 0:
			return False
		else:
			return True
	def has_delete_permission(self,request, obj=None):
		return False
	def save_model(self,request,obj,form,change):
		obj.save()
		init_field(request.POST["field_x"],request.POST["field_y"]);
admin.site.register(FieldSize,FieldSizeAdmin)
class CostAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	change_form_template =  "admin/tcgcreator/monster_effect.html"
	class Media:
		js = ['js/jquery-2.2.0.min.js','js/cost_kind.js','js/field_kind2.js','js/monster_condition.js','js/monster_effect_move.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/monster_variable_change.js','js/ajax.js','js/cost.js','js/monster_effect_kind.js','js/monster_effect_choose.js','js/monster_effect_choose_both.js']

admin.site.register(Cost,CostAdmin)
class MonsterEffectAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return True
	change_form_template =  "admin/tcgcreator/monster_effect.html"
	class Media:
		js = ['js/monster_effect_choose_both.js','js/monster_effect_choose.js','js/monster_effect_move.js','js/monster_variable_change.js','js/jquery-2.2.0.min.js','js/monster_effect_kind.js','js/field_kind2.js','js/monster_effect.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/monster_condition.js']
	
admin.site.register(MonsterEffect,MonsterEffectAdmin)
class TriggerTimingAdmin(admin.ModelAdmin):
    def has_delete_permission(self,request, obj=None):
        return False
    change_form_template =  "admin/tcgcreator/trigger.html"
    class Media:
        css = {
            'all':('css/common.css',)
        }
        js = ['js/jquery-2.2.0.min.js','js/monster_condition.js','js/field_kind2.js','js/trigger_timing.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/trigger_variable.js']

admin.site.register(TriggerTiming,TriggerTimingAdmin)
class TriggerAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	change_form_template =  "admin/tcgcreator/trigger.html"
	class Media:
		css = {
			'all':('css/common.css',)
		}
		js = ['js/jquery-2.2.0.min.js','js/monster_condition.js','js/field_kind2.js','js/trigger.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/trigger_variable.js']
	
admin.site.register(Trigger,TriggerAdmin)
class EternalEffectAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	change_form_template =  "admin/tcgcreator/eternal_effect.html"
	class Media:
		js = ['js/jquery-2.2.0.min.js','js/field_kind2.js','js/eternal_effect.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/eternal_effect_variable.js','js/monster_condition.js']
	
admin.site.register(EternalEffect,EternalEffectAdmin)
class FieldAdmin(admin.ModelAdmin):
	form = FieldForm

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self,request, obj=None):
		return False

	class Media:
		js = ['js/jquery-2.2.0.min.js','js/field_kind.js','js/ajax.js']

admin.site.register(Field,FieldAdmin)
class MonsterVariablesAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	def save_model(self,request,obj,form,change):
		obj.save();
		if change == False:
			init_monster_item(obj)
admin.site.register(MonsterVariablesKind,admin.ModelAdmin)
admin.site.register(FieldKind,admin.ModelAdmin)
admin.site.register(MonsterVariables,MonsterVariablesAdmin)
class MonsterItemInline(admin.StackedInline):
	def has_delete_permission(self,request, obj=None):
		return False
	model = MonsterItem
	def get_extra (self, request, obj=None, **kwargs):
		if obj: 
			return 0
		return MonsterVariables.objects.count()
		
admin.site.register(MonsterEffectKind)
class MonsterAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return True
	change_form_template =  "admin/tcgcreator/monster_form.html"

	def changeform_view(self, request,object_id,form_url, extra_context=None):
		extra_context = {}
		extra_context["monster_item_number"] = MonsterVariables.objects.count()
		return super(MonsterAdmin, self).changeform_view(request, object_id, form_url, extra_context=extra_context)
	inlines = [MonsterItemInline]
	class Media:
		js = ['js/jquery-2.2.0.min.js','js/monster_deck.js','js/monster_item.js','js/ajax.js']
	
class PhaseAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	class Media:
		js = ['js/jquery-2.2.0.min.js','js/phase.js','js/ajax.js']
class VirtualVariableAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	change_form_template =  "admin/tcgcreator/virtual_variable.html"
	class Media:
		js = ['js/jquery-2.2.0.min.js','js/common.js','js/ajax.js','js/virtual_variable.js','js/jquery-ui-1.12.1/jquery-ui.min.js']
admin.site.register(Monster,MonsterAdmin)
class DuelAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	class Meta:
		fields = [];
admin.site.register(Duel)
admin.site.register(Phase,PhaseAdmin)
admin.site.register(UserDeckGroup)
admin.site.register(Config)
admin.site.register(GlobalVariable)
admin.site.register(VirtualVariable,VirtualVariableAdmin)
class EternalTriggerAdmin(admin.ModelAdmin):
    def has_delete_permission(self,request, obj=None):
        return True
    change_form_template =  "admin/tcgcreator/monster_effect.html"
    class Media:
        js = ['js/monster_effect_choose_both.js','js/monster_effect_choose.js','js/monster_effect_move.js','js/monster_variable_change.js','js/jquery-2.2.0.min.js','js/monster_effect_kind.js','js/field_kind2.js','js/monster_effect.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/monster_condition.js']
admin.site.register(EternalTrigger,EternalTriggerAdmin)
class EternalWrapperAdmin(admin.ModelAdmin):
    def has_delete_permission(self,request, obj=None):
        return True
    change_form_template =  "admin/tcgcreator/monster_effect.html"
    class Media:
        js = ['js/monster_effect_choose_both.js','js/monster_effect_choose.js','js/monster_effect_move.js','js/monster_variable_change.js','js/jquery-2.2.0.min.js','js/monster_effect_kind.js','js/field_kind2.js','js/monster_effect.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/monster_condition.js']
admin.site.register(EternalWrapper,EternalWrapperAdmin)
class MonsterEffectWrapperAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return True
	change_form_template =  "admin/tcgcreator/monster_effect.html"
	class Media:
		js = ['js/monster_effect_choose_both.js','js/monster_effect_choose.js','js/monster_effect_move.js','js/monster_variable_change.js','js/jquery-2.2.0.min.js','js/monster_effect_kind.js','js/field_kind2.js','js/monster_effect.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/monster_condition.js']
	
admin.site.register(MonsterEffectWrapper,MonsterEffectWrapperAdmin)
class CostWrapperAdmin(admin.ModelAdmin):
    def has_delete_permission(self,request, obj=None):
        return False
    change_form_template =  "admin/tcgcreator/monster_effect.html"
    class Media:
        js = ['js/jquery-2.2.0.min.js','js/cost_kind.js','js/field_kind2.js','js/monster_condition.js','js/monster_effect_move.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/monster_variable_change.js','js/ajax.js','js/cost.js','js/monster_effect_kind.js','js/monster_effect_choose.js','js/monster_effect_choose_both.js']
admin.site.register(CostWrapper,CostWrapperAdmin)
admin.site.register(Pac)
admin.site.register(PacCost)
admin.site.register(PacCostWrapper)
class PacWrapperAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return True
	change_form_template =  "admin/tcgcreator/monster_effect.html"
	class Media:
		js = ['js/monster_effect_choose_both.js','js/monster_effect_choose.js','js/monster_effect_move.js','js/monster_variable_change.js','js/jquery-2.2.0.min.js','js/monster_effect_kind.js','js/field_kind2.js','js/monster_effect.js','js/common.js','js/jquery-ui-1.12.1/jquery-ui.min.js','js/ajax.js','js/monster_condition.js']
admin.site.register(PacWrapper,PacWrapperAdmin)
class DefaultDeckAdmin(admin.ModelAdmin):
	def has_delete_permission(self,request, obj=None):
		return False
	class Media:
		js = ['js/jquery-2.2.0.min.js','js/phase.js','js/ajax.js']
admin.site.register(DefaultDeck,DefaultDeckAdmin)
admin.site.register(Timing)
admin.site.register(DuelHand)
admin.site.register(DuelDeck)
admin.site.register(DuelGrave)
