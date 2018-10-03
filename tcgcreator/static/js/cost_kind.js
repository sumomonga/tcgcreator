	var prev;
	var monster_kind_id = [];
	var cost_kind_i = 0;
	$(document).ready(function(){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind/",
   'data': "delete_flag=0&id2=id_cost_kind&id=id_cost_kind&num=0",
'success': function(data){
		$("#id_cost_kind").after("<input type=\"button\" onclick=\"deleteMonsterChangeKind()\" value=\"削除\"><br>");
			$("#id_cost_kind").after(data);
        } 
	})
	});
	function deleteMonsterChangeKind(){
		$("#id_cost_kind").val("");
	}
	
		
