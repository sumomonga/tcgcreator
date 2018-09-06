from django.db import models
from django.conf import settings
from django.contrib.auth.models import  User,AbstractBaseUser,BaseUserManager, PermissionsMixin

TRIGGER_WHO =(
    (0,"元々の持ち主"),
    (1,"行使者" ),
    (2,"非行使者" ),
    (3,"移動元"),
    (4,"移動先")
)

MINE_OR_OTHER3 = (
    (0, '全て'),
    (1, "自分"),
    (2, "相手"),
    (3, "共通"),
)
MINE_OR_OTHER = (
    (0, "共通"),
    (1, '自分'),
    (2, '相手'),
)
PLACE_KIND = (
    (0, "全て"),
    (1, "デッキ"),
    (2, '墓地'),
    (3, '手札'),
    (4, 'フィールド'),
)
COST_OR_EFFECT = (
    (0,"両方"),
    (1,"コスト"),
    (2,"効果"),
)
CHAIN = (
    (0,"以上"),
    (1,"以下"),
    (2,"ちょうど"),
)
class Timing(models.Model):
    next_timing = models.ForeignKey("Timing",default=None,blank=True,null=True)
    timing_name= models.CharField(max_length=32,blank=True)
    timing_auto = models.BooleanField(default=False)
    def __str__(self):
        return self.timing_name
class TriggerTiming(models.Model):
    def __str__(self):
        return self.trigger_timing_name
    trigger = models.ForeignKey('Trigger',default=None,null=True,blank=True);
    kinds = models.CharField(max_length=32,blank=True)
    from_place_kind = models.IntegerField(choices = PLACE_KIND,default = 0);
    from_deck = models.ForeignKey("Deck",default =None,null=True,related_name='from_deck',blank=True)
    from_grave = models.ForeignKey("Grave",default = None,null=True,related_name='from_grave',blank=True)
    from_hand = models.ForeignKey("Hand",default=None,null=True,related_name='from_hand',blank=True)
    from_field = models.ForeignKey("FieldKind",default=None,null=True,related_name='from_field_kind',blank=True)
    from_mine_or_other = models.IntegerField(choices = MINE_OR_OTHER3)
    to_place_kind = models.IntegerField(choices = PLACE_KIND,default = 0);
    to_deck = models.ForeignKey("Deck",default =None,null=True,related_name ="to_deck",blank=True)
    to_grave = models.ForeignKey("Grave",default = None,null=True,related_name ="to_grave",blank=True)
    to_hand = models.ForeignKey("Hand",default=None,null=True,related_name ="to_hand",blank=True)
    to_field = models.ForeignKey("FieldKind",default=None,null=True,related_name='to_field_kind',blank=True)
    to_mine_or_other = models.IntegerField(choices = MINE_OR_OTHER3)
    monster = models.ManyToManyField("Monster")
    who =  models.IntegerField(choices=TRIGGER_WHO,default=0)
    chain_user = models.IntegerField(choices=MINE_OR_OTHER3,default=0)
    cost_or_effect = models.IntegerField(choices = COST_OR_EFFECT,blank=True)
    trigger_timing_name = models.CharField(max_length=32,blank=True)
class Trigger(models.Model):
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER,default=1)
    priority = models.IntegerField(default="100")
    turn = models.IntegerField(choices=MINE_OR_OTHER)
    phase = models.ForeignKey('Phase',default=None,blank=True,null=True)
    chain = models.IntegerField(default=0,blank=True)
    chain_kind = models.IntegerField(default=0,blank=True,choices = CHAIN)
    force = models.BooleanField(default=False)
    pac = models.ForeignKey('PacWrapper',default=None,blank=True,null=True)
    next_effect = models.ForeignKey('MonsterEffectWrapper',default=None,blank=True,null=True)
    trigger_condition = models.TextField(default="",blank=True)
    trigger_timing = models.BooleanField(default=False,blank=True)
    trigger_monster = models.TextField(default=None,null=True,blank=True)
    trigger_none_monster = models.BooleanField(default=False)
    trigger_name = models.CharField(max_length=32,default=None,null=True,blank=True)
    trigger_sentence = models.CharField(max_length=32,default=None,null=True,blank=True)
    trigger_cost = models.ForeignKey('CostWrapper',default=None,null=True,blank=True)
    trigger_cost_pac = models.ForeignKey('PacCostWrapper',default=None,blank=True,null=True)
    trigger_kind = models.CharField(max_length=32,default="",blank=True)
    timing = models.ManyToManyField(Timing,default=None,blank = True,null=True)
    none_timing = models.BooleanField(default=False)
    log = models.TextField(default="",blank=True)
    def __str__(self):
        return self.trigger_name

class FieldSize(models.Model):
    field_x = models.IntegerField()
    field_y = models.IntegerField()
# Create your models here.
MINE_OR_OTHER2 = (
    (0, '特になし'),
    (1, "共通"),
)
SHOW = (
    (0,"表示しない"),
    (1,"自分のみ"),
    (2,"両方"),
)
MONSTER_VARIABLE_SHOn = (
    (0,"表示しない"),
    (1,"表示"),
    (2,"0以外表示"),
)
SHOW2 = (
    (0,"表示しない"),
    (1,"表示"),
)
ETERNAL_EFFECT_VAL = (
    (0, "無効化 効果を受けない"),
    (1, '数値変動'),
    (3, '選択できない'),
    (2, '発動できない'),
)
ETERNAL_EFFECT_VAL2 = (
    (0, "永続無効化"),
    (1, '発動効果無効化'),
    (2, '無効化'),
    (3, '効果を受けない'),
    (4, "無効化　発動できない"),
)
MONSTER_EFFECT_VAL = (
    (0, "条件"),
    (1, '移動'),
    (17, 'シンプル移動'),
    (2, '変数変動'),
    (9, 'モンスター変数変動'),
    (3, '選択自分'),
    (4, '選択相手'),
    (5, '選択両者'),
    (7, 'フェイズ移動'),
    (8, 'ターンエンド'),
    (10, 'シャッフル'),
    (11, 'クリア'),
    (12, 'レイズ'),
    (13, '優先権移行'),
    (14, 'タイミング移行'),
    (19, 'タイミング次に移行'),
    (15, 'タイミングレイズ'),
    (24, '永続レイズ'),
    (16, 'Yes Or No'),
    (18, 'タイミング 変数移動'),
    (21, '音楽鳴らす'),
    (20, 'キャンセル'),
    (22, '勝利'),
    (23, '敗北'),
    (6, 'その他'),
)
ASK = (
    (0, "なし"),
    (1, "ターンプレイヤー"),
    (2, "非ターンプレイヤー"),
    (3, "両者"),
)
class Phase(models.Model):
    priority = models.IntegerField(unique=True)
    phase_name = models.CharField(max_length=32,default="")
    show = models.IntegerField(default=1,choices = SHOW2)
    def __str__(self):
        return self.phase_name
class DuelDeck(models.Model):
    room_number = models.IntegerField()
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER)
    deck_id= models.IntegerField();
    deck_content = models.TextField(blank=True)
class DuelGrave(models.Model):
    room_number = models.IntegerField()
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER)
    grave_id= models.IntegerField();
    grave_content = models.TextField(blank=True)
class DuelHand(models.Model):
    room_number = models.IntegerField()
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER)
    hand_id= models.IntegerField();
    hand_content = models.TextField(blank=True)
class Deck(models.Model):
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER2)
    min_deck_size = models.IntegerField();
    max_deck_size = models.IntegerField();
    deck_name = models.CharField(max_length = 32,default="")
    show = models.IntegerField(choices=SHOW)
    priority = models.IntegerField(default=100)
    max_deck_num = models.IntegerField(default=10)
    invoke = models.BooleanField(default=True)
    eternal = models.BooleanField(default=True)
    def __str__(self):
        return self.deck_name

class UserDeckGroup(models.Model):
    user= models.ForeignKey(User);
    deck_name=models.TextField(default="デッキ")
    user_deck_id  = models.IntegerField();
class DefaultDeckGroup(models.Model):
    deck_name=models.TextField(default="デッキ")
    default_deck_id  = models.IntegerField();
class UserDeck(models.Model):
    user= models.ForeignKey(User);
    deck_type = models.ForeignKey(Deck);
    deck_group = models.ForeignKey(UserDeckGroup);
    deck=models.TextField()
class DefaultDeck(models.Model):
    deck=models.TextField()
    deck_type = models.ForeignKey(Deck);
    deck_group = models.ForeignKey(DefaultDeckGroup,default="1");
class DefaultDeckChoice(models.Model):
    default_deck  = models.ForeignKey(DefaultDeckGroup,default="1");
class UserDeckChoice(models.Model):
    user = models.OneToOneField(User);
    user_deck  = models.ForeignKey(UserDeckGroup);
class Grave(models.Model):
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER2)
    show = models.IntegerField(default=0,choices=SHOW)
    grave_name = models.CharField(max_length = 32,default="")
    priority = models.IntegerField(default=100)
    invoke = models.BooleanField(default=True)
    eternal = models.BooleanField(default=True)
    def __str__(self):
        return self.grave_name
class Hand(models.Model):
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER2)
    show = models.IntegerField(default=0,choices = SHOW)
    max_hand_size = models.IntegerField(default=5);
    hand_name = models.CharField(max_length = 32,default="")
    invoke = models.BooleanField(default=True)
    eternal = models.BooleanField(default=True)
    def __str__(self):
        return self.hand_name

class Field(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    kind = models.CharField(max_length = 32,blank=True)
    mine_or_other = models.IntegerField(choices=MINE_OR_OTHER)

class MonsterVariablesKind(models.Model):
    monster_variable_sentence= models.TextField(null=True)
    monster_variable_name= models.CharField(max_length=32,null=True)
    def __str__(self):
        return self.monster_variable_name
class MonsterVariables(models.Model):
    monster_variable_name = models.CharField(max_length=32)
    monster_variable_label = models.CharField(max_length=32)
    monster_variable_kind_id = models.ForeignKey(MonsterVariablesKind,related_name='monster_variable_kind_id',on_delete = models.CASCADE)
    monster_variable_show = models.IntegerField(default = 0)
    priority = models.IntegerField()
    default_value = models.CharField(max_length=32)
    def __str__(self):
        return self.monster_variable_name
class Flag(models.Model):
    flag = models.BooleanField(default=False,blank=True)
class Monster(models.Model):
    monster_name = models.CharField(max_length=32)
    monster_sentence = models.TextField(default="",blank=True)
    monster_limit = models.IntegerField(default=3)
    monster_deck = models.CharField(max_length=32,default="1")
    monster_variable = models.ManyToManyField(MonsterVariables,through='MonsterItem')
    trigger = models.ManyToManyField(Trigger,blank=True)
    eternal_effect = models.ManyToManyField('EternalEffect',blank=True)
    img = models.CharField(max_length=32,default="",blank=True)

    def __str__(self):
        return self.monster_name
class MonsterItem(models.Model):
    monster_id= models.ForeignKey(Monster,related_name='monster_item',on_delete = models.CASCADE)
    monster_variables_id= models.ForeignKey(MonsterVariables,on_delete = models.CASCADE)
    monster_item_text = models.CharField(max_length=32,null=True)
class FieldKind(models.Model):
    field_kind_name = models.CharField(max_length=32)
    mine_or_other = models.IntegerField(default=0,choices = MINE_OR_OTHER2)
    def __str__(self):
        return self.field_kind_name
class GlobalVariable(models.Model):
    variable_name= models.CharField(max_length=32)
    priority= models.IntegerField(default=100)
    show = models.IntegerField(default=1,choices = SHOW2)
    initial_value = models.IntegerField(default=0)
    mine_or_other = models.IntegerField(default=0,choices = MINE_OR_OTHER2)
    def __str__(self):
        return self.variable_name
class VirtualVariable(models.Model):
    variable_name= models.CharField(max_length=32)
    priority= models.IntegerField(default=100)
    show = models.IntegerField(default=1,choices = SHOW2)
    value = models.TextField(default="")
    mine_or_other = models.IntegerField(default=0,choices = MINE_OR_OTHER2)
    def __str__(self):
        return self.variable_name
class MonsterEffectKind(models.Model):
    monster_effect_name = models.CharField(max_length=32)
    def __str__(self):
        return self.monster_effect_name
class MonsterEffect(models.Model):
    monster_effect_val = models.IntegerField(choices=MONSTER_EFFECT_VAL)
    monster_effect = models.TextField(blank=True)
    monster_condition = models.TextField(blank=True)
    prompt = models.TextField(blank=True)
    sentence = models.CharField(max_length=32,blank=True,default="")
    monster_effect_name = models.CharField(default="",max_length=32)
    eternal_flag = models.BooleanField(default = False)
    def __str__(self):
        return self.monster_effect_name
class PacCostWrapper(models.Model):
    cost_next = models.ForeignKey('CostWrapper',related_name = '%(class)s_cost_next',null=True,blank=True)
    cost_next2 = models.ForeignKey('CostWrapper',related_name='%(class)s_cost_next2',null=True,blank=True)
    pac_next = models.ForeignKey('PacCostWrapper',related_name  = '%(class)s_pac_cost_next',null=True,blank=True,default=None)
    pac_next2 = models.ForeignKey('PacCostWrapper',related_name  = '%(class)s_pac_cost_next2',null=True,blank=True,default=None)
    monster_effect_kind = models.CharField(max_length=32,blank=True)
    pac_cost= models.ForeignKey('PacCost',related_name='PacCost',on_delete = models.CASCADE)
    pac_cost_name = models.CharField(default="",max_length=32)
    log = models.TextField(default="",blank=True)
    def __str__(self):
        return self.pac_cost_name
class PacCost(models.Model):
    pac_cost_next = models.ForeignKey('CostWrapper',null=True,blank=True,related_name='%(class)s_pac_cost_next')
    pac_cost_name = models.CharField(default="",max_length=32)
    def __str__(self):
        return self.pac_cost_name
class PacWrapper(models.Model):
    monster_effect_next = models.ForeignKey('MonsterEffectWrapper',related_name = '%(class)s_monster_effect_next',null=True,blank=True)
    monster_effect_next2 = models.ForeignKey('MonsterEffectWrapper',related_name='%(class)s_monster_effect_next2',null=True,blank=True)
    pac_next = models.ForeignKey('PacWrapper',related_name  = '%(class)s_pac_cost_next',null=True,blank=True,default=None)
    pac_next2 = models.ForeignKey('PacWrapper',related_name  = '%(class)s_pac_cost_next2',null=True,blank=True,default=None)
    monster_effect_kind = models.CharField(max_length=32,blank=True)
    pac= models.ForeignKey('Pac',related_name='Pac',on_delete = models.CASCADE)
    pac_name = models.CharField(default="",max_length=32)
    log = models.TextField(default="",blank=True)
    def __str__(self):
        return self.pac_name
class Pac(models.Model):
    pac_next = models.ForeignKey('MonsterEffectWrapper',null=True,blank=True,related_name='%(class)s_pac_next')
    pac_name = models.CharField(default="",max_length=32)
    def __str__(self):
        return self.pac_name
class EternalWrapper(models.Model):
    priority = models.IntegerField(default="100")
    monster_effect= models.ForeignKey(MonsterEffect,related_name='eternal_wrapper',on_delete = models.CASCADE)
    monster_effect_kind = models.CharField(max_length=32,blank=True)
    monster_effect_next = models.ForeignKey('self',null=True,blank=True)
    monster_effect_next2= models.ForeignKey('self',related_name='%(class)s_monster_effect_next2',default=None,null=True,blank=True);
    monster_effect_name = models.CharField(default="",max_length=32)
    log = models.TextField(default="",blank=True)
    none_timing = models.BooleanField(default=False,blank=True)
    def __str__(self):
        return self.monster_effect_name
class MonsterEffectWrapper(models.Model):
    monster_effect= models.ForeignKey(MonsterEffect,related_name='monster_effect_wrapper',on_delete = models.CASCADE)
    monster_effect_kind = models.CharField(max_length=32,blank=True)
    monster_effect_next = models.ForeignKey('self',null=True,blank=True)
    monster_effect_next2= models.ForeignKey('self',related_name='%(class)s_monster_effect_next2',default=None,null=True,blank=True);
    pac = models.ForeignKey(PacWrapper,null=True,blank=True,related_name = '%(class)s_pac')
    pac2= models.ForeignKey(PacWrapper,related_name='%(class)s_pac2',default=None,null=True,blank=True);
    monster_effect_name = models.CharField(default="",max_length=32)
    log = models.TextField(default="",blank=True)
    def __str__(self):
        return self.monster_effect_name
class EternalEffect(models.Model):
    eternal_effect_val = models.IntegerField(choices=ETERNAL_EFFECT_VAL,default=0)
    eternal_effect_val2 = models.IntegerField(choices=ETERNAL_EFFECT_VAL2,default=0)
    priority = models.IntegerField(default="100")
    turn = models.IntegerField(choices=MINE_OR_OTHER)
    chain = models.IntegerField(default=0,blank=True,null=True)
    chain_kind = models.IntegerField(default=0,blank=True,choices = CHAIN)
    phase = models.ForeignKey('Phase',default=None,blank=True,null=True)
    mine_or_other = models.IntegerField(choices = MINE_OR_OTHER,default=0)
    eternal_effect_condition = models.TextField(default="",blank=True)
    eternal_effect = models.TextField(default="",blank=True)
    eternal_effect_det = models.TextField(default="",blank=True)
    eternal_timing = models.BooleanField(default=False,blank=True)
    eternal_monster = models.TextField(default=None,null=True,blank=True)
    eternal_global_variable = models.TextField(default=None,null=True,blank=True)
    eternal_global_variable_val = models.CharField(max_length=32,default=None,null=True,blank=True)
    eternal_variable = models.CharField(max_length=32,default="",blank=True)
    eternal_variable_val = models.IntegerField(default=0,null=True,blank=True)
    eternal_name = models.CharField(max_length=32,default=None,null=True,blank=True)
    eternal_kind = models.CharField(max_length=32,default="",blank=True)
    invalid_eternal_kind = models.CharField(max_length=32,default="",blank=True)
    invalid_monster = models.TextField(default="",blank=True)
    timing = models.ManyToManyField(Timing,default=None,blank = True,null=True)
    none_timing = models.BooleanField(default=False)
    none_monster = models.BooleanField(default=False)
    persist = models.BooleanField(default=False)
    def __str__(self):
        return self.eternal_name
class Cost(models.Model):
    cost_val = models.IntegerField(choices=MONSTER_EFFECT_VAL)
    cost = models.TextField(blank=True)
    cost_condition = models.TextField(default="",blank=True)
    cost_name = models.CharField(default="",max_length=32)
    prompt = models.TextField(blank=True)
    sentence = models.CharField(max_length=32,blank=True,default="")
    def __str__(self):
        return self.cost_name
class CostWrapper(models.Model):
    cost= models.ForeignKey(Cost,related_name='cost_wrapper',on_delete = models.CASCADE)
    cost_kind = models.CharField(max_length=32,blank=True,default="")
    cost_next = models.ForeignKey('self',null=True,blank=True)
    cost_next2= models.ForeignKey('self',related_name='%(class)s_cost_next2',default=None,null=True,blank=True);
    pac = models.ForeignKey('PacCostWrapper',null=True,blank=True,related_name = '%(class)s_pac')
    pac2= models.ForeignKey('PacCostWrapper',related_name='%(class)s_pac2',default=None,null=True,blank=True);
    cost_name = models.CharField(default="",max_length=32)
    log = models.TextField(default="",blank=True)
    def __str__(self):
        return self.cost_name
class Battle(models.Model):
    battle_number = models.IntegerField()
    attaker = models.CharField(max_length=32)
class Duel(models.Model):
    field = models.TextField(blank=True)
    turn_count = models.IntegerField(default=0)
    ask = models.IntegerField(default=0,choices = ASK);
    ask_kind= models.CharField(max_length = 32,blank=True,default="")
    ask_det = models.TextField(default="");
    answer = models.TextField(default="");
    user_turn = models.IntegerField(default=0)
    phase = models.ForeignKey(Phase,default=None,blank=True,null=True)
    global_variable = models.TextField(default="",blank=True)
    user_1= models.ForeignKey(User,blank=True,related_name='%(class)s_requests_user_1',default=None,null=True);
    user_2= models.ForeignKey(User,default=None,blank=True,null=True);
    chain = models.IntegerField(default=0,blank=True,null=False)
    chain_det = models.TextField(default="",blank=True)
    chain_user = models.TextField(default="",blank=True)
    mess = models.TextField(blank=True,default="")
    in_cost = models.BooleanField(default=False)
    in_trigger_waiting = models.BooleanField(default=False)
    cost_result = models.TextField(blank=True,default="")
    cost = models.TextField(blank=True,default="")
    cost_det = models.IntegerField(default=0,blank=True)
    cost_user = models.IntegerField(default=0,blank=True)
    trigger_waiting = models.TextField(default="",blank=True)
    appoint = models.IntegerField(default=0,blank=True)
    timing = models.ForeignKey(Timing,default=None,blank=True,null = True)
    timing_waiting = models.ForeignKey(Trigger,default=None,blank=True,null = True)
    timing_mess = models.TextField(default="")
    current_priority = models.IntegerField(default=10000)
    pac = models.IntegerField(default=0,blank=True,null=False)
    in_pac = models.TextField(default="",blank = True)
    in_pac_cost = models.TextField(default="",blank = True)
    no_invoke_eternal_effect = models.TextField(default="",blank = True)
    #invoke_invalid_eternal_effect = models.TextField(default="",blank = True)
    #no_choose_eternal_effect = models.TextField(default="",blank = True)
    #no_eternal_eternal_effect = models.TextField(default="",blank = True)
    #not_effected_eternal_effect = models.TextField(default="",blank = True)
    #change_val_eternal_effect = models.TextField(default="",blank = True)
    audio = models.CharField(max_length=32,default="",blank=True)
    log = models.TextField(default="",blank=True)
    log_turn = models.TextField(default="",blank=True)
    cost_log= models.TextField(default="",blank=True)
    duel_id = models.TextField(default="",blank=True)
    winner = models.IntegerField(default=0,blank=True)
    in_eternal = models.BooleanField(default=False)
    eternal_det = models.TextField(default="",blank=True)
    in_pac_eternal = models.TextField(default="",blank = True)
    eternal_mess = models.TextField(default="",blank=True)
    eternal_user = models.TextField(default="",blank=True)
    time_1 = models.FloatField(default=0.0)
    time_2 = models.FloatField(default=0.0)
    waiting = models.BooleanField(default=False)
    end_time = models.FloatField(default=0.0)
class Config(models.Model):
    cancel_name = models.CharField(max_length=32)
    game_name = models.CharField(max_length=32,default="")
    hide_name = models.CharField(max_length=32,default="")
    limit_time = models.IntegerField(default=300)
    time_win = models.CharField(default="",blank=True,max_length=32)
    beep = models.BooleanField(default=False)
    common_name = models.CharField(default="共有",max_length=32)
    gray_out = models.ForeignKey(MonsterVariables,default=None,blank=True,null=True)
    default_sort = models.ForeignKey(MonsterVariables,default=None,blank=True,null=True,related_name="default_sort")

