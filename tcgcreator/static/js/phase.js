	var current_i = 0;	
	$(document).ready(function(){
	
		$("#id_next_phase").after("<input type=\"button\" onclick=\"getNextPhase()\" value=\"追加\"><input type=\"button\" onclick=\"deleteNextPhase()\" value=\"削除\"><br>");
	});
	function deleteNextPhase(){
		for(var i=0;i<current_i;i++){
			$("#next_phase-"+i).remove()
		}
		$("#id_next_phase").val("");
		current_i=0;
	}
	function getNextPhase(){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_timing/",
   'data': "num="+current_i,
'success': function(data){
		$("#id_next_phase").prop("type","hidden");
		var result = '<select id="next_phase-'+current_i+'">'+data+'</select>'
		if(current_i==0 ){
			$("#id_next_phase").after(result);
			current_i++;
			changePhaseKindNum();
		}else{
			$("#next_phase-"+(current_i-1)).after(result);
			current_i++;
			changePhaseKindNum();
		}
		
        } 
	})
		
	}
	function changePhaseKindNum(){
		var tmp_str = "";
		for(var i=0;i<current_i;i++){
			tmp_str+=$("#next_phase-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_next_phase").val(tmp_str);

	}
