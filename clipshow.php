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
$argument2 = $_GET['f'];
#separate the argument before the- and the one after
$league = explode('-', $argument2)[0];
$playername = substr(explode('-', $argument2)[1],0,-4);
# replace spaces by nothing
$playername2 = preg_replace('/\s+/', '', $playername);
$it = new RecursiveDirectoryIterator("/var/www/html/grabber/dataframes");
$row = 1;
$column = 1;
$maxcolumn = 3;
#echo $league, $playername;
echo '<div><h2>'.$league.'-'.$playername.'</h2></div>';
foreach(new RecursiveIteratorIterator($it) as $file)
{
    # write div code
	#echo($file."\n");
    if (strpos($file, 'mp4') > 0) {
		#echo "seg ok";
		if (strpos($file, $league) > 0) {
			#echo "league ok";
			if (strpos($file, $playername2) > 0) {
				# write header
				if ($column == 1) {
					echo '<div class="section group">';
				}
				# write body
				#echo "all ok";
				#echo explode('grabber/',$file)[0]
				echo '<div class="col span_1_of_3">';
				echo '<video width="640" height="480" controls>';
				echo '<source src="'.explode('grabber/',$file)[1].'" type="video/mp4">';
				echo '</video><a href="feedback.php?clip='.urlencode(explode('grabber/',$file)[1]).'" class="feedback">Clip not correct?</a></div>';
				$column += 1;		
				# write footer
				if ($column > $maxcolumn){
					echo '</div>';
					$column = 1;
					$row += 1;
				}
			}
		}
	}
    
}
if (($row == 1) and ($column == 1)){
echo "<div>No clips found!</div>";
}

?>
</body>
</html>