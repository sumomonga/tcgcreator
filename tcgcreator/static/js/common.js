    var initEquation = false;
	function showMonsterNameEqual(id){
		ids = id.split("_");
		if(ids.length == 3){
			if($("#get_monster_name_equal_"+ids[0]+"_"+ids[1]+"_"+ids[2]).val() == ""){
				$("#get_monster_name_equal_"+ids[0]+"_"+ids[1]+"_"+ids[2]).val("=") ;
			
			}
		}else if(ids.length == 2){
			if($("#get_monster_name_equal_"+ids[0]+"_"+ids[1]).val() == ""){
				$("#get_monster_name_equal_"+ids[0]+"_"+ids[1]).val("=") ;
			
			}
		}else if(ids.length == 1){
			if($("#get_monster_name_equal_"+ids[0]).val() == ""){
				$("#get_monster_name_equal_"+ids[0]).val("=") ;
			
			}
		}
	}
	function showMonsterEquation(id){
		monster_or_global = id;
		ids = id.split("_");
		if(ids.lenght == 7){
			if($("#get_monster_variable_equal_"+ids[3]+"_"+ids[4]+"_"+ids[5]+"_"+ids[6]).val() == ""){
				
				$("#get_monster_variable_equal_"+ids[3]+"_"+ids[4]+"_"+ids[5]+"_"+ids[6]).val("=") ;
				
			}
		}else if(ids.length== 6){
			if($("#get_monster_variable_equal_"+ids[3]+"_"+ids[4]+"_"+ids[5]).val() == ""){
				
				$("#get_monster_variable_equal_"+ids[3]+"_"+ids[4]+"_"+ids[5]).val("=") ;
				
			}
		}else if(ids.length == 5){
			if($("#get_monster_variable_equal_"+ids[3]+"_"+ids[4]).val() == ""){
				
				$("#get_monster_variable_equal_"+ids[3]+"_"+ids[4]).val("=") ;
				
			}
		}
		showEquationDet();
	}
	function addMonsterVariableChange(i){
		i++;
		$(".add_button_monster_variable_change").hide();
		var result = '変数変更名<input type="text" id="monster_variable_change_name_'+i+'"> <select id="monster_variable_change_how_'+i+'"> <option value="0">増やす</option> <option value="1">減らす</option> <option value="2">指定</option> </select> <input type="text" id="monster_variable_change_val'+i+'" onfocus="showMonsterVariableEquation('+i+')"><input type="button" onclick="addMonsterVariableChange('+i+')" class="add_button_monster_variable_change" value="追加" id="add_button_monster_variable_change_'+i+'">';
		$("#monster_variable_change").append(result);
	}
	function putGlobalVariableToEquation(){
		var editor =$("#equation_editor_det").val();
	    var val = $("#equation_editor_global_val").val();
	    val = val.split("_");
	    val = "^"+val[1]+"gt:"+val[2]+"^";
	    editor+=val;
		$("#equation_editor_det").val(editor);
	}
	function putPlaceToEquation(){
		var editor =$("#equation_editor_det").val();
		var place = $("#equation_editor_place").val();
		var tmp = "";
		place = place.split("_");
		if(place[0] == "field"){
			tmp += "|";	
			tmp += place[1]+":";
			tmp += place[2]+":";
			tmp += "|";	
		}else{
			tmp+="&";
			tmp+=place[0]+":";
			tmp+=place[1]+":";
			tmp+=place[2]+":";
			tmp += "&";	
		}
		editor += tmp;
		$("#equation_editor_det").val(editor);
	}
	function getPlaceForEquation(){
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_place_kind/",
		   'data': "",
		'success': function(data){
			$("#equation_editor_place").html(data);
		}});
	}
	function getGlobalValForEquation(){
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_variable_kind/",
		   'data': "",
		'success': function(data){
			$("#equation_editor_global_val").html(data);
		}});
	}
	function showEquationDet(){
		$("#equation_editor").show();
		$("#equation_editor").draggable();
		if(initEquation == false){
		    $("#equation_editor").offset({top:0,left:200});
		    initEquation = true;
		}
		getGlobalValForEquation();
		getPlaceForEquation();
	}
	function addCustomMonsterCondition(id){
		id = id.split("_");
		var org = id[id.length-1];
		var result="";
		if(org == 0){
		result="カスタム変数名<input type=\"text\" id=\"custom_monster_variable_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+id[3]+"\">";
		}
		result+="値<input type=\"text\" onfocus=\"showMonsterEquation('custom_get_monster_variable_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+id[3]+"')\" id=\"custom_get_monster_variable_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+id[3]+"\">";
		result+='<select id="custom_get_monster_variable_equal_'+id[0]+'_'+id[1]+'_'+id[2]+'_'+id[3]+'"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select>';
		result+='<select id="custom_monster_variable_and_or_'+id[0]+"_"+id[1]+"_"+id[2]+'_'+id[3]+'" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="custom_monster_variable_add_'+id[0]+"_"+id[1]+'_'+id[2]+'_'+id[3]+'" type="button" value="追加" onclick="addCustomMonsterCondition(\''+id[0]+'_'+id[1]+'_'+id[2]+'_'+String(parseInt(id[3])+1)+'\')">';
		if(org == 0){
			result+='<input type="button" value="カスタム追加" id="custom_add_'+id[0]+"_"+id[1]+'_'+String(parseInt(id[2])+1)+'_0" class="custom_add" onclick="addCustomMonsterCondition(\''+id[0]+"_"+id[1]+'_'+String(parseInt(id[2])+1)+'_0\')">';
			$("#custom_add_"+id[0]+"_"+id[1]+"_"+id[2]+"_0").after(result);
			$("#custom_add_"+id[0]+"_"+id[1]+"_"+id[2]+"_0").remove();
		}else{
			$("#custom_monster_variable_and_or_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+String(parseInt(id[3])-1)).after(result);
		}
	}
	function addMonsterEquation(id){
		var id = id.split("_");
		var org = id[id.length-1];
		id[id.length-1] = String(parseInt(id[id.length-1])+1);
		var result="";
		if(id.length==4){
		result+="<br><input type=\"text\" onfocus=\"showMonsterEquation('get_monster_variable_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+id[3]+"')\" id=\"get_monster_variable_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+id[3]+"\">"
		result+='<select id="get_monster_variable_equal_'+id[0]+'_'+id[1]+'_'+id[2]+"_"+id[3]+'"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select>'
		result+='<select id="monster_variable_and_or_'+id[0]+"_"+id[1]+"_"+id[2]+"_"+id[3]+'" onchange="addMonsterEquation(\''+id[0]+'_'+id[1]+'_'+id[2]+"_"+id[3]+'\')"> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_variable_add_'+id[0]+"_"+id[1]+'_'+id[2]+'_'+id[3]+'" type="button" value="追加" onclick="addMonsterEquation(\''+id[0]+'_'+id[1]+'_'+id[2]+'_'+id[3]+'\')">'
		
		$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+org).after(result);
		$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+org).hide();
		}else if (id.length==3){
		result+="<br><input type=\"text\" onfocus=\"showMonsterEquation('get_monster_variable_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+"')\" id=\"get_monster_variable_"+id[0]+"_"+id[1]+"_"+id[2]+"\">"
		result+='<select id="get_monster_variable_equal_'+id[0]+'_'+id[1]+'_'+id[2]+'"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select>'
		result+='<select id="monster_variable_and_or_'+id[0]+"_"+id[1]+"_"+id[2]+'" onchange="addMonsterEquation(\''+id[0]+'_'+id[1]+'_'+id[2]+'\')"> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_variable_add_'+id[0]+"_"+id[1]+'_'+id[2]+'" type="button" value="追加" onclick="addMonsterEquation(\''+id[0]+'_'+id[1]+'_'+id[2]+'\')">'
		
		$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+org).after(result);
		$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+org).hide();
		}else if (id.length==2){
		result+="<br><input type=\"text\" onfocus=\"showMonsterEquation('get_monster_variable_"+id[0]+"_"+id[1]+"')\" id=\"get_monster_variable_"+id[0]+"_"+id[1]+"\">"
		result+='<select id="get_monster_variable_equal_'+id[0]+'_'+id[1]+'"><option value="">全て</option><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select>'
		result+='<select id="monster_variable_and_or_'+id[0]+"_"+id[1]+'" onchange="addMonsterEquation(\''+id[0]+'_'+id[1]+'\')"> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_variable_add_'+id[0]+"_"+id[1]+'" type="button" value="追加" onclick="addMonsterEquation(\''+id[0]+'_'+id[1]+'\')">'
		
		$("#monster_variable_add_"+id[0]+"_"+org).after(result);
		$("#monster_variable_add_"+id[0]+"_"+org).hide();
		}
	}
	function addMonsterEquation2(id,kinds_org){
		kinds = kinds_org.split("|")
		id = id.split("_");
		org = id[id.length-1];
		id[id.length-1] = String(parseInt(id[id.length-1])+1);
		if(id.length == 4){
			var result="";
			result+="<select id=\"get_monster_variable"+id[0]+"_"+id[1]+"_"+id[2]+"_"+id[3]+"\">";
			result+="<option value=\"0\">全て</option>"
			for(var i=0;i<kinds.length;i++){
					result+="<option value=\""+i+"\">"+kinds[i]+"</option>"
			}
			result+="</select>";
			result+='<input id="monster_variable_add_'+id[0]+"_"+id[1]+'_'+id[2]+'_'+id[3]+'" value="追加" type="button" onclick="addMonsterEquation2(\''+id[0]+'_'+id[1]+'_'+id[2]+'_'+id[3]+'\',\''+kinds_org+'\')"><br>'
			$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+org).after(result);
			$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+id[2]+"_"+org).hide();
		}else if(id.length == 3){
			var result="";
			result+="<select id=\"get_monster_variable"+id[0]+"_"+id[1]+"_"+id[2]+"\">";
			result+="<option value=\"0\">全て</option>"
			for(var i=0;i<kinds.length;i++){
					result+="<option value=\""+i+"\">"+kinds[i]+"</option>"
			}
			result+="</select>";
			result+='<input id="monster_variable_add_'+id[0]+"_"+id[1]+'_'+id[2]+'" value="追加" type="button" onclick="addMonsterEquation2(\''+id[0]+'_'+id[1]+'_'+id[2]+'\',\''+kinds_org+'\')"><br>'
			$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+org).after(result);
			$("#monster_variable_add_"+id[0]+"_"+id[1]+"_"+org).hide();
		}else if(id.length == 2){
			var result="";
			result+="<select id=\"get_monster_variable"+id[0]+"_"+id[1]+"\">";
			result+="<option value=\"0\">全て</option>"
			for(var i=0;i<kinds.length;i++){
					result+="<option value=\""+i+"\">"+kinds[i]+"</option>"
			}
			result+="</select>";
			result+='<input id="monster_variable_add_'+id[0]+'_'+id[1]+'" value="追加" type="button" onclick="addMonsterEquation2(\''+id[0]+'_'+id[2]+'\',\''+kinds_org+'\')"><br>'
			$("#monster_variable_add_"+id[0]+"_"+org).after(result);
			$("#monster_variable_add_"+id[0]+"_"+org).hide();
		}
	}
	function addMonsterName(id){
		id = id.split("_");
		org = id[id.length-1];
		id[id.length-1] = String(parseInt(id[id.length-1])+1);
		var result="";
		if(id.length==3){
	result+="<input type=\"text\" onfocus=\"showMonsterNameEqual('"+id[0]+"_"+id[1]+"_"+id[2]+"')\" id=\"monster_name_"+id[0]+'_'+id[1]+"_"+id[2]+"\">";
	result+='<select id="get_monster_name_equal_'+id[0]+'_'+id[1]+'_'+id[2]+'"><option value="">全て</option><option value="=">=</option><option value="like">含む</option></select><select id="monster_name_and_or_'+id[0]+'_'+id[1]+'_'+id[2]+'" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_name_add_'+id[0]+'_'+id[1]+'_'+id[2]+'" type="button" value="追加"  onclick="addMonsterName(\''+id[0]+"_"+id[1]+'_'+id[2]+'\')"><br>';
		
		$("#monster_name_add_"+id[0]+"_"+id[1]+"_"+org).after(result);
		$("#monster_name_add_"+id[0]+"_"+id[1]+"_"+org).hide();
		}else if(id.length==2){
	result+="<input type=\"text\" onfocus=\"showMonsterNameEqual('"+id[0]+"_"+id[1]+"')\" id=\"monster_name_"+id[0]+'_'+id[1]+"\">";
	result+='<select id="get_monster_name_equal_'+id[0]+'_'+id[1]+'"><option value="">全て</option><option value="=">=</option><option value="like">含む</option></select><select id="monster_name_and_or_'+id[0]+'_'+id[1]+'" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_name_add_'+id[0]+'_'+id[1]+'" type="button" value="追加"  onclick="addMonsterName(\''+id[0]+"_"+id[1]+'\')"><br>';
		
		$("#monster_name_add_"+id[0]+"_"+org).after(result);
		$("#monster_name_add_"+id[0]+"_"+org).hide();
		}else if(id.length==1){
	result+="<input type=\"text\" onfocus=\"showMonsterNameEqual('"+id[0]+"')\" id=\"monster_name_"+id[0]+"\">";
	result+='<select id="get_monster_name_equal_'+id[0]+'"><option value="">全て</option><option value="=">=</option><option value="like">含む</option></select><select id="monster_name_and_or_'+id[0]+'" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><input id="monster_name_add_'+id[0]+'" type="button" value="追加"  onclick="addMonsterName(\''+id[0]+'\')"><br>';
		
		$("#monster_name_add_"+org).after(result);
		$("#monster_name_add_"+org).hide();
		}
	}
	function showMaxEquationTo(){
		monster_or_global = "max_equation_number_to";
		showEquationDet();
	}
	function showMinEquationTo(){
		monster_or_global = "min_equation_number_to";
		showEquationDet();
	}
	function showMaxEquation(num){
		monster_or_global = "max_equation_number_"+num;
		showEquationDet();
	}
	function showMinEquation(num){
		monster_or_global = "min_equation_number_"+num;
		showEquationDet();
	}
	function showVariableEquation(){
		monster_or_global = "variable_change_val";
		showEquationDet();
	}
	function showMonsterVariableEquation(i){
		monster_or_global = "monster_variable_change_val"+i;
		showEquationDet();
	}
	function showFlagEquation(){
		monster_or_global = "flag_change_val";
		showEquationDet();
	}
	function putEquation(){

	var equation = $("#equation_editor_det").val();
	equation = equation.split("");
	
	var i;
	var j;
	var c;
	var index;
	var stack = [];
	var result = [];
	var workstack = [];
        for(i = 0;i<equation.length;i++){
		token = equation[i];
           	 switch (token) {
               	 case '+':
               	 case '-':
                 	while (stack.length!=0) {
                        	c = stack[stack.length-1];
	                        if (c == '*' || c == '/') {
	                            result.push(stack.pop());
	                        } else {
	                            break;
	                        }
	                 }
                   	 stack.push(token);
                   	 break;
              	 case '*':
               	 case '/':
               	 case '(':
                    stack.push(token);
                    break;
                case ')':
                    index = stack.indexOf('(');

			workstack = [];
                    for (j = 0; j <= index; i++) {
                         c = stack.pop();
                        if (c != '(') {
                            workStack.push(c);
                        }
                    }

                    while (workStack.length != 0) {
                        result.push(workStack.pop());
                    }
                    break;
		case '{':
			variable = "";
			for(;equation[i]!="}";i++){
				variable += equation[i];
			}
			variable+="}";
			result.push(variable);
			break;
		case '^':
			variable = "^";
			i++;
			for(;equation[i]!="^";i++){
				variable += equation[i];
			}
			variable+="^";
			result.push(variable);
			break;
		case '[':
			variable = "";
			for(;equation[i]!="]";i++){
				variable += equation[i];
			}
			variable+="]";
			result.push(variable);
			break;
		case '|':
			variable = "|";
			i++;
			for(;equation[i]!="|";i++){
				variable += equation[i];
			}
			variable+="|";
			console.log(variable);
			result.push(variable);
			break;
		case '&':
			variable = "&";
			i++;
			for(;equation[i]!="&";i++){
				variable += equation[i];
			}
			variable+="&";
			result.push(variable);
			break;
		case 't':
			variable = "t";
			i++;
			for(;equation[i]!="t";i++){
				variable += equation[i];
			}
			variable+="t";
			result.push(variable);
			break;
                default:
                    // 数値の場合
                    result.push(token);
                    break;
            }
        }

        while (stack.length != 0) {
            result.push(stack.pop());
        }
	$("#"+monster_or_global).val(result.join("$"));
    }
	function showIfEditorPlaceIsField(){
		var tmp = $("#equation_editor_place").val();
		tmp = tmp.split("_");
		if(tmp[0] == "field"){
			$("#editor_place_is_designated").show();
		}else{
			$("#editor_place_is_designated").hide();
		}
	}
	function showXandYForEditorPlace(){
		var tmp = $("#editor_place_is_designated").val();
		if(tmp[0] == "1"){
			$("#equation_editor_x_and_y").show();
		}else{
			$("#equation_editor_x_and_y").hide();
		}
	}
	function getShuffle(){
		$("#shuffle").show();
		$("#shuffle").draggable();
		$("#shuffle").offset({top:0,left:200});
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_place_kind/",
		   'data': "",
			'success': function(data){
				$("#monster_effect_shuffle_place").html(data);
			}
		});
	}
	function putShuffle(id){
		var val= $("#"+id).val();
		var tmp = $("#monster_effect_shuffle_place").val();
		var val2;
		if(val == ""){
			val2=[];
		}else{
			val2= JSON.parse(val);
		}
		json={};
		json["place"] = {};
		json["place"][0] = tmp;
		val2.push(json);
		val = JSON.stringify(val2);
		$("#"+id).val(val);
	}
	function getRaiseTrigger(){
		$("#raise_trigger").show();
		$("#raise_trigger").draggable();
		$("#raise_trigger").offset({top:0,left:200});
		$.ajax({
		   'type': "POST",
		   'url': "/tcgcreator/get_trigger/",
		   'data': "",
			'success': function(data){
				$("#monster_effect_raise_trigger").html(data);
			}
		});
	}
	function putRaiseTrigger(id){
		var val= $("#"+id).val();
		var tmp = $("#monster_effect_raise_trigger").val();
		var val2;
		if(val == ""){
			val2=[];
		}else{
			val2= JSON.parse(val);
		}
		json={};
		json["trigger"] = {};
		json["trigger"][0] = tmp;
		val2.push(json);
		val = JSON.stringify(val2);
		$("#"+id).val(val);
	}
    function showMonsterVariable(id){
        $(".show_monster_variable_"+id).hide();
        $(".hide_monster_variable_"+id).show();
        $(".monster_variable_box"+id).show();
        }
    function hideMonsterVariable(id){
        $(".show_monster_variable_"+id).show();
        $(".hide_monster_variable_"+id).hide();
        $(".monster_variable_box"+id).hide();
        }
    function showCardExist(){
        $(".show_card_exist").hide();
        $(".hide_card_exist").show();
        $(".card_exist_box").show();
        }
    function hideCardExist(){
        $(".show_card_exist").show();
        $(".hide_card_exist").hide();
        $(".card_exist_box").hide();
        }
    function showFieldXandY(){
        $(".show_field_x_and_y").hide();
        $(".hide_field_x_and_y").show();
        $(".field_x_and_y").show();
        }
    function hideFieldXandY(){
        $(".show_field_x_and_y").show();
        $(".hide_field_x_and_y").hide();
        $(".field_x_and_y").hide();
        }
    function showTo(){
        $(".show_to").hide();
        $(".hide_to").show();
        $(".to").show();
        }
    function hidePutFlag(){
        $(".show_to").show();
        $(".hide_to").hide();
        $(".to").hide();
        }
    function showPutFlag(){
        $(".show_put_flag").hide();
        $(".hide_put_flag").show();
        $("#monster_variable_change").show();
        }
    function hidePutFlag(){
        $(".show_put_flag").show();
        $(".hide_put_flag").hide();
        $("#monster_variable_change").hide();
        }
    function showAsMonster(){
        $(".show_as_monster").hide();
        $(".hide_as_monster").show();
        $(".as_monster").show();
        }
    function hideAsMonster(){
        $(".show_as_monster").show();
        $(".hide_as_monster").hide();
        $(".as_monster").hide();
        }
    function showEquation(){
        $(".show_equation").hide();
        $(".hide_equation").show();
        $(".monster_equation").show();
        }
    function hideEquation(){
        $(".show_equation").show();
        $(".hide_equation").hide();
        $(".monster_equation").hide();
        }
    function showExclude(){
        $(".show_exclude").hide();
        $(".hide_exclude").show();
        $(".exclude").show();
        }
    function hideExclude(){
        $(".show_exclude").show();
        $(".hide_exclude").hide();
        $(".exclude").hide();
        }
    function showCustomMonsterCondition(){
        $(".show_custom_monster_condition").hide();
        $(".hide_custom_monster_condition").show();
        $(".custom_monster_condition_box").show();
        }
    function hideCustomMonsterCondition(){
        $(".show_custom_monster_condition").show();
        $(".hide_custom_monster_condition").hide();
        $(".custom_monster_condition_box").hide();
        }
    function showMonsterCondition(){
        $(".show_monster_condition").hide();
        $(".hide_monster_condition").show();
        $(".monster_condition_box").show();
        }
    function hideMonsterCondition(){
        $(".show_monster_condition").show();
        $(".hide_monster_condition").hide();
        $(".monster_condition_box").hide();
        }
    function showMonsterId(){
        $(".show_monster_id").hide();
        $(".hide_monster_id").show();
        $(".monster_id_box").show();
        }
    function hideMonsterId(){
        $(".show_monster_id").show();
        $(".hide_monster_id").hide();
        $(".monster_id_box").hide();
        }
    function showMonsterName(){
        $(".show_monster_name").hide();
        $(".hide_monster_name").show();
        $(".monster_name_box").show();
        }
    function hideMonsterName(){
        $(".show_monster_name").show();
        $(".hide_monster_name").hide();
        $(".monster_name_box").hide();
        }
    function showFlag(){
        $(".show_flag").hide();
        $(".hide_flag").show();
        $(".flag_box").show();
        }
    function hideFlag(){
        $(".show_flag").show();
        $(".hide_flag").hide();
        $(".flag_box").hide();
        }
    function showPlace(){
        $(".show_place").hide();
        $(".hide_place").show();
        $(".trigger_condition_place_box").show();
        }
    function hidePlace(){
        $(".show_place").show();
        $(".hide_place").hide();
        $(".trigger_condition_place_box").hide();
        }
	function addPlace(place,i,j,json=null){
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_place_kind/",
   'data': "",
'success': function(data){
		if(j!=undefined){
			if( $("#"+place+"_"+i+"_"+j).length == 0){
			$("#"+place+"_add_"+i+"_"+(j-1)).after('<select id="'+place+'_'+i+'_'+j+'" class="monster_condition_place" style=""> </select> <select id="'+place+'_add_'+i+"_"+j+'" onchange="addPlace(\''+place+'\','+i+','+(j+1)+')" class="monster_condition_place" style=""> <option value=""></option><option value="and"> <option value="or">または</option> </select>');
			 $("#"+place+"_"+i+"_"+j).html(data);
			}
		}else{
			if( $("#"+place+"_"+i).length == 0){
			$("#"+place+"_add_"+i).after('<select id="'+place+'_'+i+'" class="monster_condition_place" style=""> </select> <select id="'+place+'_add_'+i+'" onchange="addPlace(\''+place+'\','+(i+1)+','+')" class="monster_condition_place" style=""> <option value=""></option><option value="and"> <option value="or">または</option> </select>');
			 $("#"+place+"_"+i).html(data);
			}
		}
		if(json != null){
		    putPlace(place,i,j,json)
		}
	}
	});
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
	function addFieldX(i,next,id){
		result='<input id="'+id+'_field_x_'+i+'_'+next+'" style=""><input type="button" value="追加" id="add_field_x_'+i+'_'+next+'" onclick="addFieldX('+i+','+(next+1)+',\''+id+'\')">'
		result+='演算子<select id="get_field_x_det_'+i+'_'+next+'"><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>';
		result+='<select id="get_field_x_and_or_'+i+'_'+next+'" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select><br>';
		$("#add_field_x_"+i+"_"+(next-1)).after(result);
	}
	function addFieldY(i,next,id){
		result='<input id="'+id+'_field_y_'+i+'_'+next+'" style="">';
		result+='演算子<select id="get_field_y_det_'+i+'_'+next+'"><option value="=">=</option><option value="!=">!=</option><option value=">=">&gt;=</option><option value="<=">&lt;=</option></select><br>';
		result+='<select id="get_field_y_and_or_'+i+'_'+next+'" > <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select>';
		result+='<input type="button" value="追加" id="add_field_y_'+i+'_'+next+'" onclick="addFieldX('+i+','+(next+1)+',\''+id+'\')"><br>'
		$("#add_field_y_"+i+"_"+(next-1)).after(result);
	}
