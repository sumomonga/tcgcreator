	var trigger_kind_id = [];
	var condition_i = 0;
	var global_trigger_val=1;
	$(document).ready(function(){
	
		$("#id_trigger_timing").after("<input type=\"button\" onclick=\"getTriggerTiming()\" value=\"追加\">");
		$("#id_trigger_condition").after("<input type=\"button\" onclick=\"getConditionKind('trigger_condition',0,100,0)\" value=\"追加\">");
		// $("#id_trigger_cost").after("<input type=\"button\" onclick=\"getTriggerCost()\" value=\"追加\">");
		$("#id_trigger_monster").after("<input type=\"button\" onclick=\"getConditionKind('trigger_monster',0,100,0)\" value=\"追加\">");
		$(".submit-row").prepend('<input type="button" onclick="gotoDiagram()" value="diagram">');
		getTriggerChange(0);
	});
	function gotoDiagram(){
	location.href = "../diagram"
	}
	function getTriggerCondition(){
		$("#monster_condition").show();
		$("#monster_condition").draggable();
		getTriggerConditionKind(-1);
	}
	
	function changeConditionNum(){
		var tmp_str = "";
		for(var i=0;i<condition_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_trigger_effect_kind").val(tmp_str);

	}
	var monter_kind_i = 0;
	
	function getTriggerChangeBefore(){
		getTriggerChange(monter_kind_i)
	}
	function deleteTriggerChange(){
		for(var i=0;i<monter_kind_i;i++){
			$("#monster_kind-"+i).remove()
		}
		$("#id_trigger_kind").val("");
		getTriggerChange(0);
		monter_kind_i=0;
	}
	function getTriggerChange(){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind/",
   'data': "delete_flag=0&id=id_trigger_kind&id2=id_trigger_kind&num=0",
'success': function(data){
			$("#id_trigger_kind").after(data);
        } 
	})
		
	}
	function getTriggerCost(){
		$("#monster_cost").show();
		$("#monster_cost").draggable();
		getTriggerCostKind(-1);
	}
	
	function changeCostNum(){
		var tmp_str = "";
		for(var i=0;i<cost_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_trigger_effect_kind").val(tmp_str);

	}
	function getTriggerCostKind(cost_kind){
		if(cost_kind == "0" || cost_kind == "1"){
			$("#monster_cost_place_tab").show();
		}else{
			$("#monster_cost_place_hide").show();
		}
		if(cost_kind == "0"){
			$("#monster_cost_place_to_wrapper").show();
		}else{
			$("#monster_cost_place_to_wrapper").hide();
		}
		$("#monster_cost").show();
		$("#monster_cost").offset({top:0,left:200});
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "",
'success': function(data){
		$(".monster_cost_place").show();
		$("#monster_cost_place_1").html(data);
		$("#monster_cost_place_to").html(data);
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster/",
			   'data': "",
			'success': function(data){
					$("#monster_cost_monster").show();
					$("#monster_cost_monster").html(data);
					$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_equation/",
			  			 'data': "",
						'success': function(data){
							$("#monster_cost_equation").show();
							$("#monster_cost_equation").html(data);
			      		 } 
					})
			        } 
				})
        } 
	})
	}	
	function addTriggerCostPlace(i){
		var html = $("#monster_cost_place_1").html();
		and_or = "または";
		var html = and_or+'<select id="monster_cost_place_'+(i+1)+'" class="monster_cost_place" >'+html+'</select>';
		html+='<select id="monster_cost_place_add_'+(i+1)+'" onchange="addTriggerCostPlace('+(i+1)+')" class="monster_cost_place" ><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		$("#monster_cost_place_add_"+i).after(html);
		$("#monster_cost_place_add_"+(i)).remove();;
	}
	function putTriggerCost(){
		var val= $("#id_trigger_cost").val();
		var tmp = $("#monster_cost_place_1").val();
		var place = "(";
		var place_to;
		var tmp2 =$("#monster_cost_kind").val();
		if(tmp2 == "0"){
			place_to = $("#monster_cost_place_to").val();
			place_to = "(place_to = "+place_to+")";
		}else if(tmp2=="1"){
			place_to = "(place_designation)";
		}
		
		if(tmp != "0"){
			place += "place = "+tmp;
			for(var i=2;$("#monster_cost_place_add_"+(i-1)).val();i++){
				var tmp = $("#monster_cost_place_"+i).val();
				var operator = $("#monster_cost_place_add_"+(i-1)).val();
				if(tmp != "0"){
					place += " "+operator+" "+tmp;
				}
			}
			place+=")";
		}
		var monster_cost = "";
		var j=0;
		for(var i=1;$("#get_monster_variable_"+i).length != 0;i++){
			if($("#get_monster_variable_equal_"+i).length != 0){
				num = $("#get_monster_variable_"+i).val();
				operator = $("#get_monster_variable_equal_"+i).val();
				if(operator == ""){
					continue;
				}
				monster_cost += '(id='+i+'&num='+num+'&operator='+operator+')';
				j++;
			}else{
				num = $("#get_monster_variable_"+i).val();
				if(num == "0" || num == ""){
					continue;
				}
				monster_cost += "(id="+i+"&num="+num+"&operator=)";
				j++;
			}
			
		}
		equation = "(equation = '"+$("#get_equation_det").val()+"')";
		equation_kind = "(equation_kind = "+$("#get_equation_kind").val()+")";
		equation_number = "(equation_number = "+$("#get_equation_number").val()+")";
		if($("#get_monster_name_equal").val() == ""){
			monster_name_kind = "";
		}else if($("#get_monster_name_equal").val() == "="){
			monster_name_kind = '(monster_name_kind = "+$("#monster_name").val()+")';
		}else{
			monster_name_kind = '(monster_name_kind like "+$("#monster_name").val()+")';
		}
		val += "{"+place+place_to+monster_name_kind+monster_cost+equation+equation_kind+equation_number+"}";
		$("#id_trigger_cost").val(val);
		$("#monster_cost").hide();
		$("#monster_monster").hide();
		$("#monster_equation").hide();
		$("#monster_cost_place_to_wrapper").hide();
		$(".monster_cost_place").hide();
		for(var i=2;$("#monster_cost_place_"+(i)).length;i++){
			$("#monster_cost_place_"+i).remove();
			$("#monster_cost_place_add"+i).remove();
			
		}
		
		
	}
	function getTriggerMonster(){
		$("#trigger_monster").show();
		$("#trigger_monster").draggable();
		getTriggerMonsterKind();
	}
	
	function changeTriggerMonsterNum(){
		var tmp_str = "";
		for(var i=0;i<cost_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_trigger_effect_kind").val(tmp_str);

	}
	function getTriggerMonsterKind(){
			$("#monster_monster_place_tab").show();
		$("#trigger_monster").show();
		$("#trigger_monster").offset({top:0,left:200});
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "",
'success': function(data){
		$(".monster_monster_place").show();
		$("#monster_monster_place_1").html(data);
		$("#monster_monster_place_to").html(data);
		$("#monster_condition_place_1").html("");
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster/",
			   'data': "",
			'success': function(data){
					$("#monster_monster_monster").show();
					$("#monster_monster_monster").html(data);
					$("#monster_monster").html("");
			        } 
				})
        } 
	})
	}	
	function addTriggerMonsterPlace(i){
		var html = $("#monster_monster_place_1").html();
		and_or = "または";
		var html = and_or+'<select id="monster_monster_place_'+(i+1)+'" class="monster_monster_place" >'+html+'</select>';
		html+='<select id="monster_monster_place_add_'+(i+1)+'" onchange="addTriggerCostPlace('+(i+1)+')" class="monster_monster_place" ><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		$("#monster_monster_place_add_"+i).after(html);
		$("#monster_monster_place_add_"+(i)).remove();;
	}
	function putTriggerMonster(){
		var val= $("#id_trigger_monster").val();
		var tmp = $("#monster_monster_place_1").val();
		var place = "(";
		var place_to;
		var tmp2 =$("#monster_monster_kind").val();
		var json={};
		if(val == ""){
			val2=[];
		}else{
			val2= JSON.parse(val);
		}
		json["place"]  = [];
		if(tmp != "0"){
			json["place"][0] = tmp;
			var place_counter=1;
			for(var i=2;$("#monster_monster_place_add_"+(i-1)).val();i++){
				var tmp = $("#monster_monster_place_"+i).val();
				if(tmp != "0"){
					json["place"][place_counter] =tmp;
					place_counter++;
				}
			}
		}
		json["monster_monster"] = [];
		var j=0;
		for(var i=1;$("#get_monster_variable_"+i).length != 0;i++){
			json["monster_monster"][i-1] = {};
			if($("#get_monster_variable_equal_"+i).length != 0){
				num = $("#get_monster_variable_"+i).val();
				operator = $("#get_monster_variable_equal_"+i).val();
				if(operator == ""){
					continue;
				}
				json["monster_monster"][i-1]["num"]= num
				json["monster_monster"][i-1]["operator"]= operator;
			}else{
				num = $("#get_monster_variable_"+i).val();
				if(num == "0" || num == ""){
					continue;
				}
				json["monster_monster"][i-1]["num"]= num
				json["monster_monster"][i-1]["operator"]= "=";
			}
			
		}
		if($("#get_monster_name_equal").val() == ""){
			json["monster_name_kind"] = "";
		}else if($("#get_monster_name_equal").val() == "="){
			json["monster_name_kind"] = {};
			json["monster_name_kind"]["operator"] = "=";
			json["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}else{
			json["monster_name_kind"] = {};
			json["monster_name_kind"]["operator"] = "like";
			json["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}
		json["as_trigger_monster"] = $("#as_monster_monster").val()
		val2.push(json)
		val = JSON.stringify(val2);
		$("#id_trigger_monster").val(val);
		$("#trigger_monster").hide();
		$("#trigger_monster").hide();
		$("#monster_equation").hide();
		$(".monster_monster_place").hide();
		for(var i=2;$("#monster_monster_place_"+(i)).length;i++){
			$("#monster_monster_place_"+i).remove();
			$("#monster_monster_place_add"+i).remove();
			
		}
		
		
	}
	function getTriggerTiming(){
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_timing/",
			   'data': "",
			'success': function(data){
					$("#timing").show();
					$("#timing").draggable();
					$("#timing").offset({top:0,left:200});
					$("#timing_phase").html(data);
			        } 
				})
        } 
	function putTiming(){
		var phase = $("#timing_phase").val();
		
		$("#id_trigger_timing").val(phase);	
	}
