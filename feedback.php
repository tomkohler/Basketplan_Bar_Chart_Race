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
$argument2 = $_GET['clip'];
#separate the argument before the- and the one after
$feedback = $argument2;
file_put_contents('feedback.txt', $feedback."\n", FILE_APPEND);
echo '<div><h2>Thank your for your feedback. We try to update the incorrect clip in the next weeks!</h2></div>';
?>
</body>
</html>