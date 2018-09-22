	var prev;
	var current_i_deck = 0;
	$(document).ready(function(){
	
			$("#id_monster_deck").after("<input type=\"button\" onclick=\"getDeckChangeBefore()\" value=\"追加\"><input type=\"button\" onclick=\"deleteDeckChange()\" value=\"削除\"><br>");
			getDeckChange(0);
			current_i_deck=1;
	});
	function getDeckChangeBefore(){
		getDeckChange(current_i_deck)
		current_i_deck++;
	}
	function deleteDeckChange(){
		for(var i=0;i<current_i_deck;i++){
			$("#monster_deck_text_"+i).remove()
		}
		$("#id_monster_deck").val("");
		getDeckChange(0);
		current_i_deck=1;
	}
	function changeDeckNum(){
		var tmp_str = "";
		for(var i=0;i<current_i_deck;i++){
			tmp_str+=$("#monster_deck_text_"+(i)).val()+"_";;
		}
		tmp_str = tmp_str.substr(0,tmp_str.length-1);
		$("#id_monster_deck").val(tmp_str);
		

	}
	function getDeckChange(num){
	
	// デッキ構築の時に入れるデッキを決める
	$.ajax({
   'type': "POST",
   'url': "/tcgcreator/get_monster_deck_type/",
   'data': "delete_flag=0&num="+num,
'success': function(data){
		if(num==0 ){
			$("#id_monster_deck").after(data);
		}else{
			$("#monster_deck_text_"+(num-1)).after(data);
			changeDeckNum();
		}
        } 
	})
		
	}
