<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="styles.css">
    <title>Swiss Basketball Statistics</title>
    <meta name="description" content="Swiss Basketball Statistics">
    <meta name="Thomas Kohler" content="SitePoint">
</head>
<body>
<?php
$dir = "/var/www/html/grabber/";
$dir2 = "datafiles2/";
$file = file_get_contents($dir."linkcache.txt");
$linkcache = unserialize($file);
#ksort($linkcache);
#print_r($linkcache);
foreach($linkcache as $name => $value) {
    $picturelink2 = "http://www.basketplan.ch/".$value[1];
    $filename = $dir2.$value[0]."-".$name.".png";
      echo '<section id="photos"><a href="'.$filename.'"><img src="'.$picturelink2.'" alt="'.$name.'" style="width:80px;height:80px;border:5"></a></section>';
}
?>
</body>
</html>