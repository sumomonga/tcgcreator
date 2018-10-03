monster_kind_i = 0;
	function deleteTriggerTimingKinds(){
		for(var i=0;i<monster_kind_i;i++){
			$("#monster_kind-"+i).remove()
		}
		$("#id_kinds").val("");
		getTriggerTimingKindChange(0);
		monster_kind_i=0;
	}
	function getTriggerTimingKindChange(0){

	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind/",
   'data': "delete_flag=0&id2=id_kinds&id=id_kinds&num="+num,
'success': function(data){
			$("#id_kinds").after(data);
        }
	})

	}
	$(document).ready(function(){
		$("#id_kinds").after("<input type=\"button\" onclick=\"getTriggerTimingKindChangeBefore()\" value=\"追加\"><input type=\"button\" onclick=\"deleteTriggerTimingKindChange()\" value=\"削除\"><br>");
		getTriggerTimingKindChange(0);
	});
	function getTriggerTimingKindChangeBefore(){
		getTriggerTimingKindChange(monster_kind_i)
	}
