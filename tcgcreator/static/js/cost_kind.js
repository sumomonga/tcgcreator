	var prev;
	var monster_kind_id = [];
	var cost_kind_i = 0;
	$(document).ready(function(){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind/",
   'data': "delete_flag=0&num=0",
'success': function(data){
		$("#id_cost_kind").after("<input type=\"button\" onclick=\"changeMonsterKindNum()\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterChangeKind()\" value=\"削除\"><br>");
			$("#id_cost_kind").after(data);
        } 
	})
	});
	function deleteMonsterChangeKind(){
		$("#id_cost_kind").val("");
	}
	function changeMonsterKindNum(){
		var tmp_str,tmp;
		tmp = $("#id_cost_kind").val();
		tmp_str=$("#monster_kind-0").val();
		if(tmp == ""){
			tmp = tmp_str;
		}else{
			tmp += "_"+tmp_str;
		}
		$("#id_cost_kind").val(tmp);

	}
	
		
