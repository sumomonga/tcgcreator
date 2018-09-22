	var prev;
	var monster_kind_id = [];
	var effect_move_i = 0;
	var global_target_math = "";
	
	var monster_or_global;	
	$(document).ready(function(){
		hideAllWindow();
		$("#id_cost_condition").after("<input type=\"button\" onclick=\"getConditionKind('cost_condition',0,100,0)\" value=\"追加\">");
	
		switch($("#id_cost_val").val()){
			case "5":
				$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterChooseBoth('cost')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
				$("#monster_who").show();
				break;
		    case "17":
				$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectTimingVariable()\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
		        break;
			case "1":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectMovePlace('cost')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
			break;
			case '3':
			case "4":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectMove('cost')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
				$("#monster_who").hide();
				break;
			case "7":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectMovePhase(0)\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
			break;
			case "8":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectChangeTurn(0)\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
			break;
			case "2":
			$("#id_cost").after("<input type=\"button\" onclick=\"getVariableChange(0)\" value=\"追加\"><input type=\"button\" onclick=\"deleteVariableChange(0)\" value=\"削除\"><br>");
				break;
			case "9":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterVariableChange('cost')\" value=\"追加\"><input type=\"button\" onclick=\"deleteVariableChange(0)\" value=\"削除\"><br>");
				break;
			}
		$("#id_cost_val").change(function(){
		hideAllWindow();
			switch($("#id_cost_val").val()){
		    case "17":
				$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectTimingVariable()\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
		        break;
				case "1":
				$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectMovePlace('cost')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
				$("#monster_who").hide();
				break;
				case "3":
				case "4":
				$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectMove('cost')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
				$("#monster_who").hide();
				break;
				case "5":
				$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterChooseBoth('cost')\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
				$("#monster_who").show();
				break;
			case "7":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectMovePhase(0)\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
			break;
			case "8":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterEffectChangeTurn(0)\" value=\"追加\"><input type=\"button\" onclick=\"deleteMonsterEffect(0)\" value=\"削除\"><br>");
			break;
			case "2":
			$("#id_cost").after("<input type=\"button\" onclick=\"getVariableChange(0)\" value=\"追加\"><input type=\"button\" onclick=\"deleteVariableChange(0)\" value=\"削除\"><br>");
				break;
			case "9":
			$("#id_cost").after("<input type=\"button\" onclick=\"getMonsterVariableChange()\" value=\"追加\"><input type=\"button\" onclick=\"deleteVariableChange(0)\" value=\"削除\"><br>");
				break;
				}
		});
	});
	function putMonsterVariableChange(){
		var tmp = $("#monster_variable_change_place_1").val();
		var val= $("#id_cost").val();
		var tmp = $("#cost_move_place_1").val();
		var val2;
		
		if(val == ""){
			val2=[];
		}else{
			val2= JSON.parse(val);
		}
		
		json={};
		if(tmp != "0"){
			json["place"] = {};
			json["place"][0] =  tmp;
			for(var i=2;$("#monster_variable_change_move_place_add_"+(i-1)).val();i++){
				var tmp = $("#monster_variable_change_move_place_"+i).val();
				var operator = $("#monster_variable_change_move_place_add_"+(i-1)).val();
				if(tmp != "0"){
					json["place"][i-1] =  tmp;
				}
			}
		}
		var j=0;
		json["monster_variable_change_name"] = {}
		if($("#get_monster_name_equal").val() == ""){
			json["monster_variable_change_name"]["monster_name_kind"] = "";
		}else if($("#get_monster_name_equal").val() == "="){
			json["monster_variable_change_name"]["monster_name_kind"] = {};
			json["monster_variable_change_name"]["monster_name_kind"]["operator"] = "=";
			json["monster_variable_change_name"]["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}else{
			json["monster_variable_change_name"]["monster_name_kind"] = {};
			json["monster_variable_change_name"]["monster_name_kind"]["operator"] = "like";
			json["monster_variable_change_name"]["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}
		if($("#flag_equal").val() == ""){
			json["flag"] = "";
		}else{
			json["flag"] = {};
			json["flag"]["operator"] = "=";
			json["flag"]["flag_det"] =$("#flag").val();
		}
		json["monster_variable_change_move"] = [];
		for(var i=1;$("#get_monster_variable_"+i).length != 0;i++){
			if($("#get_monster_variable_equal_"+i).length != 0){
				num = $("#get_monster_variable_"+i).val();
				operator = $("#get_monster_variable_equal_"+i).val();
				if(operator == ""){
					continue;
				}
				json["monster_variable_change_move"][i-1] = {};
				json["monster_variable_change_move"][i-1]["num"] = num;
				json["monster_variable_change_move"][i-1]["operator"] = operator;
					
				j++;
			}else{
				num = $("#get_monster_variable_"+i).val();
				if(num == "0" || num == ""){
					continue;
				}
				json["monster_variable_change_move"][i-1] = {};
				json["monster_variable_change_move"][i-1]["num"] = num;
				json["monster_variable_change_move"][i-1]["operator"] = "";
			}
			
		}
		json["equation"] = $("#get_equation_det").val();
		json["equation_kind"] = $("#get_equation_kind").val();
		json["min_equation_number"] = $("#min_equation_number").val();
		json["max_equation_number"] = $("#max_equation_number").val();
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
		if($("#flag_equal").val() == ""){
			json["flag"] = "";
		}else{
			json["flag"] = {};
			json["flag"]["operator"] = "=";
			json["flag"]["flag_det"] =$("#flag").val();
		}
		json["monster_name_det"] = $("#monster_name_det").val();
		json["exclude"] = $("#exclude").val();
		json["monster_variable_name"] = $("#monster_variable_name").val();
		json["monster_variable_who"] = parseInt($("#monster_variable_who").val());
		json["monster_variable_change_how"] = parseInt($("#monster_variable_change_how").val());
		json["monster_variable_change_val"] = parseInt($("#monster_variable_change_val").val());
		json["monster_variable_change_name"] = $("#monster_variable_change_name").val();
		json["monster_variable_as"] = $("#as_cost_variable_from").val();
		val2.push(json)
		val = JSON.stringify(val2);
		$("#id_cost").val(val);
		$("#monster_variable_change").hide();
		
	}
	function putVariableChange(){
		var val =  {};
		val["variable_name"] = $("#variable_name").val();
		val["variable_who"] = parseInt($("#variable_who").val());
		val["variable_change_how"] = parseInt($("#variable_change_how").val());
		val["variable_change_val"] = parseInt($("#variable_change_val").val());
		$("#id_cost").val(JSON.stringify(val));
		$("#variable_change").hide();
		
	}
	function getMonsterEffectMovePhase(i){
		$("#cost_phase_move").show();
		$("#cost_phase_move").draggable();
		$("#cost_phase_move").offset({top:0,left:200});
		getMonsterEffectPhase(i);
	}
	function getMonsterEffectChangeTurn(i){
		$("#cost_change_turn").show();
		$("#cost_change_turn").draggable();
		$("#cost_change_turn").offset({top:0,left:200});
	}
	function getVariableChange(i){
		$("#variable_change").show();
		$("#variable_change").draggable();
		$("#variable_change").offset({top:0,left:200});
		getMonsterEffectVariable(i);
	}
	function deleteVariableChange(){
		$("#id_cost").val("");
	}
	function getMonsterEffectMove(i){
		getConditionKind("cost",0,100,0);
	}
	
	function deleteMonsterEffect(i){
		$("#id_cost").val("");
	}
	function deleteMonsterChange(i){
		for(var i=0;i<current_i;i++){
			$("#monster_kind-"+i).remove()
		}
		$("#id_cost_move_kinds").val("");
		current_i=0;
	}
	function changeEffectMoveNum(){
		var tmp_str = "";
		for(var i=0;i<current_i;i++){
			tmp_str+=$("#monster_kind-"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_cost_move_kinds").val(tmp_str);

	}
	function getMonsterEffectMoveKindPlace(num){
		$("#cost_move").show();
		$("#cost_move").offset({top:0,left:200});
		$("#monster_cost_move").hide();
		$("#monster_cost_move_how_main").hide();
		$("#monster_equation").hide();
		$("#monster_cost_move_to").hide();
		$("#monster_cost_move_how_main_to").hide();
		$("#monster_equation_to").hide();
	}
	function getMonsterEffectMoveKind(num){
		$("#cost_move").show();
		$("#cost_move").offset({top:0,left:200});
		$("#monster_cost_move").hide();
		$("#monster_cost_move_how_main").hide();
		$("#monster_equation").hide();
	}
	function getMonsterEffectVariable(){
			$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_variable_kind/",
		   'data': "",
			'success': function(data){
				$("#variable_name").html(data);
			}
		});
	}
	function getMonsterEffectPhase(){
			$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_phase/",
		   'data': "",
			'success': function(data){
				$("#monster_change_phase").html(data);
			}
		});
	}
	function getWhetherIsField(val){
		var tmp = val.split("_");
		if(tmp[0] == "field"){
			$("#field_whether_monster_exists").show();
			$("#field_x").show();
			$("#field_y").show();
		}else{
			$("#field_x").hide();
			$("#field_y").hide();
			$("#field_whether_monster_exists").hide();
		}
	}
	function getWhetherIsFieldTo(val){
		var tmp = val.split("_");
		if(tmp[0] == "field"){
			$("#field_to").show();
			$("#field_x_to").show();
			$("#field_y_to").show();
		}else{
			$("#field_to").hide();
			$("#field_x_to").hide();
			$("#field_y_to").hide();
		}
	}
	function getMonsterEffectMoveKind2(num){
		if(num == 0){
			$("#as_monster_from").show();
			$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_place_kind/",
		   'data': "",
			'success': function(data){
				$(".cost_move_place").show();
				$("#cost_move_place_1").html(data);
				$.ajax({
					   'type': "POST",
					   'url': "/tcgcreator/get_monster/",
					   'data': "",
					'success': function(data){
							$("#monster_cost_move").show();
							$("#monster_cost_how_main").show();
							$("#monster_cost_move").html(data);
							$.ajax({
					  			 'type': "POST",
					  			 'url': "/tcgcreator/get_equation/",
					  			 'data': "num=0",
								'success': function(data){
									$("#monster_equation").show();
									$("#monster_equation").html(data);
					      		 } 
							})
					        } 
						})
		        } 
			})
		}else if(num==1){
			$("#as_monster_to").show();
			$("#as_monster_from").show();
			$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_place_kind/",
		   'data': "",
			'success': function(data){
				$(".cost_move_place").show();
				$("#cost_move_place_1").html(data);
				$("#cost_move_place_1_to").html(data);
				$.ajax({
					   'type': "POST",
					   'url': "/tcgcreator/get_monster/",
					   'data': "",
					'success': function(data){
							$("#monster_cost_move").show();
							$("#monster_cost_how_main").show();
							$("#monster_cost_move").html(data);
							$.ajax({
					  			 'type': "POST",
					  			 'url': "/tcgcreator/get_equation/",
					  			 'data': "",
								'success': function(data){
									$("#monster_equation").show();
									$("#monster_equation").html(data);
					      		 } 
							})
					        } 
				})
		        } 
			})
		}
	}	
	function addMonsterEffectName(i){
		var html = '<input type="text" id="monster_name_det_'+(i+1)+'">';
		html+='<select id="monster_name_add_'+(i+1)+'" onchange="addMonsterEffectName('+(i+1)+')" class="cost_move_place" style="display:none"><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		$("#monster_name_add_"+i).after(html);
	}
	function addMonsterEffectMovePlaceTo(i){
		var html= $("#cost_move_place_1_to").html();
		var html = '<select id="cost_move_place_'+(i+1)+'_to" class="cost_move_place" >'+html+'</select>';
		html+='<select id="cost_move_place_add_1_to" onchange="addMonsterEffectMovePlaceTo('+(i+1)+')" class="cost_move_place" style="display:none"><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		$("#cost_move_place_add_"+i+"_to").after(html);
	}
	function addMonsterEffectMovePlace(i){
		var html= $("#cost_move_place_1").html();
		var html = '<select id="cost_move_place_'+(i+1)+'" class="cost_move_place" >'+html+'</select>';
		html+='<select id="cost_move_place_add_1" onchange="addMonsterEffectMovePlace('+(i+1)+')" class="cost_move_place" style="display:none"><option value=""></option><option value="and">かつ</option><option value="or">または</option></select>';
		$("#cost_move_place_add_"+i).after(html);
	}
	function putMonsterEffectTimingToVariable(){
		var val =  {};
		val["org_val"] = $("#timing_variable_org_monster").val();
		val["val"] = $("#timing_variable_monster").val();
		$("#id_cost").val(JSON.stringify(val));
		$("#monster_effect_timing_variable").hide();

	}
	function putMonsterEffectChangeTurn(){
		var val =  {};
		val["change_turn"] = 1;
		$("#id_cost").val(JSON.stringify(val));
		$("#cost_change_turn").hide();
		
	}
	function putMonsterEffectMovePhase(){
		var val =  {};
		val["move_to_phase"] = parseInt($("#monster_change_phase").val());
		$("#id_cost").val(JSON.stringify(val));
		$("#cost_phase_move").hide();
		
	}
	function putMonsterEffectMove(){
		var val= $("#id_cost").val();
		var tmp = $("#cost_move_place_1").val();
		var val2;
		
		if(val == ""){
			val2=[];
		}else{
			val2= JSON.parse(val);
		}
		json={};
		if(tmp != "0"){
			json["place"] = {};
			json["place"][0] =  tmp;
			for(var i=2;$("#cost_move_place_add_"+(i-1)).val();i++){
				var tmp = $("#cost_move_place_"+i).val();
				var operator = $("#cost_move_place_add_"+(i-1)).val();
				if(tmp != "0"){
					json["place"][i-1] =  tmp;
				}
			}
		}
		var j=0;
		json["cost_name"] = {}
		if($("#get_monster_name_equal").val() == ""){
			json["cost_name"]["monster_name_kind"] = "";
		}else if($("#get_monster_name_equal").val() == "="){
			json["cost_name"]["monster_name_kind"] = {};
			json["cost_name"]["monster_name_kind"]["operator"] = "=";
			json["cost_name"]["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}else{
			json["cost_name"]["monster_name_kind"] = {};
			json["cost_name"]["monster_name_kind"]["operator"] = "like";
			json["cost_name"]["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}
		if($("#flag_equal").val() == ""){
			json["flag"] = "";
		}else{
			json["flag"] = {};
			json["flag"]["operator"] = "=";
			json["flag"]["flag_det"] =$("#flag").val();
		}
		json["cost_move"] = [];
		for(var i=1;$("#get_monster_variable_"+i).length != 0;i++){
			if($("#get_monster_variable_equal_"+i).length != 0){
				num = $("#get_monster_variable_"+i).val();
				operator = $("#get_monster_variable_equal_"+i).val();
				if(operator == ""){
					continue;
				}
				json["cost_move"][i-1] = {};
				json["cost_move"][i-1]["num"] = num;
				json["cost_move"][i-1]["operator"] = operator;
					
				j++;
			}else{
				num = $("#get_monster_variable_"+i).val();
				if(num == "0" || num == ""){
					continue;
				}
				json["cost_move"][i-1] = {};
				json["cost_move"][i-1]["num"] = num;
				json["cost_move"][i-1]["operator"] = "";
			}
			
		}
		json["equation"] = $("#get_equation_det").val();
		json["equation_kind"] = $("#get_equation_kind").val();
		json["min_equation_number"] = $("#min_equation_number").val();
		json["max_equation_number"] = $("#max_equation_number").val();
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
		if($("#flag_equal").val() == ""){
			json["flag"] = "";
		}else{
			json["flag"] = {};
			json["flag"]["operator"] = "=";
			json["flag"]["flag_det"] =$("#flag").val();
		}
		json["variables"] = [];
		for(var i=1;$("#get_monster_variable_"+i).length != 0;i++){
			if($("#get_monster_variable_equal_"+i).length != 0){
				num = $("#get_monster_variable_"+i).val();
				operator = $("#get_monster_variable_equal_"+i).val();
				if(operator == ""){
					continue;
				}
				json["variables"][i-1] = {};
				json["variables"][i-1]["num"] = num;
				json["variables"][i-1]["operator"] = operator;
					
				j++;
			}else{
				num = $("#get_monster_variable_"+i).val();
				if(num == "0" || num == ""){
					continue;
				}
				json["variables"][i-1] = {};
				json["variables"][i-1]["num"] = num;
				json["variables"][i-1]["operator"] = "";
			}
			
		}
		json["monster_name_det"] = $("#monster_name_det").val();
		json["move_how"] = $("#cost_move_how").val();
		json["who_choose"] = $("#cost_who").val();
		json["as_cost_from"] = $("#as_cost_from").val();
		json["whether_monster"] = $("#monster_exist").prop("checked")?1:0;
		if($("#field_x").val() != ""){
			json["field_x"] = $("#field_x").val();
		}
		if($("#field_y").val() != ""){
			json["field_y"] = $("#field_y").val();
		}
		if($("#field_x_to").val() != ""){
			json["field_x_to"] = $("#field_x_to").val();
		}
		if($("#field_y_to").val() != ""){
			json["field_y_to"] = $("#field_y_to").val();
		}
		json["sentence"] = $("#monster_sentence").val();
		json["exclude"] = $("#exclude").val();

		if($("#id_cost_val").val() == 1){
		var j=0;
		var tmp = $("#cost_move_place_1_to").val();
		if(tmp != ""){
			json["place_to"] = {};
			json["place_to"][0] =  tmp;
			for(var i=2;$("#cost_move_place_add_"+(i-1)+"_to").val();i++){
				var tmp = $("#cost_move_place_"+i+"_to").val();
				var operator = $("#cost_move_place_add_"+(i-1)+"_to").val();
				if(tmp != "0"){
					json["place_to"][i-1] =  tmp;
				}
			}
		}
		json["move_how_to"] = $("#cost_move_how_to").val();
		json["as_cost_to"] = $("#as_cost_to").val();

		}
		val2.push(json)
		val = JSON.stringify(val2);
		$("#id_cost").val(val);
		$("#cost_move").hide();
		$("#monster_monster").hide();
		$("#monster_equation").hide();
		$(".cost_move_place").hide();
		for(var i=2;$("#cost_move_place_"+(i)).length;i++){
			$("#cost_move_place_"+i).remove();
			$("#cost_move_place_add"+i).remove();
			
		}
		
		
	}
	function  hideAllWindow(){
		$("#monster_effect_phase_move").hide();
		$("#monster_effect_change_turn").hide();
		$("#variable_change").hide();
		$("#monster_variable_change").hide();
		$("#monster_effect_move").hide();
	}
	function getCostCondition(){
		$("#cost_condition").show();
		$("#cost_condition").draggable();
		getCostConditionKind(-1);
	}
	function getCostConditionKind(cost_kind){
		if(cost_kind == "0" || cost_kind == "1"){
			$("#monster_condition_place_tab").show();
		}else{
			$("#monster_condition_place_tab").hide();
		}
		if(cost_kind == "2"){
			$("#variable_condition_tab").show();
			getCostConditionVariables();
		}else{
			$("#variable_condition_tab").hide();
		}
		$("#cost_condition").show();
		$("#cost_condition").offset({top:0,left:200});
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "",
'success': function(data){
		$(".monster_condition_place").show();
		$("#monster_condition_place_1").html(data);
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster/",
			   'data': "",
			'success': function(data){
					$("#monster_monster").show();
					$("#monster_monster").html(data);
					$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_equation/",
			  			 'data': "num=1",
						'success': function(data){
							$(".monster_equation").show();
							$("#monster_equation_1").html(data);
			      		 } 
					})
			        } 
				})
        } 
	})
	}	
	function getMonsterConditionVariables(){
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
	function putCostCondition(){
		var val= $("#id_cost_condition").val();
		if(val == ""){
			val = [];
		}else{
			val = JSON.parse(val);
		}
			
		var tmp = $("#monster_condition_place_1").val();
		var tmp2 = $("#variable_condition_1").val();
		var json = {};
		
		if(tmp2 != "0" && tmp2!="" && tmp2!=null){
			json["variable"] = {};
			json["variable_equation"] = {};
			json["variable_equation_val"] = {};
			json["variable"][0] = tmp2;
			json["variable_equation"][0] =$("#variable_condition_equation_1").val();;
			json["variable_equation_val"][0] =$("#variable_equation_val_1").val();;
			for(var i=2;$("#variable_condition_add_"+(i-1)).val();i++){
				var tmp = $("#variable_condition_"+i).val();
				var operator = $("#variable_condition_equation_"+(i-1)).val();
				var variable_val = $("#variable_equation_val_"+(i-1)).val();;
				if(tmp != "0"){
					json["varaiable"][i-1] =  tmp;
					json["varaiable_equation"][i-1] =  operator;
				}
			}
		}
			json["place"] = {};
			json["place"][0] =  tmp;
			json["equation"] = [];
			json["equation"][0] = {};
			json["equation"][0]["equation"] = $("#get_equation_det").val();
			json["equation"][0]["equation_kind"] = $("#get_equation_kind").val();
			json["equation"][0]["equation_number"] = $("#get_equation_number").val();
			for(var i=2;$("#monster_condition_place_add_"+(i-1)).val();i++){
				var tmp = $("#monster_condition_place_"+i).val();
				var operator = $("#monster_condition_place_add_"+(i-1)).val();
				if(tmp != "0"){
					json["place"][i-1] =  tmp;
				}
				json["equation"][i-1] = {};
				
				json["equation"][i-1]["equation"] = $("#get_equation_det_"+i).val();
				json["equation"][i-1]["equation_kind"] = $("#get_equation_kind"+i).val();
				json["equation"][i-1]["equation_number"] = $("#get_equation_number"+i).val();
			}
		json["monster_name_condition"] = {}
		if($("#get_monster_name_equal").val() == ""){
			json["monster_name_condition"]["monster_name_kind"] = "";
		}else if($("#get_monster_name_equal").val() == "="){
			json["monster_name_condition"]["monster_name_kind"] = {};
			json["monster_name_condition"]["monster_name_kind"]["operator"] = "=";
			json["monster_name_condition"]["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}else{
			json["monster_name_condition"]["monster_name_kind"] = {};
			json["monster_name_condition"]["monster_name_kind"]["operator"] = "like";
			json["monster_name_condition"]["monster_name_kind"]["monster_name"] =$("#monster_name").val();
		}
		if($("#flag_equal").val() == ""){
			json["flag"] = "";
		}else{
			json["flag"] = {};
			json["flag"]["operator"] = "=";
			json["flag"]["flag_det"] =$("#flag").val();
		}
		json["monster_condition"] = [];
		for(var i=1;$("#get_monster_variable_"+i).length != 0;i++){
			json["monster_condition"][i-1] = {};
			if($("#get_monster_variable_equal_"+i).length != 0){
				num = $("#get_monster_variable_"+i).val();
				operator = $("#get_monster_variable_equal_"+i).val();
				if(operator == ""){
					continue;
				}
				json["monster_condition"][i-1]["num"] = num;
				json["monster_condition"][i-1]["operator"] = operator;
					
			}else{
				num = $("#get_monster_variable_"+i).val();
				if(num == "0" || num == ""){
					continue;
				}
				json["monster_condition"][i-1]["num"] = num;
				json["monster_condition"][i-1]["operator"] = "";
			}
			
		}
		var j=0;
		if($("#as_cost_condition").val() != ""){
			json["as_monster_condition"] = $("#as_cost_condition").val();
		}	
		json["min_equation_number"] = $("#min_equation_number").val();
		json["max_equation_number"] = $("#max_equation_number").val();
		val.push(json);
		val =  JSON.stringify(val);
		$("#id_cost_condition").val(val);
		$("#cost_condition").hide();
		$("#monster_monster").hide();
		$("#monster_equation").hide();
		$(".monster_condition_place").hide();
		for(var i=2;$("#monster_condition_place_"+(i)).length;i++){
			$("#monster_condition_place_"+i).remove();
			$("#monster_condition_place_add"+i).remove();
			
		}
		
		
	}
