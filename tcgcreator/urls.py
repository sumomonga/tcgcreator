from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import battle_det
from . import explain_grave
from . import explain
from . import explain_deck
from . import battle
from . import watch
from . import ask
from . import answer
from . import hand_trigger
from . import deck_trigger
from . import field_trigger
from . import choices
from . import get_monster_variable
urlpatterns = [
#	url(r'^$', views.index, name='index'),
	url(r'^monster_variables/$',views.monster_variables,name='monster_variables'),
	url(r'^edit_monster_variables/(?P<monster_variables_id>\d+)/$',views.edit_monster_variables,name='edit_monster_variables'),
	url(r'^monster_variables_kind/$',views.monster_variables_kind,name='monster_variables_kind'),
	url(r'^edit_monster_variables_kind/(?P<monster_variables_kind_id>\d+)/$',views.edit_monster_variables_kind,name='edit_monster_variables_kind'),
	url(r'^new_monster_variables_kind/$',views.new_monster_variables_kind,name='new_monster_variables_kind'),
	url(r'^new_monster_variables/$',views.new_monster_variables,name='new_monster_variables'),
	url(r'^new_monster/$',views.new_monster,name='new_monster'),
	url(r'^monster/$',views.monster,name='monster'),
    url(r'^choose/$',views.choose,name='choose'),
	url(r'^get_monster_kind_type/$',views.get_monster_kind_type,name='get_monster_kind_type'),
	url(r'^get_monster_kind_type_for_new_monster/$',views.get_monster_kind_type_for_new_monster,name='get_monster_kind_type_for_new_monster'),
	url(r'^get_field_kind/$',views.get_field_kind,name='get_field_kind'),
	url(r'^get_field_kind2/$',views.get_field_kind2,name='get_field_kind2'),
	url(r'^get_monster_kind/$',views.get_monster_kind,name='get_monster_kind'),
    url(r'^get_invalid_monster_kind/$',views.get_invalid_monster_kind,name='get_invalid_monster_kind'),
	url(r'^get_monster_condition/$',views.get_monster_condition,name='get_monster_condition'),
	url(r'^get_monster_move/$',views.get_monster_move,name='get_monster_move'),
	url(r'^get_equation/$',views.get_equation,name='get_equation'),
	url(r'^get_monster_to/$',views.get_monster_to,name='get_monster_to'),
	url(r'^get_equation_to/$',views.get_equation_to,name='get_equation_to'),
	url(r'^get_trigger/$',views.get_trigger,name='get_trigger'),
	url(r'^get_place_kind/$',views.get_place_kind,name='get_place_kind'),
    url(r'^get_place_kind_to/$',views.get_place_kind_to,name='get_place_kind_to'),
	url(r'^get_variable_kind/$',views.get_variable_kind,name='get_variable_kind'),
	url(r'^battle1/$',battle.battle1,name='battle1'),
    url(r'^battle2/$',battle.battle2,name='battle2'),
    url(r'^battle3/$',battle.battle3,name='battle3'),
	url(r'^watch1/$',watch.watch1,name='watch1'),
    url(r'^watch2/$',watch.watch2,name='watch2'),
    url(r'^watch3/$',watch.watch3,name='watch3'),
    url(r'^leave_battle1/$',views.leave_battle1,name='leave_battle1'),
    url(r'^leave_battle2/$',views.leave_battle2,name='leave_battle2'),
    url(r'^leave_battle3/$',views.leave_battle3,name='leave_battle3'),
	url(r'^wait_battle1/$',views.wait_battle1,name='wait_battle1'),
    url(r'^wait_battle2/$',views.wait_battle2,name='wait_battle2'),
    url(r'^wait_battle3/$',views.wait_battle3,name='wait_battle3'),
	url(r'^init_battle1/$',views.init_battle1,name='init_battle1'),
    url(r'^init_battle2/$',views.init_battle2,name='init_battle2'),
    url(r'^init_battle3/$',views.init_battle3,name='init_battle3'),
    url(r'^send_lose/$',views.send_lose,name='send_lose'),
	url(r'^get_timing/$',views.get_timing,name='get_timing'),
	url(r'^get_field_x_and_y/$',views.get_field_x_and_y,name='get_field_x_and_y'),
	url(r'^makedeck/$',views.makedeck,name='makedeck'),
	url(r'^get_monster_deck_type/$',views.get_monster_deck_type,name='get_monster_deck_type'),
	url(r'^battle_det/$',battle_det.battle_det,name='battle_det'),
    url(r'^send_message/$',battle_det.send_message,name='send_message'),
	url(r'^watch_det/$',watch.watch_det,name='watch_det'),
	url(r'^explain_deck/$',explain_deck.explain_deck,name='explain_deck'),
	url(r'^explain/$',explain.explain,name='explain'),
	url(r'^explain_grave/$',explain_grave.explain_grave,name='explain_grave'),
	url(r'^ask_place/$',ask.ask_place,name='ask_place'),
	url(r'^answer/$',answer.answer,name='answer'),
	url(r'^none/$',answer.none,name='none'),
    url(r'^cancel/$',answer.cancel,name='cancel'),
	url(r'^hand_trigger/$',hand_trigger.hand_trigger,name='hand_trigger'),
	url(r'^deck_trigger/$',deck_trigger.deck_trigger,name='deck_trigger'),
	url(r'^field_trigger/$',field_trigger.field_trigger,name='field_trigger'),
	url(r'^choices/$',choices.choices,name='choices'),
	url(r'^get_phase/$',views.get_phase,name='get_phase'),
	url(r'^get_trigger/$',views.get_trigger,name='get_trigger'),
	url(r'^get_tcg_timing/$',views.get_tcg_timing,name='get_tcg_timing'),
	url(r'^get_monster_variable/$',get_monster_variable.get_monster_variable,name='get_monster_variable'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^user_info_change/$', views.user_info_change, name='user_info_change'),
    url(r'^index/$', views.index, name='index'),
    url(r'^howto/$', views.howto, name='howto'),


]+static(settings.MEDIA_URL,document_root  = settings.MEDIA_ROOT)
