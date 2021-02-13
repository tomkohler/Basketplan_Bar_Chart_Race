<?php
$dir = "/var/www/html/grabber/";
$dir2 = "datafiles2/";
$dir3 = "pics/";
//echo glob('var/www/html/dataframes/*.mp4');
$file = file_get_contents($dir."linkcache.txt");
$linkcache = unserialize($file);
ksort($linkcache);
$title = '';
$defaultpicture = 'pics/person-icon.jpg';
foreach($linkcache as $name=>$value) {	
    $picturelink2 = $dir3.$value[1];
	if (strlen($picturelink2) <= 5) {
		$picturelink2 = $defaultpicture;
	}
    $filename = $name.".png";
    $playername = substr($name, strpos($name, "-") + 1);
    if($title != $value[0]) {
	$title = $value[0];
        echo '</div><h2>'.$title.'</h2><div class="container">';
    }
	// count files with relevant player name
	$counter=0;
	$temp="dataframes/*/*/*".str_replace(' ', '', $playername)."*seg.mp4";
	foreach (glob($temp) as $filename) {
		$counter += 1;
	}
	//echo $temp."-".$counter;
	//echo $playername."-".$counter;
	if $counter > 0 {
		echo '<a href="imgshow.php?f='.utf8_encode($filename).'"><img class="item" src="'.utf8_encode($picturelink2).'" alt="'.utf8_encode($playername).'"><figcaption class="fc">'.utf8_encode($playername).'('.$counter.')'.'</figcaption></a>';
	}
	//echo '<br>';
}
echo '</div>';
?>