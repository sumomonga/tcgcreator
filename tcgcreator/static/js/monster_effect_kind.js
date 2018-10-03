	var prev;
	var monster_kind_id = [];
	var monster_effect_kind_i = 0;
	$(document).ready(function(){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind/",
   'data': "delete_flag=0&num=0",
'success': function(data){
		$("#id_monster_effect_kind").after("<input type=\"button\" onclick=\"changeMonsterKindNum('id_monster_effect_kind',monster_kind,1')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterChangeKind()\" value=\"削除\"><br>");
			$("#id_monster_effect_kind").after(data);
        } 
	})
	});
	function deleteMonsterChangeKind(){
		$("#id_monster_effect_kind").val("");
	}
	
		
