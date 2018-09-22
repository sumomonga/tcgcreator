
	function addTriggerMonsterConditionPlace(id){
	
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster_trigger_condition/",
			   'data': "",
			'success': function(data){
		$("#"+id).after('<div id="'+id+'"><div id="monster_monster" style=""></div> </div> <div id="monster_equation" class="monster_equation" style=""></div> </div> </div>');
					$("#monster_monster").show();
					$("#monster_monster").html(data);
					displayTriggerMonsterCondition(id);
			        } 
		})
		}
		
	function getTriggerMonsterKind(id,kind){
		if(kind == undefined){
			kind =-1;
		}
		$("#"+id).show();
		$("#"+id).draggable();
		$("#"+id+"_0_1").show();
			$("#"+id+"_place_tab").show();
	if($("#id_"+id).val() == ""){
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "i=1",
'success': function(data){
		$("."+id+"_place").show();
		$("#"+id+"_place_0_0").html(data);
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster/",
			   'data': "i=1&j=0",
			'success': function(data){
					$("#"+id+"_0_1").html("<div id=\"monster_monster_0_1\"></div>");
					
					$("#monster_monster_0_1").html(data);
					$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_equation/",
			  			 'data': "c=0",
						'success': function(data){
							$("."+id+"_equation").show();
							$("#"+id+"_equation_0").html(data);
			      		 } 
					})
			        } 
				})
		}
	})
	}else{
		getConditionKindWithData(id);
	}
	}	
	function getConditionKindWithData(id){
		val = $("#id_"+id).val();
		val = JSON.parse(val);
		for(var c = 0;c<val.length;c++){
		equ = val[c]["equation"];
		val2 = val[c];
		monster = val[c]["monster"];
	for(i=1;i<=monster.length;i++){
               (function(i,c){
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "i="+i,
'success': function(data){
		var l;
		$(".monster_condition_place").show();
		for(l=0;l<monster[i-1]["place"].length;l++){
		$("#monster_condition_place_"+i+"_"+l).html(data);
		if($("#monster_condition_place_"+i+"_"+l).length==0){
			addPlace("monster_condition_place",i,l);
		}
		$("#monster_condition_place_"+i+"_"+l).monster( val[i-1]["place"][l]["det"]);
		$("#monster_condition_place_add_"+i+"_"+l).monster(val[i-1]["place"][l]["and_or"]);
		}
               (function(i,c){
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster/",
   				'data': "i="+i+"&j="+c,
			'success': function(data){
					$("#monster_monster_"+i).show();
					$("#monster_monster_"+i).html(data);
					$("#flag_equal_"+i).val(monster[i-1]["flag"]["operator"]);
					$("#get_monster_name_equal_"+i).val(monster[i-1]["monster_name_kind"]["operator"]);
					$("#get_monster_name_"+i).val(monster[i-1]["monster_name_kind"]["monster_name"]);
					for(j=1;j<=monster[i-1]["monster_condition"].length;j++){
						for(var k=0;k<=monster[i-1]["monster_condition"][j-1].length;k++){
							if(monster[i-1]["monster_condition"][j-1][k] == undefined){
								continue;
							}
							if(k!=0){
								addMonsterEquation(i+"_"+j+"_"+(k-1));
							}
							$("#get_monster_variable_equal_"+i+"_"+j+"_"+k).val(monster[i-1]["monster_condition"][j-1][k]["operator"]);
							$("#get_monster_variable_"+i+"_"+j+"_"+k).val(monster[i-1]["monster_condition"][j-1][k]["num"]);
							$("#monster_variable_and_or_"+i+"_"+j+"_"+k).val(monster[i-1]["monster_condition"][j-1][k]["and_or"]);
						}
					}
					
					if(i==1){
               			(function(i,c){
					$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_equation/",
			  			 'data': "c="+c,
						'success': function(data){
							$("."+id+"_equation").show();
							$("#"+id+"_equation_"+c).html(data);
							$("#get_equation_det_"+c).val(equ["equation"]);
							$("#get_equation_number_"+c).val(equ["equation_number"]);
							$("#get_equation_kind_"+c).val(equ["equation_kind"]);
		$("#min_equation_number_"+c).val(equ["min_equation_number"]);
		$("#max_equation_number_"+c).val(equ["max_equation_number"]);
			      		 } 
					})
				})(i,c)
					}
			        } 
				})
				})(i,c)
		}
	})
	})(i,c)
	}
	}
	}
	function putCondition(id,mode = 0){
			val = {};
			val["monster"] = []
		var k=0;
			
		var tmp = [];
		var json = {};
		
		var place;
		if(mode != 0){
			val["variable"] = []
		var tmp2 = $("#"+id+"variable_condition_1").val();
		if(tmp2 != "0" && tmp2!="" && tmp2!=null){
			json = {};
			for(var i=1;$("#"+id+"variable_condition_add_"+(i-1)).val();i++){
				tmp_json={}
				var tmp = $("#"+id+"variable_condition_"+i).val();
				var operator = $("#"+id+"variable_condition_equation_"+(i-1)).val();
				var variable_val = $("#"+id+"variable_equation_val_"+(i-1)).val();;
				if(tmp != "0"){
					tmp_json["variable"] =  tmp;
					tmp_json["varaiable_equation"] =  operator;
					val["variable"].push(tmp_json)
				}
			}
		}
		}
		var l;
		json = {};
		for(m=0;$("#"+id+"_place_"+m+"_"+0).val();m++){
		var tmp = {};
		place = [];
		for(l=0;$("#"+id+"_place_"+m+"_"+l).val();l++){
		place[l] = {};
		var and_or = $("#"+id+"_place_add_"+m+"_"+l).val();
		place[l]["and_or"] = and_or;
			var tmp_place = $("#"+id+"_place_"+m+"_"+l).val();
			if(tmp_place != "0"){
				place[l]["det"] =  tmp_place;
			}
		}
		json = {};
		for(var i=1;$("#get_monster_name_equal_"+m+"_"+i+"_0").length;i++){
			json["place"] = place;
		json["monster_name_kind"] = [];
		for(var j=0;$("#get_monster_name_equal_"+m+"_"+i+"_"+j).length;j++){
		if($("#get_monster_name_equal_"+m+"_"+i+"_"+j).val() == ""){
			json["monster_name_kind"][j] = {};
			json["monster_name_kind"][j]["operator"] = "";
			json["monster_name_kind"][j]["monster_name"] ="";
		}else if($("#get_monster_name_equal_"+m+"_"+i+"_"+j).val() == "="){
			json["monster_name_kind"][j] = {};
			json["monster_name_kind"][j]["operator"] = "=";
			json["monster_name_kind"][j]["monster_name"] =$("#monster_name_"+m+"_"+i+"_"+j).val();
			json["monster_name_kind"][j]["and_or"] =$("#monster_name_and_or_"+m+"_"+i+"_"+j).val();
		}else{
			json["monster_name_kind"][j] = {};
			json["monster_name_kind"][j]["operator"] = "like";
			json["monster_name_kind"][j]["and_or"] =$("#monster_name_and_or_"+m+"_"+i+"_"+j).val();
			json["monster_name_kind"][j]["monster_name"] =$("#monster_name_"+m+"_"+i+"_"+j).val();
		}
		}
		if($("#flag_equal_"+m+"_"+i).val() == ""){
			json["flag"] = "";
		}else{
			json["flag"] = {};
			json["flag"]["operator"] = "=";
			json["flag"]["flag_det"] =$("#flag_"+m+"_"+i).val();
		}
		json["monster_condition"] = [];
		for(var j=1;$("#get_monster_variable_"+m+"_"+i+"_"+j+"_0").length != 0;j++){
			json["monster_condition"][j-1] = [];
			for(k=0;$("#get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).length != 0;k++){
			json["monster_condition"][j-1][k] = {};
			if($("#get_monster_variable_equal_"+m+"_"+i+"_"+j+"_"+k).length != 0){
				num = $("#get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).val();
				operator = $("#get_monster_variable_equal_"+m+"_"+i+"_"+j+"_"+k).val();
				and_or = $("#monster_variable_and_or_"+m+"_"+i+"_"+j+"_"+k).val();
				if(operator == ""){
					continue;
				}
				json["monster_condition"][j-1][k]["num"] = num;
				json["monster_condition"][j-1][k]["operator"] = operator;
				json["monster_condition"][j-1][k]["and_or"] = and_or;
					
			}else{
				num = $("#get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).val();
				and_or = $("#monster_variable_and_or_"+m+"_"+i+"_"+j+"_"+k).val();
				if(num == "" || num==0){
					continue;
				}
				json["monster_condition"][j-1][k]["num"] = num;
				json["monster_condition"][j-1][k]["operator"] = "";
				json["monster_condition"][j-1][k]["and_or"] = and_or;
			}
			}
			
		}
		tmp["monster"]=json;
		}
		if($("#as_"+id+"_"+m).val() != ""){
			tmp["as_monster_condition"] = $("#as_monster_effect_condition").val();
		}
		tmp["min_equation_number"] = $("#min_equation_number_"+m).val();
		tmp["max_equation_number"] = $("#max_equation_number_"+m).val();
		tmp["equation"] = {};
		tmp["equation"]["equation"] = $("#get_equation_det_"+m).val();
		tmp["equation"]["equation_kind"] = $("#get_equation_kind_"+m).val();
		tmp["equation"]["equation_number"] = $("#get_equation_number_"+m).val();
		val["monster"].push(tmp);
		}
		var j=0;
		val =  JSON.stringify(val);
		$("#id_"+id).val(val);
		$("#"+id).hide();
		for(var i=2;$("#"+id+"_place_"+(i)).length;i++){
			$("#"+id+"_place_"+i).remove();
			$("#"+id+"_place_add"+i).remove();
			
		}
		
		
	}
	function getConditionVariables(id){
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_variable_kind/",
		   'data': "",
		'success': function(data){
			$("."+id+"_variable_condition_").show();
			$("#"+id+"_variable_condition_1").html(data);
		}
		});
	}
	function addConditionPlaceAll(id,i){
		if(!(i==0 )){
			$("#"+id+"_all_add_button_"+i).remove();
		}else{
			$("#"+id+"_all_add_button_"+i).hide();
		}
	var j=i+1;
	$("#choose_"+id+"_"+i).after('<div id="choose_'+id+'_'+j+'"> <input type="button" class="active" value="条件1" onclick="displayCondition(\''+id+'\','+j+',1)" id="'+id+'_button_'+j+'_1"><input type="button" value="追加" id="'+id+'_add_button_'+j+'_1" onclick="addConditionPlace(\''+id+'\','+j+',1)"><br><select id="'+id+'_place_'+j+'_0" class="'+id+'_place" style=""> </select> <select id="'+id+'_place_add_'+j+'_0" onchange="addPlace(\''+id+'_place\','+j+',1)" class="'+id+'_place" style=""> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select> <div id="'+id+'_'+j+'_1"> </div> <div id="'+id+'_equation_'+j+'" class="'+id+'_equation" style=""></div> </div> </div><div>as <input type="text" id="as_'+id+'_'+j+'"></div> </div > </div></div>');
	$("#"+id+"_all_button_"+i).after('<input type="button" value="'+(j+1)+'" onclick="displayConditionAll(\''+id+'\','+j+')" id="'+id+'_all_button_'+j+'"><input id="trigger_condition_all_add_button_'+j+'" type="button" value="追加" onclick="addConditionPlaceAll(\''+id+'\','+j+')">');
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "i="+j,
'success': function(data){
		$("."+id+"_place").show();
		$("#"+id+"_place_"+j+"_0").html(data);
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster/",
			   'data': "i=1&j="+j,
			'success': function(data){
					$("#"+id+"_"+j+"_1").html("<div id=\"monster_monster_"+j+"_1\"></div>");
					
					$("#monster_monster_"+j+"_1").html(data);
					$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_equation/",
			  			 'data': "c="+j,
						'success': function(data){
							$("."+id+"_equation").show();
							$("#"+id+"_equation_"+j).html(data);
							displayConditionAll(id,j);
			      		 } 
					})
			        } 
		})
	}});
		
	}
