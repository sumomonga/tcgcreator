	var eternal_effect_kind_id = [];
	var condition_i = 0;
	$(document).ready(function(){
	
		$("#id_eternal_effect_timing").after("<input type=\"button\" onclick=\"getEternalEffectTiming()\" value=\"追加\">");
		$("#id_eternal_effect_condition").after("<input type=\"button\" onclick=\"getConditionKind('eternal_effect_condition',0)\" value=\"追加\">");
		// $("#id_eternal_effect_cost").after("<input type=\"button\" onclick=\"getEternalEffectCost()\" value=\"追加\">");
		$("#id_eternal_monster").after("<input type=\"button\" onclick=\"getConditionKind('eternal_monster',0)\" value=\"追加\">");
		$("#id_invalid_monster").after("<input type=\"button\" onclick=\"getConditionKind('invalid_monster',0)\" value=\"追加\">");
		$("#id_eternal_kind").after("<input type=\"button\" onclick=\"getEternalEffectChangeBefore()\" value=\"追加\"><input type=\"button\" onclick=\"deleteEternalEffectChange()\" value=\"削除\"><br>");
		$("#id_invalid_eternal_kind").after("<input type=\"button\" onclick=\"getInvalidEternalEffectChangeBefore()\" value=\"追加\"><input type=\"button\" onclick=\"deleteInvalidEternalEffectChange()\" value=\"削除\"><br>");
		$("#id_eternal_variable").after("<input type=\"button\" onclick=\"getVariable('eternal_variable')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");

		getEternalEffectChange(0);
		getInvalidEternalEffectChange(0);
	});
	function getEternalEffectVariable(){
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_variable_kind/",
		   'data': "",
		'success': function(data){
			$("#eternal_variable").show();
			$("#eternal_variable").offset({top:0,left:200});
			$("#eternal_variable").draggable();
			console.log(data);
			$("#eternal_variable_select").html(data);
		}
		});
	}
	function putEternalEffectVariable(){
		$("#id_eternal_variable").val($("#eternal_variable_select").val());
		$("#eternal_variable").hide();
		
	}
	function  hideAllWindow(){
	}
	function getEternalEffectConditionVariables(){
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_variable_kind/",
		   'data': "",
		'success': function(data){
			$(".variable_condition_").show();
			$("#variable_condition_1").html(data);
		}
		});
	}
	var monster_kind_i = 0;
	var invalid_monster_kind_i = 0;

	function getEternalEffectChangeBefore(){
		getEternalEffectChange(monster_kind_i)
	}
	function getInvalidEternalEffectChangeBefore(){
		getInvalidEternalEffectChange(invalid_monster_kind_i)
	}
	function deleteInvalidEternalEffectChange(){
		for(var i=0;i<monster_kind_i;i++){
			$("#invalid_monster_kind-"+i).remove()
		}
		$("#id_invalid_eternal_kind").val("");
		getInvalidEternalEffectChange(0);
		invalid_monster_kind_i=0;
	}
	function deleteEternalEffectChange(){
		for(var i=0;i<monster_kind_i;i++){
			$("#monster_kind-"+i).remove()
		}
		$("#id_eternal_kind").val("");
		getEternalEffectChange(0);
		monster_kind_i=0;
	}
	function changeInvalidMonsterKindNum(){
		var tmp_str = "";
		for(var i=0;i<invalid_monster_kind_i;i++){
			tmp_str+=$("#invalid_monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_invalid_eternal_kind").val(tmp_str);

	}
	function changeMonsterKindNum(){
		var tmp_str = "";
		for(var i=0;i<monster_kind_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_eternal_kind").val(tmp_str);

	}
	function getInvalidEternalEffectChange(num){

	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_invalid_monster_kind/",
   'data': "delete_flag=0&num="+num,
'success': function(data){
		if(num==0 ){
			$("#id_invalid_eternal_kind").after(data);
			invalid_monster_kind_i++;
		}else{
			$("#invalid_monster_kind-"+(num-1)).after(data);
			invalid_monster_kind_i++;
		}
        }
	})

	}
	function getEternalEffectChange(num){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind/",
   'data': "delete_flag=0&num="+num,
'success': function(data){
		if(num==0 ){
			$("#id_eternal_kind").after(data);
			monster_kind_i++;
		}else{
			$("#monster_kind-"+(num-1)).after(data);
			monster_kind_i++;
		}
        } 
	})
		
	}
	function getEternalEffectCost(){
		$("#monster_cost").show();
		$("#monster_cost").draggable();
		getEternalEffectCostKind(-1);
	}
	
	function changeCostNum(){
		var tmp_str = "";
		for(var i=0;i<cost_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_eternal_effect_effect_kind").val(tmp_str);

	}
	function getEternalEffectCostKind(cost_kind){
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
	function addEternalEffectCostPlace(i){
		var html = $("#monster_cost_place_1").html();
		and_or = "または";
		var html = and_or+'<select id="monster_cost_place_'+(i+1)+'" class="monster_cost_place" >'+html+'</select>';
		html+='<select id="monster_cost_place_add_'+(i+1)+'" onchange="addEternalEffectCostPlace('+(i+1)+')" class="monster_cost_place" ><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		$("#monster_cost_place_add_"+i).after(html);
		$("#monster_cost_place_add_"+(i)).remove();;
	}
	function putEternalEffectCost(){
		var val= $("#id_eternal_effect_cost").val();
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
		$("#id_eternal_effect_cost").val(val);
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
	function getEternalEffectMonster(){
		$("#eternal_effect_monster").show();
		$("#eternal_effect_monster").draggable();
		getEternalEffectMonsterKind();
	}
	
	function changeEternalEffectMonsterNum(){
		var tmp_str = "";
		for(var i=0;i<cost_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_eternal_effect_effect_kind").val(tmp_str);

	}
	function getEternalEffectMonsterKind(){
			$("#monster_monster_place_tab").show();
		$("#eternal_effect_monster").show();
		$("#eternal_effect_monster").offset({top:0,left:200});
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
	function addEternalEffectMonsterPlace(i){
		var html = $("#monster_monster_place_1").html();
		and_or = "または";
		var html = and_or+'<select id="monster_monster_place_'+(i+1)+'" class="monster_monster_place" >'+html+'</select>';
		html+='<select id="monster_monster_place_add_'+(i+1)+'" onchange="addEternalEffectCostPlace('+(i+1)+')" class="monster_monster_place" ><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		$("#monster_monster_place_add_"+i).after(html);
		$("#monster_monster_place_add_"+(i)).remove();;
	}
	function putEternalEffectMonster(){
		var val= $("#id_eternal_effect_monster").val();
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
		json["as_eternal_effect_monster"] = $("#as_monster_monster").val()
		val2.push(json)
		val = JSON.stringify(val2);
		$("#id_eternal_effect_monster").val(val);
		$("#eternal_effect_monster").hide();
		$("#eternal_effect_monster").hide();
		$("#monster_equation").hide();
		$(".monster_monster_place").hide();
		for(var i=2;$("#monster_monster_place_"+(i)).length;i++){
			$("#monster_monster_place_"+i).remove();
			$("#monster_monster_place_add"+i).remove();
			
		}
		
		
	}
	function getEternalEffectTiming(){
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
		
		$("#id_eternal_effect_timing").val(phase);	
	}
