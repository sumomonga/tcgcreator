monster_kind_i = 0;
	function deleteTriggerTimingKinds(){
		for(var i=0;i<monster_kind_i;i++){
			$("#monster_kind-"+i).remove()
		}
		$("#id_kinds").val("");
		getTriggerTimingKindChange(0);
		monster_kind_i=0;
	}
	function getTriggerTimingKindChange(num){

	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind/",
   'data': "delete_flag=0&num="+num,
'success': function(data){
		if(num==0 ){
			$("#id_kinds").after(data);
			monster_kind_i++;
		}else{
			$("#monster_kind-"+(num-1)).after(data);
			monster_kind_i++;
		}
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
	function changeMonsterKindNum(){
		var tmp_str = "";
		for(var i=0;i<monster_kind_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_kinds").val(tmp_str);

	}
