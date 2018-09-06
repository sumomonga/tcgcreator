
	function displayMove(id,i,j){
		var k;
		for(k=1;$("#"+id+"_"+i+"_"+k).length != 0;k++){
			$("#"+id+"_"+i+"_"+k).hide();
			$("#"+id+"_button_"+i+"_"+k).removeClass("active");
		}
			$("#"+id+"_button_"+i+"_"+j).addClass("active");
		$("#"+id+"_"+i+"_"+j).show();
	}
	function displayMoveAll(id,i){
		var k;
		for(k=0;$("#choose_"+id+"_"+k).length != 0;k++){
			$("#as_"+id+"_wrapper_"+k).hide();
			$("#choose_"+id+"_"+k).hide();
			$("#choose_"+id+"_"+k).removeClass("active");
		}
		$("#choose_"+id+"_"+i).addClass("active");
		$("#choose_"+id+"_"+i).show();
		$("#as_"+id+"_wrapper_"+i).show();
	}
	function addMovePlace(id,i,j){
		if(!(i==0 && j==1)){
			$("#"+id+"_add_button_"+i+"_"+j).remove();
		}else{
			$("#"+id+"_add_button_"+i+"_"+j).hide();
		}
	j++;
	
	$("#"+id+"_button_"+i+"_"+(j-1)).after('<input type="button" value="条件'+j+'" onclick="displayMove(\''+id+'\','+i+','+j+')" id="'+id+'_button_'+i+'_'+j+'"><input type="button" value="追加" id="'+id+'_add_button_'+i+'_'+j+'" onclick="addMovePlace(\''+id+'\','+i+','+j+')">');
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster_condition/",
			   'data': "i="+i+"&j="+j,
			'success': function(data){
		$("#"+id+"_"+i+"_"+(j-1)).after('<div id="'+id+'_'+i+'_'+j+'"><div id="monster_monster_'+i+'_'+j+'" style=""></div> </div> <div id="monster_equation_'+i+'_'+j+'" class="monster_equation" style=""></div> </div> </div>');
					$("#monster_monster_"+i+"_"+j).show();
					$("#monster_monster_"+i+"_"+j).html(data);
					displayMove(id,i,j);
			        } 
		})
		}
		
	function getMoveKind(id,kind,y,x){
		if(kind == undefined){
			kind =-1;
		}
		$("#"+id).show();
		$("#"+id).draggable();
		$("#"+id).offset({top:x,left:y});
		$("#"+id+"_0_1").show();
		if(kind == "0" || kind == "1"){
			$("#"+id+"_place_tab").show();
		}else{
			$("#"+id+"_place_tab").hide();
		}
		if(kind == "2"){
			$("#"+id+"_variable_condition_tab").show();
			getMoveVariables();
		}else{
			$("#"+id+"_variable_condition_tab").hide();
		}
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
			   'url': "/tcgcreator/get_monster_condition/",
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
					$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_field_x_and_y/",
			  			 'data': "c=0",
						'success': function(data){
							$("."+id+"_field_x_and_y_0").show();
							$("#"+id+"_field_x_and_y_0").html(data);
			      		 } 
					})
			        } 
				})
		}
	})
	}else{
		getMoveKindWithData(id);
	}
	}	
	function getMoveKindWithData(id){
		val = $("#id_"+id).val();
		val = JSON.parse(val);
		for(var c = 0;c<val.length;c++){
		equ = val[c]["equation"];
		field_x_and_y = val[c]["field_x_and_y"];
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
			   'url': "/tcgcreator/get_monster_condition/",
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
						 })(i,c);
						(function(i,c){
						$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_field_x_and_y/",
			  			 'data': "c="+c,
						'success': function(data){
							var j;
							$("#"+id+"_field_x_and_y_"+c).html(data);
							for(j=0;j<field_x_and_y["x"].length;j++){
								$("#field_x_"+c+"_"+j).val(field_x_and_y["x"][j]);
							}
							for(j=0;j<field_x_and_y["y"].length;j++){
								$("#field_y_"+c+"_"+j).val(field_x_and_y["y"][j]);
							}
							
			      		 	} 
						})
						})(i,c);
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
	function putMove(id,mode = 0){
			val = {};
			val["monster"] = []
		var k=0;
			
		var tmp = [];
		var json = {};
		
		var place;
		if(mode == 1){
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
			tmp["as_monster_condition"] = $("#as_"+id+"_"+m).val();
		}
		tmp["min_equation_number"] = $("#min_equation_number_"+m).val();
		tmp["max_equation_number"] = $("#max_equation_number_"+m).val();
		tmp["equation"] = {};
		tmp["equation"]["equation"] = $("#get_equation_det_"+m).val();
		tmp["equation"]["equation_kind"] = $("#get_equation_kind_"+m).val();
		tmp["equation"]["equation_number"] = $("#get_equation_number_"+m).val();
		val["field_x"] = [];
		for(var field_x=0;$("#"+id+"_field_x_"+m+"_"+field_x).val() != "";field_x++){
			val["field_x"][j] = $("#"+id+"_field_x").val();
		}
		for(var field_y=0;$("#"+id+"_field_y_"+m+"_"+field_y).val() != "";field_y++){
			val["field_y"][j] = $("#"+id+"_field_y").val();
		}
		val["monster"].push(tmp);
		}
		
		if(mode==2){
			val["move_how"] = $("#"+id+"_move_how").val();;
			val["monster_exist"] = $("#"+id+"_monster_exist").val();
		}
		if($("#exclude_"+id).val() != ""){
			val["exclude"] = $("#exclude_"+id).val();
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
	function addMovePlaceAll(id,i){
		if(!(i==0 )){
			$("#"+id+"_all_add_button_"+i).remove();
		}else{
			$("#"+id+"_all_add_button_"+i).hide();
		}
	var j=i+1;
	$("#choose_"+id+"_"+i).after('<div id="choose_'+id+'_'+j+'"> <input type="button" class="active" value="条件1" onclick="displayMove(\''+id+'\','+j+',1)" id="'+id+'_button_'+j+'_1"><input type="button" value="追加" id="'+id+'_add_button_'+j+'_1" onclick="addMovePlace(\''+id+'\','+j+',1)"><br><select id="'+id+'_place_'+j+'_0" class="'+id+'_place" style=""> </select> <select id="'+id+'_place_add_'+j+'_0" onchange="addPlace(\''+id+'_place\','+j+',1)" class="'+id+'_place" style=""> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select> <div id="'+id+'_'+j+'_1"> </div> <div id="'+id+"_field_x_and_y_"+j+'"></div><div id="'+id+'_equation_'+j+'" class="'+id+'_equation" style=""></div> </div> </div><div id="as_'+id+'_wrapper_'+j+'">as <input type="text" id="as_'+id+'_'+j+'"></div> </div > </div></div>');
	$("#"+id+"_all_button_"+i).after('<input type="button" value="'+(j+1)+'" onclick="displayMoveAll(\''+id+'\','+j+')" id="'+id+'_all_button_'+j+'"><input id="trigger_condition_all_add_button_'+j+'" type="button" value="追加" onclick="addMovePlaceAll(\''+id+'\','+j+')">');
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "i="+j,
'success': function(data){
		$("."+id+"_place").show();
		$("#"+id+"_place_"+j+"_0").html(data);
		$.ajax({
			   'type': "POST",
			   'url': "/tcgcreator/get_monster_condition/",
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
							displayMoveAll(id,j);
			      		 } 
					})
					$.ajax({
			  			 'type': "POST",
			  			 'url': "/tcgcreator/get_field_x_and_y/",
			  			 'data': "c="+j,
						'success': function(data){
							$("."+id+"_field_x_and_y").show();
							$("#"+id+"_field_x_and_y_"+j).html(data);
			      		 } 
					})
			        } 
		})
	}});
		
	}
