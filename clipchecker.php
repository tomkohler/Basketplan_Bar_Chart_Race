<!DOCTYPE html>
<html>
	<head>
        <style>
            table {
                font-family: arial, sans-serif;
				font-size: 9px;
                border-collapse: collapse;
                width: 100%;
            }
			.eqcol {
				width: 14%;
			}

            td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 3px;
            }

            tr:nth-child(even) {
                background-color: #dddddd;
            }
        </style>
    </head>
<body>
<h2>Clip Checker</h2>
<?php

$excludedclubs = array("SION", "GOLDCOAST", "KLEINBASEL", "MORGES", "LAVAUX");
$excludedleagues = array("SUPERCUPM", "SUPERCUPF");
$excludedgames = array("20-03602", "20-03606", "20-03610");
$prevgamenumber = "";
$counter = 1;

$dir = "/var/www/html/grabber/";
if (($handle = fopen($dir."data3.csv", "r")) !== FALSE) {
  while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
	if ($counter != 1) {
		$league = strtoupper($data[0]);
		$hometeam = $data[13];
		$shot = $data[7];
		$gamenumber = $data[16];
		$awayteam = $data[15];
		$gamedate = $data[3];
		$vlk = $data[11];

		if ($prevgamenumber != $gamenumber) {
			if ((in_array($hometeam, $excludedclubs)==false) and (in_array($league, $excludedleagues) == false) and (in_array($gamenumber, $excludedgames) == false) and ($vlk != "")) {
				echo "</table><h4>".utf8_encode($hometeam)." vs ".utf8_encode($awayteam)." ".$gamedate." ".$gamenumber." ".$league." <a href=https://www.youtube.com/watch?v=".$vlk.">".$vlk."</a></h4>";
				echo "<table><tr><td class=eqcol>Cliplink</td><td class=eqcol>Flag</td><td class=eqcol>Player Name</td><td class=eqcol>Score Team</td><td class=eqcol>Game Time</td><td class=eqcol>Shot</td><td class=eqcol>Shot2</td></tr>";
			}
			$prevgamenumber = $gamenumber;
		}
			
		if ((substr($shot, 1,4) == 'pt_r') and (in_array($hometeam, $excludedclubs)==false) and (in_array($league, $excludedleagues) == false) and (in_array($gamenumber, $excludedgames) == false)) {
			
			$gametime = floatval($data[6]);
			if ($gametime == 40) {
				$q = 4;
			} else {
				$q = intval($gametime/10)+1;
			}
			
			$min = intval(($q * 10) - $gametime);
			if ($min < 0) { $min = 0; } elseif ($min > 40) { $min = 40; }
    
			//$sec = intval(((($q * 10) - $gametime) - $min)*60);
			$sec = intval((1 - ($gametime - intval($gametime))) * 60);
			// needs to be corrected once done in clipextractor.py if ($sec < 0) { $sec = 0; } elseif ($sec > 59) { $min -= 1; $sec = 59; }
			if ($sec < 0) { $sec = 0; } elseif ($sec > 59) { $sec = 59; }
			// echo $q."-".sprintf("%02d", $min).":".sprintf("%02d", $sec)."<br>";
			
			$scoreteam = $data[2];
			
			$shot2 = $data[8];
			$playername = str_replace(" ", "", $data[5]);
			$playernamedisplay = $data[5];
			$quartergametime = $q."-".sprintf("%02d", $min).sprintf("%02d", $sec);
			
			$filename1 = "dataframes/*".utf8_encode($playername)."-".$gamenumber."*-Q".$quartergametime.".mp4";
			$filename2 = "dataframes/*".utf8_encode($playername)."-".$gamenumber."*-Q".$quartergametime.".jpg";
			//$filename = $dir."dataframes/".$playername."*.*";
			//echo $playername;
			//echo count(glob($filename))."<br>";

			if (count(glob($filename1)) > 0) {
				//echo glob($filename1)[0];
				//echo "<tr><td><video width=32 height=18><source src=".glob($filename1)[0]." type=video/mp4></video></td><td><div style='color:green; text-align:center; -webkit-appearance:none;'>&#x2588</div></td>";
				echo "<tr><td><a href=".glob($filename1)[0].">Link</a></td><td><div style='color:green; text-align:center; -webkit-appearance:none;'>&#x2588</div></td>";
			} elseif (count(glob($filename2)) > 0) {
				echo "<tr><td></td><td><div style='color:red; text-align:center; -webkit-appearance:none;'>&#x2588</div></td>";
			} else {
				echo "<tr><td></td><td><div style='color:grey; text-align:center; -webkit-appearance:none;'>&#x2588</div></td>";
			}
			echo "<td>".utf8_encode($playernamedisplay)."</td><td>".$scoreteam."</td><td>Q".$quartergametime."</td><td>".$shot."</td><td>".$shot2."</td></tr>";
		}
	}
	$counter += 1;
  }
  fclose($handle);
}

?>

</body>
</html>