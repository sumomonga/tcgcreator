	var prev;
	var current_i = [];
	var monster_kind_id = [];
	$(document).ready(function(){
	
		for(var i=0;i<monster_item_number;i++){
			current_i[i] =1;
			$("#id_monster_item-"+i+"-monster_item_text").after("<input type=\"button\" onclick=\"getItemChangeBefore("+i+")\" value=\"追加\"><input type=\"button\" onclick=\"deleteItemChange("+i+")\" value=\"削除\"><br>");
			getItemChange(i,0);
		}
	});
	function getItemChangeBefore(prefix){
		getItemChange(prefix,current_i[prefix])
		current_i[prefix]++;
	}
	function deleteItemChange(prefix){
		for(var i=0;i<current_i[prefix];i++){
			$("#"+prefix+"-monster_item_text_"+i).remove()
		}
		$("#id_monster_item-"+prefix+"-monster_item_text").val("");
		$("#"+prefix+"_label").remove();
		getItemChange(prefix,0);
		current_i[prefix]=1;
	}
	function changeItemNum(prefix){
		var tmp_str = "";
		for(var i=0;i<current_i[prefix];i++){
			tmp_str+=$("#"+prefix+"-monster_item_text_"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_monster_item-"+prefix+"-monster_item_text").val(tmp_str);

	}
	function getItemChange(prefix,num){
	
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_kind_type_for_new_monster/",
   'data': "delete_flag=0&prefix="+prefix+"&num="+num,
'success': function(data){
		data2 = data.split("$");
		$("#id_monster_item-"+prefix+"-monster_variables_id option[value=\"\"]").attr('selected',false);
		$("#id_monster_item-"+prefix+"-monster_variables_id option[value=\""+(prefix+1)+"\"]").attr('selected',true);
		//$("#id_monster_item-"+prefix+"-monster_variables_id").prop("disabled",true);
		if(data2[1]<2){
			$("#id_monster_item-"+prefix+"-monster_item_text").prop("type","text");
			$("#id_monster_item-"+prefix+"-monster_item_text").before(data2[2]);
		}else{
		if(num==0 ){
			$("#id_monster_item-"+prefix+"-monster_item_text").after("<span id="+prefix+"_label >"+data2[2]+"</span>" + data2[0]);
		}else{
			$("#"+prefix+"-monster_item_text_"+(num-1)).after(data2[0]);
		}
		}
        } 
	})
		
	}
