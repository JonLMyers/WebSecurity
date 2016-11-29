<?php
$base_url = "http://52.90.2.57/armbook/?ARM_SESSION=";
$test_url = "http://52.90.2.57/armbook/home.php";
$urls = array();
$i = 0;
while($i < 50){
  $new_session = substr(md5(time()), 0, 22);
  $value = $base_url.$new_session;
  $response = $value;
  echo "\n";
  echo $response;
  sleep(1);
  $i++;
}
?>
