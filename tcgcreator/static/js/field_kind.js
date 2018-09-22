	var prev;
	var monster_kind_id = [];
	$(document).ready(function(){
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_field_kind/",
   'data': "delete_flag=0&num="+0,
'success': function(data){
			$("#id_kind").after("<input type=\"button\" onclick=\"changeFieldNum()\" value=\"追加\"><input type=\"button\" onclick=\"deleteFieldChange()\" value=\"削除\"><br>");
			$("#id_kind").after(data);
	
		}
	});
	});
	function deleteFieldChange(){
		$("#id_kind").val("");
	}
	function changeFieldNum(){
		var tmp,tmp_str;
		tmp = $("#id_kind").val();
		tmp_str=$("#field_kind-0").val();
		if(tmp == ""){
			tmp = tmp_str;
		}else{
			tmp += "_"+tmp_str;
		}
		$("#id_kind").val(tmp);
	}
