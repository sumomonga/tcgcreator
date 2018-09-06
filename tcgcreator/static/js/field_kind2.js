	var prev;
	var monster_kind_id = [];
	var current_i = 0;
	$(document).ready(function(){
	
		getEffectConditionChange(0);
	});
	function getEffectConditionBefore(){
		getEffectConditionChange(current_i)
	}
	function deleteEffectConditionChange(i){
		$("#monster_effect_condition-"+i).remove()
		var val = $("#id_monster_effect_condition").val().split("_");
		var val2;
		for(var j=0;j<val.length;j++){
			if(i!=j){
				val2 += val+"_";
			}
			
		}
		val2 = val2.substr(0,val2.length-1);
		$("#id_monster_effect_condition").val(val2);
	}
	function changeField2Num(){
		var tmp_str = "";
		for(var i=0;i<current_i;i++){
			tmp_str+=$("#field_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_kind").val(tmp_str);

	}
	function getEffectConditionChange(num){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_field_kind2/",
   'data': "delete_flag=0&num="+num,
'success': function(data){
		$("#id_kind").prop("type","hidden");
		if(num==0 ){
			current_i++;
		}else{
			$("#field_kind-"+(num-1)).after(data);
			changeField2Num();
			current_i++;
		}
        } 
	})
		
	}
