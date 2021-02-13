<!DOCTYPE html>
<html>
<head>
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
$argument2 = $_GET['f'];
#echo '<div class=container>';
if (file_exists('datafiles2/'.$argument2) != False) {
	echo '<img class="item2" src="datafiles2/'.$argument2.'">'; 
} else {
	echo '<h2>No statistics found!</h2>';
}
#echo '</div>';
?>
</body>
</html>