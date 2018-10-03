    var global_id = "";
    function displayCondition(id,i,j){
        var k;
        for(k=1;$("#"+id+"_"+i+"_"+k).length != 0;k++){
            $("#"+id+"_"+i+"_"+k).hide();
            $("#"+id+"_button_"+i+"_"+k).removeClass("active");
        }
            $("#"+id+"_button_"+i+"_"+j).addClass("active");
        $("#"+id+"_"+i+"_"+j).show();
    }
    function displayConditionAll(id,i){
        var k;
        var j;
        for(k=0;$("#choose_"+id+"_"+k).length != 0;k++){
            $("#as_"+id+"_wrapper_"+k).hide();
            for(j=1;$("#"+id+"_"+k+"_"+j).length;j++){
                $("#"+id+"_"+k+"_"+j).hide();
            }
            $("#"+id+"_wrapper_"+k).hide();
            $("."+id+"_equation").hide();
            $("#choose_"+id+"_"+k).hide();
            $("#choose_"+id+"_"+k).removeClass("active");
        }
        $("#choose_"+id+"_"+i).addClass("active");
        $("#choose_"+id+"_"+i).show();
        $("#"+id+"_"+i+"_"+1).show();
        $("#"+id+"_equation_"+i).show();
        $("#as_"+id+"_wrapper_"+i).show();
    }
    function addConditionPlace(id,i,j){
        if(!(i==0 && j==1)){
            $("#"+id+"_add_button_"+i+"_"+j).remove();
        }else{
            $("#"+id+"_add_button_"+i+"_"+j).hide();
        }
    j++;

    $("#"+id+"_button_"+i+"_"+(j-1)).after('<input type="button" value="条件'+j+'" onclick="displayCondition(\''+id+'\','+i+','+j+')" id="'+id+'_button_'+i+'_'+j+'"><input type="button" value="追加" id="'+id+'_add_button_'+i+'_'+j+'" onclick="addConditionPlace(\''+id+'\','+i+','+j+')">');
        $.ajax({
               'type': "POST",
               'url': "/tcgcreator/get_monster_condition/",
               'data': "i="+i+"&j="+j,
            'success': function(data){
        $("#"+id+"_"+i+"_"+(j-1)).after('<div id="'+id+'_'+i+'_'+j+'"><div id="monster_monster_'+i+'_'+j+'" style=""></div> </div> <div id="monster_equation_'+i+'_'+j+'" class="monster_equation" style=""></div> </div> </div>');
                    $("#monster_monster_"+i+"_"+j).show();
                    $("#monster_monster_"+i+"_"+j).html(data);
                    displayCondition(id,i,j);
                    }
        })
        }
    function ChooseBoth(){
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
                         'data': "id="+id+"&c=0",
                        'success': function(data){
                            $("."+id+"_field_x_and_y_0").show();
                            $("#"+id+"_field_x_and_y_0").html(data);
                         }
                    })
                    }
                })
        }
    })
    var i=0;
    var j=1;
    $("#choose_"+id+"_"+i).after('<div id="choose_'+id+'_'+j+'"> <input type="button" class="active" value="条件1" onclick="displayCondition(\''+id+'\','+j+',1)" id="'+id+'_button_'+j+'_1"><input type="button" value="追加" id="'+id+'_add_button_'+j+'_1" onclick="addConditionPlace(\''+id+'\','+j+',1)"><br><select id="'+id+'_place_'+j+'_0" class="'+id+'_place" style=""> </select> <select id="'+id+'_place_add_'+j+'_0" onchange="addPlace(\''+id+'_place\','+j+',1)" class="'+id+'_place" style=""> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select> <div id="'+id+'_'+j+'_1"> </div> <div id="'+id+"_field_x_and_y_"+j+'"></div><div id="'+id+'_equation_'+j+'" class="'+id+'_equation" style=""></div> </div> </div>as<a class="show_as_monster" href="javascript:showAsMonster()">+</a><a style="display:none" class="hide_as_monster" href="javascript:hideAsMonster()">-</a><div "display:none" class="as_monster" id="as_'+id+'_wrapper_'+j+'">as <input type="text" id="as_'+id+'_'+j+'"></div> </div > </div></div>');
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
                            displayConditionAll(id,0);
                         }
                    })
                    $.ajax({
                         'type': "POST",
                         'url': "/tcgcreator/get_field_x_and_y/",
                         'data': "id="+id+"&c="+j,
                        'success': function(data){
                            $("."+id+"_field_x_and_y").show();
                            $("#"+id+"_field_x_and_y_"+j).html(data);
                         }
                    })
                    }
        })
    }});
    }

    function getConditionKind(id_det,kind,y,x){
        global_id = id_det;
        global_mode = kind;
        if(kind == undefined){
            kind =-1;
        }
        id="trigger_condition";
        $("#"+id).show();
        $("#"+id).draggable();
        $("#"+id).offset({top:x,left:y});
        $("#"+id+"_0_1").show();
        if(kind == 3 || kind == 4 || kind == 1){
            $("#monster_effect_place_to").show();
            $.ajax({
           'type': "POST",
        'url': "/tcgcreator/get_place_kind_to/",
   'data': "i=1",
'success': function(data){
        $("#monster_effect_place_1_to").html(data);
        }
        });
        }else{
            $("#monster_effect_place_to").hide();
        }
        if(kind == 4){
            $("#monster_effect_move_to").show();
            $("#trigger_condition_all_add_button_0").hide();
            $("#monster_effect_move_how").show();
        }else{
            $("#monster_effect_move_to").hide();
            $("#trigger_condition_all_add_button_0").show();
            $("#monster_effect_move_how").hide();
        }
        if(kind == 0 || kind == 1 || kind==2 || kind==3 || kind == 4 || kind == 5  || kind==6){
            $("#"+id+"_place_tab").show();
        }else{
            $("#"+id+"_place_tab").hide();
        }
        if(kind == 2){
            $("#"+id+"_variable_condition_tab").show();
            $("#monster_effect_move_how").hide();
        }else{
            $("#"+id+"_variable_condition_tab").hide();
        }
        if(kind == 6){
            $("#"+id+"_who_choose").show();
            $("#"+id+"_all_button_0").hide();
            $("#"+id+"_all_add_button_0").hide();
            ChooseBoth();
            return;
        }else{
            $("#"+id+"_who_choose").hide();
            $("#"+id+"_all_button_0").show();
            $("#"+id+"_all_add_button_0").show();
        }
    if($("#id_"+global_id).val() == ""){
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
                    if(kind != 3){
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
                    $.ajax({
                         'type': "POST",
                         'url': "/tcgcreator/get_field_x_and_y/",
                         'data': "id="+id+"&c=0",
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
        getConditionKindWithData(id_det,kind,y,x);
    }
    }
    function getConditionKindWithData(id_det,kind,y,x){
        global_id = id_det;
        global_mode = kind;
        if(kind == undefined){
            kind =-1;
        }
        id="trigger_condition";
        var val = $("#id_"+id_det).val();
        val = JSON.parse(val);
        $("#"+id).show();
        $("#"+id).draggable();
        $("#"+id).offset({top:x,left:y});
        $("#"+id+"_0_1").show();
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
                    if(kind != 3){
                    $.ajax({
                         'type': "POST",
                         'url': "/tcgcreator/get_equation/",
                         'data': "c=0",
                        'success': function(data){
                            $("."+id+"_equation").show();
                            $("#"+id+"_equation_0").html(data);
            putConditionVal(0,val);
            for(k=1;val["monster"][k] != undefined;k++){
                addConditionPlaceAll(id,k-1,val);
            }
                         }
                    })
                    }
                    $.ajax({
                         'type': "POST",
                         'url': "/tcgcreator/get_field_x_and_y/",
                         'data': "id="+id+"&c=0",
                        'success': function(data){
                            $("."+id+"_field_x_and_y_0").show();
                            $("#"+id+"_field_x_and_y_0").html(data);
        if(kind == 3 || kind == 4 || kind == 1){
            if($.inArray("exclude",val)){
                $("#exclude_change_variable").val(val["exclude"]);
            }
            if($.inArray("flag_change_how",val)){
                $("#flag_change_how").val(val["flag_change_how"]);
            }
            if($.inArray("flag_change_val",val)){
                $("#flag_change_val").val(val["flag_change_val"]);
            }
            $("#monster_effect_place_to").show();
            $.ajax({
           'type': "POST",
        'url': "/tcgcreator/get_place_kind_to/",
   'data': "i=1",
'success': function(data){
        $("#monster_effect_place_1_to").html(data);
        $("#monster_effect_place_1_to").val(val["place_to"][0]);
        if(val["monster_variable_change_name"][0] != undefined){
            $("#monster_variable_change_name_"+0).val(val["monster_variable_change_name"][0]) ;
            $("#monster_variable_change_how_"+0).val(val["monster_variable_change_how"][0]);
            $("#monster_variable_change_val_"+0).val(val["monster_variable_change_val"][0]);
            for(k=1;val["monster_variable_change_name"][k]!= undefined;k++){
	            addMonsterVariableChange(k-1);
                $("#monster_variable_change_name_"+k).val( val["monster_variable_change_name"][k] );
                $("#monster_variable_change_how_"+k).val(val["monster_variable_change_how"][k]);
                $("#monster_variable_change_val_"+k).val(val["monster_variable_change_val"][k]);
            }
        }
        if(val["relation_name"] != undefined && val["relation_name"][0] != undefined){
            $("#relation_name_"+0).val(val["relation_name"][0]) ;
            $("#relation_monster_"+0).val(val["relation_monster"][0]) ;
            $("#relation_kind_"+0).val(val["relation_kind"][0]) ;
            $("#relation_to_"+0).val(val["relation_to"][0]) ;
            for(k=1;val["relation_name"][k]!= undefined;k++){
	            addPutRelation(k-1);
                $("#relation_name_"+k).val(val["relation_name"][k]) ;
                $("#relation_monster_"+k).val(val["relation_monster"][k]) ;
                $("#relation_kind_"+k).val(val["relation_kind"][k]) ;
                $("#relation_to_"+k).val(val["relation_to"][k]) ;
            }
        }
        }
        });
        }else{
            $("#monster_effect_place_to").hide();
        }
        if(kind == 4){
            $("#monster_effect_move_to").show();
            $("#monster_effect_move_how").val(val["move_how"] );
            $("#monster_effect_move_how_to").val(val["move_how_to"] );
            $("#monster_effect_place_1_to").val(val["place_to"][0]);
            $("#as_monster_effect_to").val(val["as_monster_condition_to"]);
            if(val["field_x_to"] != undefined){
                $("#monster_effect_field_x_to").val(val["field_x_to"]);
            }
            if(val["field_y_to"] != undefined){
                $("#monster_effect_field_y_to").val(val["field_y_to"]);
            }
            $("#trigger_condition_all_add_button_0").hide();
        }else{
            $("#monster_effect_move_to").hide();
            $("#trigger_condition_all_add_button_0").show();
        }
        }
                    })
                    }
                })
        }
    })
    }
    /*
    function getConditionKindWithData(){
        var id="trigger_condition";
        var id_det=global_id;
        var val = $("#id_"+id_det).val();
        val = JSON.parse(val);
        var k;
        $("#monster_effect_place_to").hide();
        if(global_mode==3 || global_mode == 4 || global_mode ==1 ){

        $("#exclude_change_variable").val(val["exclude"]);
        $("#flag_change_how").val(val["flag_change_how"]);
        $("#flag_change_val").val(val["flag_change_val"]);
        for(k=0;k<val["monster_variable_name"].length;k++){
            if($("#monster_variable_name_"+k).length == 0){
                addMonsterVariableChange(k-1);
            }
        $("#monster_variable_name_"+k).val(val["monster_variable_name"][k]);
        $("#monster_variable_who_"+k).val(val["monster_variable_who"][k]);
        $("#monster_variable_change_how_"+k).val(val["monster_variable_change_how"][k]);
        $("#monster_variable_change_val_"+k).val(val["monster_variable_change_val"][k] );
        $("#monster_variable_change_name_"+k).val(val["monster_variable_change_name"][k]);
        }
            }
        $("#as_monster_variable_from").val(val["monster_variable_as"]  );
        }

        kind = global_mode;
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
                    $("#get_monster_place_id_"+i).val(monster[i-1]["monster_place_id"]);
                    $("#get_monster_unique_id_"+i).val(monster[i-1]["monster_unique_id"]);
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
                    if(kind != 3){
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
                    }
                        (function(i,c){
                        $.ajax({
                         'type': "POST",
                         'url': "/tcgcreator/get_field_x_and_y/",
                         'data': "id="+id+"&c="+c,
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
    */
    function putPlace(place,m,l,json){
        place = json["place"][l];
        $("#"+id+"_place_add_"+m+"_"+l).val(place["and_or"]);
        $("#"+id+"_place_"+m+"_"+l).val(place["det"]);
    }
    function putConditionVal(m,val){
        json = {};
        var tmp = {};
        place = [];
        json = val["monster"][m]["monster"];
        for(l=0;json["place"][l]!= undefined;l++){
            addPlace("trigger_condition_place",m,l,json);
        }
        $("#monster_place_id_"+m+"_1").val(json["place_id"]);
        $("#monster_unique_id_"+m+"_1").val(json["unique_id"]);
        for(var j=0;json["monster_name_kind"][j] != undefined;j++){
                $("#get_monster_name_equal_"+m+"_1_"+j).val(json["monster_name_kind"][j]["operator"]) ;
                $("#monster_name_"+m+"_1_"+j).val(json["monster_name_kind"][j]["monster_name"]);
                $("#monster_name_and_or_"+m+"_1_"+j).val(json["monster_name_kind"][j]["and_or"]);
        }
        if(json["flag"]["operator"]!= undefined){
           $("#flag_equal_"+m+"_1").val(json["flag"]["operator"]);
            $("#flag_"+m+"_1").val(json["flag"]["flag_det"] );
        }
        for(j=1;json["monster_condition"][j-1] != undefined;j++){
            for(p=1;$("#get_monster_variable_"+m+"_1_"+p+"_0").length != 0;p++){
                if(json["monster_condition"][j-1][0]["name"] == $("#get_monster_variable_name_"+m+"_1_"+p).val()){
                    break;
                }
            }
            $("#monster_variable_init_"+m+"_1_"+p+"_"+0).val(json["monster_condition"][j-1][0]["init"]);
            for(k=0;json["monster_condition"][j-1][k] != undefined;k++){

                if(k!=0){
                   addMonsterEquation(m+"_1_"+p+"_"+(k-1));
                }
                $("#get_monster_variable_"+m+"_1_"+p+"_"+k).val(json["monster_condition"][j-1][k]["num"]);
                $("#get_monster_variable_equal_"+m+"_1_"+p+"_"+k).val(json["monster_condition"][j-1][k]["operator"]);
                $("#monster_variable_and_or_"+m+"_1_"+p+"_"+k).val(json["monster_condition"][j-1][k]["and_or"]);
            }
         }
        for(j=1;json["custom_monster_condition"][j-1] != undefined;j++){
            for(k=0;json["custom_monster_condition"][j-1][k] != undefined;k++){
                if(k==0){
                    addCustomMonsterCondition(m+'_1_'+j+'_'+k);
                }
                $("#custom_monster_variable_"+m+"_1_"+j+"_0").val(json["custom_monster_condition"][j-1][k]["name"]);
                $("#custom_get_monster_variable_"+m+"_1_"+j+"_"+p).val(json["custom_monster_condition"][j-1][k]["num"]);
                $("#custom_get_monster_variable_equal_"+m+"_1_"+j+"_"+k).val(json["custom_monster_condition"][j-1][k]["operator"]);
                $("#custom_monster_variable_and_or_"+m+"_1_"+j+"_"+k).val();
            }
         }
        if(json["relation"]!= undefined){
        for(j=1;json["relation"][j-1] != undefined;j++){
            for(k=0;json["relation"][j-1][k] != undefined;k++){
                if(k==0){
                    addRelation(m+'_1_'+j+'_'+k);
                }
                $("#relation_"+m+"_1_"+j+"_0").val(json["relation"][j-1][k]);
            }
         }
       }
            $("#as_"+id+"_"+m).val(json["as_monster_condition"]);
        $("#min_equation_number_"+String(m)).val(val["monster"][m]["min_equation_number"]);
        $("#max_equation_number_"+String(m)).val(val["monster"][m]["max_equation_number"]);
        tmp["equation"] = {};
        $("#get_equation_det_"+m).val(val["monster"][m]["equation"]["equation"]);
        $("#get_equation_kind_"+m).val(val["monster"][m]["equation"]["equation_kind"]);
        //$("#get_equation_number_"+m).val(val["monster"][m]["equation"]["equation_number"]);
        $("#"+id+"_and_or_"+m).val(val["monster"][m]["and_or"]);
        $("#exclude_"+0).val(val["exclude"]);
        for(var field_x =0;val["field_x"][field_x] != undefined;field_x++){
            $("#"+id+"_field_x_"+m+"_"+field_x).val(val["field_x"][field_x]);
            $("#get_field_x_det_"+m+"_"+field_x).val(val["field_x_operator"][field_x]);
            $("#get_field_x_and_or_"+m+"_"+field_x).val(val["field_x_and_or"][field_x]);
        }
        for(var field_y =0;val["field_y"][field_y] != undefined;field_y++){
            $("#"+id+"_field_y_"+m+"_"+field_y).val(val["field_y"][field_y]);
            $("#get_field_y_det_"+m+"_"+field_y).val(val["field_y_operator"][field_y]);
            $("#get_field_y_and_or_"+m+"_"+field_y).val(val["field_y_and_or"][field_y]);
        }
    }
    function putCondition(){
        var id = "trigger_condition";
        var id_det = global_id;
        var j;
        mode = global_mode;
            val = {};
            val["monster"] = []
        var k=0;

        var tmp = [];
        var json = {};

        var place;
        if(mode == 3 || mode==4 || mode ==1 || mode == 9){
        val["flag_change_how"]=$("#flag_change_how").val();
        val["flag_change_val"]=$("#flag_change_val").val();
        val["monster_variable_change_name"]=[];
        val["monster_variable_change_how"]=[];
        val["monster_variable_change_val"]=[];
        val["relation_name"]=[];
        val["relation_monster"]=[];
        val["put_relation_kind"]=[];
        val["put_relation_to"]=[];
        for(k=0;$("#monster_variable_change_name_"+k).val();k++){
        val["monster_variable_change_name"][k] = $("#monster_variable_change_name_"+k).val();
        val["monster_variable_change_how"][k] = parseInt($("#monster_variable_change_how_"+k).val());
        val["monster_variable_change_val"][k] = ($("#monster_variable_change_val_"+k).val());
        }
        for(k=0;$("#relation_name_"+k).val();k++){
        val["relation_name"][k]=$("#relation_name_"+k).val();
        val["relation_monster"][k]=$("#relation_monster_"+k).val();
        val["put_relation_kind"][k]=$("#put_relation_kind_"+k).val();
        val["put_relation_to"][k]=$("#put_relation_to_"+k).val();
        }
        }
        k=0;
        if(mode == 1 || mode == 2){
            val["variable"] = []
        var tmp2 = $("#"+id+"_variable_condition_1").val();
        if(tmp2!="" && tmp2!=null){
            json = {};
            for(var i=1;$("#"+id+"_variable_condition_"+(i)).val();i++){
                tmp_json={}
                var tmp = $("#"+id+"_variable_condition_"+i).val();
                var operator = $("#"+id+"_variable_condition_equation_"+(i)).val();
                var variable_val = $("#"+id+"_variable_equation_val_"+(i)).val();;
                var and_or = $("#"+id+"_variable_condition_add_"+(i)).val();;
                if(tmp != "0"){
                    tmp_json["variable"] =  tmp;
                    tmp_json["variable_equation"] =  operator;
                    tmp_json["variable_val"] =  variable_val;
                    tmp_json["and_or"] =  and_or;
                    val["variable"].push(tmp_json)
                }
            }
        }
        }
        var l;
        json = {};
        for(m=0;$("#"+id+"_place_"+m+"_"+0).length;m++ ){
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
            json["place_id"] = $("#monster_place_id_"+m+"_"+i).val();
            json["unique_id"] = $("#monster_unique_id_"+m+"_"+i).val();
            json["place"] = place;
            json["monster_name_kind"] = [];
            for(var j=0;$("#get_monster_name_equal_"+m+"_"+i+"_"+j).length;j++){
            if($("#get_monster_name_equal_"+m+"_"+i+"_"+j).val() == ""){
                json["monster_name_kind"][j] = {};
                json["monster_name_kind"][j]["operator"] = "";
                json["monster_name_kind"][j]["monster_name"] ="";
                json["monster_name_kind"][j]["and_or"] = "";
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
        if($("#flag_"+m+"_"+i).val() == ""){
            json["flag"] = "";
        }else{
            json["flag"] = {};
            json["flag"]["operator"] = "=";
            json["flag"]["flag_det"] =$("#flag_"+m+"_"+i).val();
        }
        json["monster_condition"] = [];
        index2 = 0;
        index_flag = false;
        for(j=1;$("#get_monster_variable_"+m+"_"+i+"_"+j+"_0").length != 0;j++){
            name = $("#get_monster_variable_name_"+m+"_"+i+"_"+j).val();
            init= $("#monster_variable_init_"+m+"_"+i+"_"+j+"_"+0).val();
            init = parseInt(init);
            index = 0;
                if(index_flag == true){
                    index2++;
                }
                index_flag = false;
            for(k=0;$("#get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).length != 0;k++){
            if($("#get_monster_variable_equal_"+m+"_"+i+"_"+j+"_"+k).length != 0){
                num = $("#get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).val();
                operator = $("#get_monster_variable_equal_"+m+"_"+i+"_"+j+"_"+k).val();
                and_or = $("#monster_variable_and_or_"+m+"_"+i+"_"+j+"_"+k).val();
                if(operator == ""){
                    continue;
                }
                if( json["monster_condition"][index2] == undefined){
                    json["monster_condition"][index2] = [];
                    index_flag = true;
                }
                if( json["monster_condition"][index2][index] == undefined){
                    json["monster_condition"][index2][index] = {};
                }
                json["monster_condition"][index2][index]["init"] = init;
                json["monster_condition"][index2][index]["name"] = name;
                json["monster_condition"][index2][index]["num"] = num;
                json["monster_condition"][index2][index]["operator"] = operator;
                json["monster_condition"][index2][index]["and_or"] = and_or;
                index++;

            }else{
                num = $("#get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).val();
                and_or = $("#monster_variable_and_or_"+m+"_"+i+"_"+j+"_"+k).val();
                if(num == "" || num==0){
                    continue;
                }
                if( json["monster_condition"][index2] == undefined){
                    json["monster_condition"][index2] = [];
                    index_flag = true;
                }
                if( json["monster_condition"][index2][index] == undefined){
                    json["monster_condition"][index2][index] = {};
                }
                json["monster_condition"][index2][index]["init"] = init;
                json["monster_condition"][index2][index]["name"] = name;
                json["monster_condition"][index2][index]["num"] = num;
                json["monster_condition"][index2][index]["operator"] = "";
                json["monster_condition"][index2][index]["and_or"] = and_or;
                if(index_flag == true){
                    index2++;
                }
                index++;
            }
            }

        }
        json["custom_monster_condition"] = [];
        for(j=0;$("#custom_monster_variable_"+m+"_"+i+"_"+j+"_0").val();j++){
            json["custom_monster_condition"][j] = [];
            for(k=0;$("#custom_get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).length != 0;k++){
            json["custom_monster_condition"][j][k] = {};
            if($("#custom_get_monster_variable_equal_"+m+"_"+i+"_"+j+"_"+k).length != 0){
                num = $("#custom_get_monster_variable_"+m+"_"+i+"_"+j+"_"+k).val();
                operator = $("#custom_get_monster_variable_equal_"+m+"_"+i+"_"+j+"_"+k).val();
                and_or = $("#custom_monster_variable_and_or_"+m+"_"+i+"_"+j+"_"+k).val();
                if(operator == ""){
                    continue;
                }
                json["custom_monster_condition"][j][k]["name"] = $("#custom_monster_variable_"+m+"_"+i+"_"+j+"_0").val();
                json["custom_monster_condition"][j][k]["num"] = num;
                json["custom_monster_condition"][j][k]["operator"] = operator;
                json["custom_monster_condition"][j][k]["and_or"] = and_or;

            }
            }

        }
        json["relation"] = [];
        json["relation_kind"] = [];
        json["relation_to"] = [];
        for(j=0;$("#relation_"+m+"_"+i+"_"+j+"_0").val();j++){
            json["relation"][j] = [];
            json["relation_kind"][j] = [];
            json["relation_to"][j] = [];
            for(k=0;$("#relation_"+m+"_"+i+"_"+j+"_"+k).length != 0;k++){
            if($("#relation_"+m+"_"+i+"_"+j+"_"+k).length != 0){
                json["relation"][j][k] = $("#relation_"+m+"_"+i+"_"+j+"_0").val();
                json["relation_kind"][j][k] = $("#relation_kind_"+m+"_"+i+"_"+j+"_0").val();
                json["relation_to"][j][k] = $("#relation_to_"+m+"_"+i+"_"+j+"_0").val();
            }
            }
        }

        tmp["monster"]=json;
        }
            tmp["as_monster_condition"] = $("#as_"+id+"_"+m).val();
        tmp["min_equation_number"] = $("#min_equation_number_"+m).val();
        tmp["max_equation_number"] = $("#max_equation_number_"+m).val();
        tmp["equation"] = {};
        tmp["equation"]["equation"] = $("#get_equation_det_"+m).val();
        tmp["equation"]["equation_kind"] = $("#get_equation_kind_"+m).val();
       // tmp["equation"]["equation_number"] = $("#get_equation_number_"+m).val();
        var and_or = $("#"+id+"_and_or_"+m).val();
        if( and_or ==  undefined){
            and_or = "and"
        }
        tmp["and_or"] = and_or;
        val["exclude"] = $("#exclude_0").val();
        val["field_x"] = [];
        val["field_x_operator"] = [];
        val["field_x_and_or"] = [];
        for(var field_x=0;$("#"+id+"_field_x_"+m+"_"+field_x).val() != undefined && $("#"+id+"_field_x_"+m+"_"+field_x).val() != "";field_x++){
            val["field_x"][field_x] = $("#"+id+"_field_x_"+m+"_"+field_x).val();
            val["field_x_operator"][field_x] = $("#get_field_x_det_"+m+"_"+field_x).val();
            val["field_x_and_or"][field_x] = $("#get_field_x_and_or_"+m+"_"+field_x).val();
        }
        val["field_y"] = [];
        val["field_y_operator"] = [];
        val["field_y_and_or"] = [];
        for(var field_y=0;$("#"+id+"_field_y_"+m+"_"+field_y).val() != undefined && $("#"+id+"_field_y_"+m+"_"+field_y).val() != "";field_y++){
            val["field_y"][field_y] = $("#"+id+"_field_y_"+m+"_"+field_y).val();
            val["field_y_operator"][field_y] = $("#get_field_y_det_"+m+"_"+field_y).val();
            val["field_y_and_or"][field_y] = $("#get_field_y_and_or_"+m+"_"+field_y).val();
        }
        val["monster"].push(tmp);
        }
        val["sentence"] = $("#sentence").val();
        val["whether_monster"] = $("#monster_exist").prop("checked")?1:0;
        if(mode==2){
            val["move_how"] = parseInt($("#"+id+"_move_how").val());;
        }
        if(mode == 4 || mode == 3 || mode == 1){
            val["move_how"] = parseInt($("#monster_effect_move_how").val());
            val["move_how_to"] = parseInt($("#monster_effect_move_how_to").val());
            var tmp = $("#monster_effect_place_1_to").val();
            val["place_to"] = {};
            val["place_to"][0] =  tmp;
            val["as_monster_condition_to"] = $("#as_monster_effect_to").val();
            if($("#monster_effect_field_x_to").val() != ""){
                val["field_x_to"] = $("#monster_effect_field_x_to").val();
            }
            if($("#monster_effect_field_y_to").val() != ""){
                val["field_y_to"] = $("#monster_effect_field_y_to").val();
            }
        }
        var j=0;
        val =  JSON.stringify(val);
        $("#id_"+id_det).val(val);
        $("#"+id).hide();
        for(var i=2;$("#"+id+"_place_"+(i)).length;i++){
            $("#"+id+"_place_"+i).remove();
            $("#"+id+"_place_add"+i).remove();

        }
        $("#"+id+"_equation_0").html("");
        for(var i=1;$("#"+id+"_equation_"+(i)).length;i++){
            $("#"+id+"_equation_"+i).remove();

        }


    }
    function addConditionPlaceAll(id,i,json=null){
        if(!(i==0 )){
            $("#"+id+"_all_add_button_"+i).remove();
        }else{
            $("#"+id+"_all_add_button_"+i).hide();
        }
    var j=i+1;
    $("#choose_"+id+"_"+i).after('<div id="choose_'+id+'_'+j+'"> <input type="button" class="active" value="条件1" onclick="displayCondition(\''+id+'\','+j+',1)" id="'+id+'_button_'+j+'_1"><input type="button" value="追加" id="'+id+'_add_button_'+j+'_1" onclick="addConditionPlace(\''+id+'\','+j+',1)"><br> 場所 <a class="show_place" href="javascript:showPlace()">+</a><a style="display:none" class="hide_place" href="javascript:hidePlace()">-</a> <div class="trigger_condition_place_box" style="display:none"> <select id="'+id+'_place_'+j+'_0" class="'+id+'_place" style=""> </select> <select id="'+id+'_place_add_'+j+'_0" onchange="addPlace(\''+id+'_place\','+j+',1)" class="'+id+'_place" style=""> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select></div> <div id="'+id+'_'+j+'_1"> </div>カード有無 <a class="show_card_exist" href="javascript:showCardExist()">+</a><a style="display:none" class="hide_card_exist" href="javascript:hideCardExist()">-</a> <div class="card_exist_box" style="display:none"> <input type="checkbox" id="monster_exist" value="1"> </div><br> フィールド位置  <a class="show_field_x_and_y" href="javascript:showFieldXandY()">+</a><a style="display:none" class="hide_field_x_and_y" href="javascript:hideFieldXandY()">-</a> <div style="display:none" class="field_x_and_y" id="trigger_condition_field_x_and_y_'+j+'"> </div><div id="'+id+'_equation_'+j+'" class="'+id+'_equation" style=""></div> </div> </div><div id="as_'+id+'_wrapper_'+j+'">as <input type="text" id="as_'+id+'_'+j+'"></div> </div > </div></div>');
    $("#"+id+"_all_button_"+i).after('<select id="'+id+'_and_or_'+j+'"><option value=""></option><option value="and">かつ</option><option value="or">または</option></select><input type="button" value="'+(j+1)+'" onclick="displayConditionAll(\''+id+'\','+j+')" id="'+id+'_all_button_'+j+'"><input id="trigger_condition_all_add_button_'+j+'" type="button" value="追加" onclick="addConditionPlaceAll(\''+id+'\','+j+')">');
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
                            displayConditionAll(id,j);
                               $.ajax({
                         'type': "POST",
                         'url': "/tcgcreator/get_field_x_and_y/",
                         'data': "id="+id+"&c="+j,
                        'success': function(data){
                            $("."+id+"_field_x_and_y").show();
                            $("#"+id+"_field_x_and_y_"+j).html(data);
                            if(json!= null){
                                putConditionVal(i+1,json);
                            }
                         }
                    })
                         }
                    })
                    }
        })
    }});

    }
    function addVariableCondition(id,num){
    $("#"+id+"_variable_"+num).after('<div id="'+id+'_variable_'+(num+1)+'"><input type="text" id="'+id+'_variable_condition_'+(num+1)+'" class="variable_condition" style=""> <select id="'+id+'_variable_condition_equation_'+(num+1)+'" class="variable_condition" style=""> <option value="=">=</option> <option value="<=">&lt;=</option> <option value=">=">&gt;=</option> <option value="!=">!=</option> </select> <select id="'+id+'_variable_condition_add_'+(num+1)+'" onchange="addVariable('+id+','+(num+1)+')" class="variable_condition" style=""> <option value=""></option> <option value="and">かつ</option> <option value="or">または</option> </select> <input type="text" id="'+id+'_variable_equation_val_'+(num+1)+'" onfocus="showMonsterEquation(\''+id+'_variable_equation_val_'+(num+1)+'\')"> <input type="button" value="追加" onclick="addVariableCondition(\''+id+'\','+(num+1)+')"></div>');
    }
