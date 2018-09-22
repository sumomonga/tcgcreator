	var eternal_effect_kind_id = [];
	var condition_i = 0;
	function getEternalEffectConditionVariables(){
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_variable_kind/",
		   'data': "",
		'success': function(data){
			$("#variable_condition_tab").show();
			$(".variable_condition").show();
			$("#variable_condition_1").html(data);
		}
		});
	}
	function addEternalEffectConditionVariables(i){
		var html = $("#variable_condition_1").html();
		and_or = "または";
		var html = and_or+'<select id="variable_condition_'+(i+1)+'" class="variable_condition" >'+html+'</select>';
		html+='<select id="variable_condition_equation_'+(i+1)+'" class="variable_condition" ><option value="=">=</option><option value="<=">&lt;=</option><option value=">=">&gt;=</option><option value="!=">!=</option></select>';
		html+='<select id="variable_condition_add_'+(i+1)+'" onchange="addEternalEffectConditionVariable('+(i+1)+')" class="variable_condition" ><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		html+='<input type="text" id="variable_equation_val_'+(i+1)+'">';
		$("#variable_condition_add_"+i).after(html);
		$("#variable_condition_add_"+(i)).remove();;
	}
	
