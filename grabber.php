<?php
# global variable
$linkcache = array();

function replaceAccents($str)
{
    $search = explode(",", "ç,æ,œ,á,é,í,ó,ú,à,è,ì,ò,ù,ä,ë,ï,ö,ü,ÿ,â,ê,î,ô,û,å,ø,Ø,Å,Á,À,Â,Ä,È,É,Ê,Ë,Í,Î,Ï,Ì,Ò,Ó,Ô,Ö,Ú,Ù,Û,Ü,Ÿ,Ç,Æ,Œ");
    $replace = explode(",", "c,ae,oe,a,e,i,o,u,a,e,i,o,u,a,e,i,o,u,y,a,e,i,o,u,a,o,O,A,A,A,A,A,E,E,E,E,I,I,I,I,O,O,O,O,U,U,U,U,Y,C,AE,OE");
    return str_replace($search, $replace, $str);
}

function shortteamname($tn)
{
    $tn = strtoupper(replaceAccents($tn));
    $shortnames = array('MARTIGNY', 'LUZERN', 'ARLESHEIM', 'CASSARATE', 'MENDRISIOTTO', 'PRILLY', 'COSSONAY', 'CAROUGE', 'BLONAY', 'DEL', 'SION', 'BIENNE', 'GOLDCOAST', 'ARBEDO', 'HELIOS', 'MONTHEY', 'VEVEY', 'STARWINGS', 'VILLARS', 'WINTERTHUR', 'BELLINZONA', 'MEYRIN', 'BADEN', 'BONCOURT', 'MASSAGNO', 'RIVA', 'ELITE', 'NEUCHATEL', 'NYON', 'CENTRAL', 'TROISTORRENTS', 'LUGANO', 'ZURICH', 'AARAU', 'MORGES', 'COLLOMBEY', 'FRIBOURG', 'PULLY LAUSANNE', 'PULLY', 'GENEVE', 'BERNEX', 'CHENE', 'AGAUNE', 'RENENS', 'SARINE', 'KLEINBASEL', 'GC', 'LANCY', 'VAL', 'SOLOTHURN', 'JURA', 'SACONNEX', 'LAVAUX', 'EPALINGES', 'BERN', 'DIVAC', 'OLTEN', 'STB', 'VACALLO', 'VIGANELLO');
    foreach ($shortnames as $value) {
        if (strpos($tn, $value) !== false) {
            return $value;
            break;
        }
    }
    return "NONE";
}

function extractplayerstats($lshort, $teamname, $dati, $tstamp, $playerstats, $matchesarray, $vlk, $lslk)
{
    global $linkcache;
    $csvline = "";
    $shortteamname = shortteamname($teamname);
    for ($counter = 0; $counter < $playerstats; $counter++) {
        #print_r($linkcache);
        #echo "counter: ".$counter."\n";
        # in first item the href needs to be eliminated (item 0, 26, 52, etc.)
        if ((int)($counter / 26) == ($counter / 26)) {
            $personcount = preg_match('/<a href="(.*?)"/s', $matchesarray[1][$counter], $personId);
            #kill the hyperlink statement
            $matchesarray[1][$counter] = preg_replace('/<a href.*class="a_txt8">(.*)/', '', $matchesarray[1][$counter], -1, $count);
            #eliminate special &# character
            $matchesarray[1][$counter] = str_replace("&#39;", "-", $matchesarray[1][$counter]);
            #remove special characters that might give problems later
            $matchesarray[1][$counter] = trim(iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $matchesarray[1][$counter]));
            #get the person Id
            $picturelink = '';
            if ($personcount == true){
                # check in cache if already existing
                if (array_key_exists($lshort."-".$matchesarray[1][$counter], $linkcache) != false){
                    # get the value without making a http call
                    $picturelink = $linkcache[$lshort."-".$matchesarray[1][$counter]][1];
                    #echo "Cached Picturelink: ";
                    #echo $picturelink;
                    #echo "\n";
                } else {
                    # get the value through a http call
                    $personlink = "http://www.basketplan.ch/".$personId[1]."&xmlView=true";
                    #echo $personlink."\n";
                    $rootcontent20 = file_get_contents($personlink);
                    if ($rootcontent20 != false){
                        #echo $rootcontent20;
                        $rootcount20 = preg_match('/<personPicturePath>.*?<String>(.*?)<\/String>.*?<\/personPicturePath>/s', $rootcontent20, $matches20);
                        #echo "Root Count: ".$rootcount20."\n";
                        #print_r($matches20);
                        $filename = explode('/', $matches20[1]);
                        #print_r($filename);
                        $fncounter = count($filename);
                        $picturelink = $filename[$fncounter-1];
                        #echo "Stored Picturelink: ".$picturelink."\n";
                        $picfile = file_get_contents('http://basketplan.ch/uploadedImages/'.$picturelink);
                        #echo $picfile."\n";
                        #echo "Destination: ".$filename[$fncounter-1];
                        file_put_contents('/var/www/html/grabber/pics/'.$picturelink, $picfile);
                        $newarray = array($lshort."-".$matchesarray[1][$counter] => array($lshort, $filename[$fncounter-1]));
                        #print_r($newarray);
                        $linkcache = array_merge($linkcache, $newarray);
                        # getlinkfor picture
                        #echo "new picturelink: ".$picturelink."\n";
                    }
                }
            }
            #add two more fields
            $matchesarray[1][$counter] = trim($lshort) . "," . trim($teamname) . "," . trim($shortteamname) . "," . trim($dati) . "," . trim($tstamp) . "," . trim($matchesarray[1][$counter]).",".trim($personId[1]).",".trim($picturelink);
        }

        # in third argument translate the graphics to true and false
        if (((int)(($counter - 2) / 26) == (($counter - 2) / 26)) or ((int)(($counter - 4) / 26) == (($counter - 4) / 26))) {
            if (strpos($matchesarray[1][$counter], 'false')) {
                $matchesarray[1][$counter] = "false";
            } elseif (strpos($matchesarray[1][$counter], 'true')) {
                $matchesarray[1][$counter] = "true";
            }
        }
        #echo trim($matches6[1][$counter])."\n";
        #echo gettype($matches6[1][$counter]);

        $matchesarray[1][$counter] = trim($matchesarray[1][$counter]);
        $csvline = $csvline . $matchesarray[1][$counter];

        if ((int)(($counter - 25) / 26) == (($counter - 25) / 26)) {
            $csvline = $csvline . "," . $vlk . "," . $lslk;
            $csvline = $csvline . "\r\n";

        } else {
            $csvline = $csvline . ",";
        }
    }
    #echo "return CSVLINE: ". $csvline . "\n";
    return $csvline;
}

function extractlivestats($lshort, $dati, $tstamp, $gn, $lslk, $vlk, $fh2)
{
    $playerphoto = array();
	if ($lslk <> "") {
		$rootcontent10 = file_get_contents('http://www.fibalivestats.com/data/' . $lslk . '/data.json');
		if ($rootcontent10 != false) {
			$rootjson = json_decode($rootcontent10, true);
			if ($rootjson != false) {
				#echo var_dump($rootjson);
				$hometeam = $rootjson['tm'][1]['name'];
				$hometeamshots = $rootjson['tm'][1]['shot'];
				$guestteam = $rootjson['tm'][2]['name'];
				$guestteamshots = $rootjson['tm'][2]['shot'];
				# get starting 5 for each team and write it as additional actions
				$teamplayer = $rootjson['tm'][1]['pl'];
				#print_r($teamplayer);
				foreach ($teamplayer as $key => $val) {
					# $playerphoto = "";
					if (array_key_exists('scoreboardName', $val) != false) {
						if (array_key_exists('photoS', $val) != false) {
							array_push($playerphoto, $val['scoreboardName'], $val['photoS']);
						}
						if ($val['starter'] == 1) {
							#echo $val['scoreboardName'] . "\n";
							#echo $val['starter'] . "\n";							
							$csvline  = $lshort . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $hometeam) . "," . shortteamname($hometeam) . "," . $dati . "," . $tstamp . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $val["scoreboardName"]) . ",";
							$csvline .= "40,substitution,in,,," . substr($vlk,0,11) . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $hometeam) . ",";
							$csvline .= shortteamname($hometeam) . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $guestteam) . "," . shortteamname($guestteam) . "," . $gn . "\r\n";
							
							fwrite($fh2, $csvline);
						}
					} else {
						#echo "not there" . "\n";
					}
				}
				$teamplayer = $rootjson['tm'][2]['pl'];
				foreach ($teamplayer as $key => $val) {
					if (array_key_exists('scoreboardName', $val) != false) {
						if (array_key_exists('photoS', $val) !=false) {
							array_push($playerphoto, $val['scoreboardName'], $val['photoS']);
						}
						if ($val['starter'] == 1) {
							#echo $val['scoreboardName']."\n";
							#echo $val['starter']."\n";
							$csvline  = $lshort . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $guestteam) . "," . shortteamname($guestteam) . "," . $dati . "," . $tstamp . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $val["scoreboardName"]) . ",";
							$csvline .= "40,substitution,in,,," . substr($vlk,0,11) . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $hometeam) . ",";
							$csvline .= shortteamname($hometeam) . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $guestteam) . "," . shortteamname($guestteam) . "," . $gn . "\r\n";
							fwrite($fh2, $csvline);
						}
					} else {
						#echo "not there"."\n";
					}
				}
				#print_r($playerphoto);
				#echo $hometeam."-".$guestteam;
				for ($count = 0; $count < count($rootjson['pbp']); $count++) {
					if (array_key_exists('scoreboardName', $rootjson['pbp'][$count]) == true) {
						$tno = $rootjson['pbp'][$count]['tno'];
						$teamname = '';
						if ($tno == 1) {
							$teamname = $hometeam;
							$teamshots = $hometeamshots;
						} elseif ($tno == 2) {
							$teamname = $guestteam;
							$teamshots = $guestteamshots;
						}
						$playername = $rootjson['pbp'][$count]['scoreboardName'];
						$pmin = intval(substr($rootjson['pbp'][$count]['gt'], 0, 2));
						// convert seconds to decimals
						$psec = intval(substr($rootjson['pbp'][$count]['gt'], 3, 2)) / 60;
						$gperiod = intval($rootjson['pbp'][$count]['period']);
						// what is shown here in overtime?
						$gametime = $gperiod * 10 - $pmin - $psec;
						$actiontype = $rootjson['pbp'][$count]['actionType'];
						$actionnumber = $rootjson['pbp'][$count]['actionNumber'];
						$subtype = '';
						if (array_key_exists('subType', $rootjson['pbp'][$count]) != false) {
							$subtype = $rootjson['pbp'][$count]['subType'];
						}
						$success = '';
						if (array_key_exists('success', $rootjson['pbp'][$count]) != false) {
							$success = $rootjson['pbp'][$count]['success'];
						}

						# get coordinates
						$xcoord = '';
						$ycoord = '';
						if (($actiontype == '2pt') or ($actiontype == '3pt')) {
							#echo "enter parse\n";
							#get the x and y for a shot
							foreach ($teamshots as $key => $val) {
								if ($val['actionNumber'] == $actionnumber) {
									#echo "found: ".$actionnumber."\n";
									$xcoord = $teamshots[$key]['x'];
									$ycoord = $teamshots[$key]['y'];
									break;
								}
							}
						}

						# parsing
						if (($actiontype == '2pt') or ($actiontype == '3pt') or ($actiontype == 'freethrow')) {
							if ($success == 1) {
								$actiontype = $actiontype . '_r';
							} else {
								$actiontype = $actiontype . '_f';
							}
						}
						if ($actiontype == 'rebound') {
							if ($subtype == 'defensive') {
								$actiontype = 'DR';
							} else {
								$actiontype = 'OR';
							}
						}
						#echo $actiontype.", ".$xcoord.", ".$ycoord."\n";
						#print_r($teamshots)."\n";


						$csvline  = $lshort . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $teamname) . "," . shortteamname($teamname) . "," . $dati . "," . $tstamp . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $playername) . ",";
						$csvline .= $gametime . "," . trim($actiontype) . "," . trim($subtype) . "," . trim($xcoord) . "," . trim($ycoord) ."," . substr($vlk,0,11) . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $hometeam) . ",";
						$csvline .= shortteamname($hometeam) . "," . iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $guestteam) . "," . shortteamname($guestteam) . "," . $gn . "\r\n";
						#$csvtitle2 = "League, Club, ClubShort, Date, TimeStamp, PlayerName, GameTime, ActionType, SubType, XCoord, YCoord\r\n";
						fwrite($fh2, $csvline);
					}
					else {
						echo "No scoreboardName\n";
					}

				}


			}
		}
	}
}

function extractgame($lshort, $glink, $gnumber, $vlk, $lslk, $fh, $fh2)
{
    $rootcontent4 = file_get_contents($glink, false, stream_context_create(['http' => ['ignore_errors' => true]]));
    #echo "rootcontent: ".$rootcontent4."\n";
    #extract time and convert to timestamp
    $datetimeday = preg_match('/Date\/Heure\s*<\/td>\s*<td class="txt8">\s*(.*?)&nbsp;\s*(.*?)&nbsp;\s*(.*?)<\/td>/s', $rootcontent4, $matches7);
    #print_r($matches7);
    $datestring = trim($matches7[1]);
    $timestring = trim($matches7[2]);
    $datetime = $datestring . " " . $timestring;
    #echo $datetime;
    $timestamp = strtotime($datetime);
    #echo $timestamp;

    #extract hometeam code
    $homematch = preg_match('/<table id="homeTeamOverViewTable"[^>]*>(?:.|\n)*?<\/table>/m', $rootcontent4, $matches4);
    #print_r($matches4[0]);
    preg_match('/<a class="txt8LRedBGStatTabelLink.*>[\n\s]*(.*)\s/', $matches4[0], $matches5);
    #$hometeamname = iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $matches5[1]);
    $hometeamname = $matches5[1];
    $playerstats = preg_match_all('/\(\'homeTeamOverViewTable\', this\)" onmouseout="resetHighlight\(\)">(.*?)<\/td>/s', $rootcontent4, $matches6);
    #echo "playerstats home: ".$playerstats."\n";
    $csvl = extractplayerstats($lshort, $hometeamname, $datetime, $timestamp, $playerstats, $matches6, $vlk, $lslk);
    #echo $csvl;
    fwrite($fh, $csvl);

    #extract guest team code
    $guestmatch = preg_match('/<table id="guestTeamOverViewTable"[^>]*>(?:.|\n)*?<\/table>/m', $rootcontent4, $matches4);
    #print_r($matches4[0]);
    preg_match('/<a class="txt8LRedBGStatTabelLink.*>[\n\s]*(.*)\s/', $matches4[0], $matches5);
    #$guestteamname = iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $matches5[1]);
    $guestteamname = $matches5[1];
    $playerstats = preg_match_all('/\(\'guestTeamOverViewTable\', this\)" onmouseout="resetHighlight\(\)">(.*?)<\/td>/s', $rootcontent4, $matches6);
    #echo "playerstats guest: ".$playerstats."\n";
    $csvl = extractplayerstats($lshort, $guestteamname, $datetime, $timestamp, $playerstats, $matches6, $vlk, $lslk);
    #echo $csvl;
    fwrite($fh, $csvl);

    #extract livestats data on entire game all teams
    extractlivestats($lshort, $datetime, $timestamp, $gnumber, $lslk, $vlk, $fh2);

}

function extractphase($lshort, $plink, $fhandle, $fhandle2)
{
    $rootcontent3 = file_get_contents($plink, false, stream_context_create(['http' => ['ignore_errors' => true]]));
    #echo "rootcontent3: ".$rootcontent3."\n";
    $gamecount3 = preg_match_all('/onmouseout="resetThisRowColor\(this\)">(.*?)<\/tr>/s', $rootcontent3, $matches3);
    echo "gamecount: " . $gamecount3 . "\n";
    #print_r($matches3[1]);
    foreach ($matches3[1] as $value) {
        # get gamelink
        #echo "value: ".$value."\n";
        $gamecount31 = preg_match_all('/<td class=.*?>(.*?)<\/td>/s', $value, $matches31);
        #echo "game info count: ".$gamecount31."\n";
        #gameshow view is [3]
        #echo "1-3: ".$matches31[1][3]."\n";
        $gamecount311 = preg_match('/showGameOverview\.do\?gameId=(\d\d\d\d\d\d).*(\d\d-\d\d\d\d\d)/s', $matches31[1][3], $matches311);
        echo "gamecount311: ".$gamecount311."\n";
        echo "gameId: ".$matches311[1]."\n";
        echo "gamenumber: ".$matches311[2]."\n";
        $gamelink = "https://www.basketplan.ch/showGameOverview.do?gameId=" . $matches311[1];
        $gamenumber = $matches311[2];
        $videolink = '';
        $livestatlink = '';
        if ($gamecount31 > 13) {
            # get videolink if available [12]
            $gamecount312 = preg_match('/www.youtube.com\/watch\?v=(.*?)\"/s', $matches31[1][12], $matches312);
            if ($gamecount312 != false) {
                $videolink = $matches312[1];
            }
            # get livestatlink if available [13]
            $gamecount313 = preg_match('/www.fibalivestats.com\/u\/SUI\/(.*?)\//s', $matches31[1][13], $matches313);
            if ($gamecount313 != false) {
                $livestatlink = $matches313[1];
            }

        }
        extractgame($lshort, $gamelink, $gamenumber, $videolink, $livestatlink, $fhandle, $fhandle2);
    }
}

# linkcache
# if linkcache file exists, then open it
$dir = "/var/www/html/grabber/";
if (file_exists($dir . 'linkcache.txt')) {
    $file = file_get_contents($dir. 'linkcache.txt');
    $linkcache = unserialize($file);
    echo "cache found";
} else {
    echo "cache not found";
}

# write header
echo "delete old data2.csv file";
$dir = "/var/www/html/grabber/";
if (file_exists($dir . 'data3.csv')) {
    echo "found";
    unlink($dir . 'data3.csv');
} else {
    echo "not found";
}
echo "open new data file";
$fp2 = fopen($dir . 'data3.csv', 'a');
$csvtitle2 = "League,Club,ClubShort,Date,TimeStamp,PlayerName,GameTime,ActionType,SubType,XCoord,YCoord,VideoLink,HClub,HClubShort,GClub,GClubShort,GameNumber\r\n";
fwrite($fp2, $csvtitle2);

echo "delete old data2.csv file";
$dir = "/var/www/html/grabber/";
if (file_exists($dir . 'data2.csv')) {
    echo "found";
    unlink($dir . 'data2.csv');
} else {
    echo "not found";
}
echo "open new data file";
$fp = fopen($dir . 'data2.csv', 'a');
$csvtitle = "League,Club,ClubShort,Date,TimeStamp,PlayerName,PersonId,PictureLink,LicNo,S5,No,Min,2PT_R,2PT_T,2PT_P,3PT_R,3PT_T,3PT_P,FT_R,FT_T,FT_P,OR,DR,TR,AS,BP,INT,B,FP,FPR,EVAL,PM,PTS,VLK,LSTLK\r\n";
fwrite($fp, $csvtitle);

#get main header from basketplan (SBL)
$rootcontent1 = file_get_contents('https://www.basketplan.ch/findAllLeagueHoldings.do?federationId=12', false, stream_context_create(['http' => ['ignore_errors' => true]]));
# scrape main page and SBL leagues
$leaguecount1 = preg_match_all('/<td class="txt8" colspan="1">\s*(.*)/', $rootcontent1, $matches1);
$leaguecount2 = preg_match_all('/<td class="txt8" width="1%" nowrap="nowrap">\s*<a href="(.*)" class="a_txt8"/', $rootcontent1, $matches2);
$maxlines = $leaguecount1 / 5;

for ($counter = 0; $counter < $maxlines; $counter++) {
    $leagueshort = trim($matches1[1][$counter * 5 + 0]);
    if ($leagueshort == 'LNAF' or $leagueshort == 'LNAM' or $leagueshort == 'LNBM' or $leagueshort == 'LNBF' or $leagueshort == 'SuperCupM' or $leagueshort == 'SuperCupF' or $leagueshort == 'SBL CupM' or $leagueshort == 'SBL CupF') {
        $matchlink = "http://www.basketplan.ch/" . $matches2[1][$counter * 3 + 1];
        echo "Loading " . $leagueshort . " - " . $matchlink . "\n";
        #print_r($fp);
        extractphase($leagueshort, $matchlink, $fp, $fp2);
    }
}

#get main header from basketplan (SWB)
$rootcontent1 = file_get_contents('https://www.basketplan.ch/findAllLeagueHoldings.do?federationId=11', false, stream_context_create(['http' => ['ignore_errors' => true]]));
# scrape main page and SBL leagues
$leaguecount1 = preg_match_all('/<td class="txt8" colspan="1">\s*(.*)/', $rootcontent1, $matches1);
$leaguecount2 = preg_match_all('/<td class="txt8" width="1%" nowrap="nowrap">\s*<a href="(.*)" class="a_txt8"/', $rootcontent1, $matches2);
$maxlines = $leaguecount1 / 5;

for ($counter = 0; $counter < $maxlines; $counter++) {
    $leagueshort = trim($matches1[1][$counter * 5 + 0]);
    if ($leagueshort == 'Coupe Suisse M' or $leagueshort == 'Coupe Suisse F') {
        $matchlink = "http://www.basketplan.ch/" . $matches2[1][$counter * 3 + 1];
        echo "Loading " . $leagueshort . " - " . $matchlink . "\n";
        #print_r($fp);
        extractphase($leagueshort, $matchlink, $fp, $fp2);
    }
}

# write cache file
file_put_contents($dir.'linkcache.txt', serialize($linkcache));
# close output file
fclose($fp);
fclose($fp2);

# loop over leagues

# extract league by league the stats by player
?>