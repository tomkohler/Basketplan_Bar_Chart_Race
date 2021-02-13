<!DOCTYPE html>
<html>
<head>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-152765706-2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-152765706-2');
</script>
  <meta charset="utf-8">
  <link rel="stylesheet" href="styles.css">
  <title>Swiss Basketball Statistics</title>
  <meta name="description" content="Swiss Basketball Statistics">
  <meta name="Thomas Kohler" content="SitePoint">
</head>
<body>
<!-- <h2>Individual Statistics</h2> -->
<div class="topnav">
	<a href="lnam.html">LNAM</a>
	<a href="lnaf.html">LNAF</a>
	<a href="lnbm.html">LNBM</a>
	<a href="lnbf.html">LNBF</a>
	<a href="supercupm.html">SuperCup M</a>
	<a href="supercupf.html">SuperCup F</a>
	<a href="sblcupm.html">SBLCup M</a>
    <a href="sblcupf.html">SBLCup F</a>
    <a href="individual.php">Individual Statistics</a>
	<a href="clips.php">Individual Videoclips</a>

</div>
<?php
$dir = "/var/www/html/grabber/";
$dir2 = "datafiles2/";
$dir3 = "pics/";
$file = file_get_contents($dir."linkcache.txt");
$linkcache = unserialize($file);
ksort($linkcache);
$title = '';
$defaultpicture = 'pics/person-icon.jpg';

foreach($linkcache as $name => $value) {
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
	$temp="dataframes/*".str_replace(' ', '', utf8_encode($playername))."*".$title."*.mp4";
	foreach (glob($temp) as $fileXname) {
		$counter += 1;
	}
	
	if ($counter > 0) {
		echo '<a href="clipshow.php?f='.utf8_encode($filename).'"><img class="item" src="'.utf8_encode($picturelink2).'" alt="'.utf8_encode($playername).'"><figcaption class="fc">'.utf8_encode($playername).' ('.$counter.')</figcaption></a>';
	}
	
    //echo '<a href="clipshow.php?f='.utf8_encode($filename).'"><img class="item" src="'.utf8_encode($picturelink2).'" alt="'.utf8_encode($playername).'"><figcaption class="fc">'.utf8_encode($playername).'</figcaption></a>';
}
echo '</div>';
?>
</body>
</html>