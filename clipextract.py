# import the necessary packages
import datetime
import os
from pathlib import Path

import cv2
import ffmpy
import imutils
import numpy as np
import pandas as pd
import youtube_dl
import random
from PIL import Image, ImageFont, ImageDraw
from imutils import contours

os.environ['DISPLAY'] = ':0'

def write_titleimage(msg1, msg2, msg3, msg4, fpth, fname, pwidth, pheight, length):
    # write image title jpg
    W, H = (pwidth, pheight)
    fnt1 = ImageFont.truetype('arial.ttf', 60)
    fnt2 = ImageFont.truetype('arial.ttf', 48)
    # create new image
    image = Image.new("RGB", (W, H), "black")
    draw = ImageDraw.Draw(image)
    w1, h1 = draw.textsize(msg1, font=fnt1)
    w2, h2 = draw.textsize(msg2, font=fnt2)
    w3, h3 = draw.textsize(msg3, font=fnt2)
    w4, h4 = draw.textsize(msg4, font=fnt2)
    draw.text(((W - w1) / 2, (H - h1) / 2 - 100), msg1, font=fnt1, fill="white")
    draw.text(((W - w2) / 2, (H - h2) / 2 - 25), msg2, font=fnt2, fill="white")
    draw.text(((W - w3) / 2, (H - h3) / 2 + 25), msg3, font=fnt2, fill="white")
    draw.text(((W - w4) / 2, (H - h4) / 2 + 75), msg4, font=fnt2, fill="white")
    image.save(fpth + '/' + fname + '.jpg')

    # make mp4 title screen (inserted globaloptions to be quiet)
    ff = ffmpy.FFmpeg(global_options='-loglevel panic',
                      inputs={fpth + '/' + fname + '.jpg': '-y -loop 1 -t ' + str(length)},
                      outputs={fpth + '/' + fname + '.mp4': None})
    ff.cmd
    ff.run()
    os.remove(fpth + '/' + fname + '.jpg')


def calc_params(gt):
    # INPUT: gametime, which is a float variable counting down the gametime from 40 mins
    # OUTPUT: array with [quarter, minutes, seconds], all as integers
    # EXAMPLE: 9.25 is in 4th quarter, 9th minute and 15th second (0.25 * 60)
    gametimeasc = float(gt)
    if gametimeasc < 0:
        gametimeasc = 0
    qt = int(gametimeasc / 10) + 1
    if qt > 4:
        qt = 4
    elif qt < 1:
        qt = 1
    mm = int((qt * 10) - gametimeasc)
    if mm < 0:
        mm = 0
    elif mm > 40:
        mm = 40
    ss = int((1 - (gametimeasc - int(gametimeasc))) * 60)
    if ss < 0:
        ss = 0
    elif ss > 59:
        ss = 59
    # print(str(GameTime) + "-" + str(gametimeasc) + "-" + str(quarter) + "-" + str(minutes).zfill(2) + ":" + str(
    #    seconds).zfill(2))
    return [qt, mm, ss]


def compare_result(fxquarter, fxminutes, fxseconds, quarter, minutes, seconds, tolerance):
    # INPUT: inputarray is an array with [quarter, gametime], gametime as mmss (mm=minutes ss=seconds)
    # INPUT: quarter, minutes, seconds are integers
    # OUTPUT: resultcode depending on what is found (described further below)
    # validate input
    if tolerance < 0 or tolerance > 10:
        tolerance = 0
    if quarter == fxquarter:
        # quarter correct
        if minutes == fxminutes:
            # quarter, minutes correct
            if seconds == fxseconds or seconds == (fxseconds - tolerance) or (seconds == (fxseconds + tolerance)):
                # quarter, minutes, seconds correct
                result = 10
            elif seconds > fxseconds:
                # quarter, minutes correct, but target seconds are further forward in stream
                result = 3
            else:
                # quarter, minutes correct, but target seconds are further back in stream
                result = -3
        elif minutes > fxminutes:
            # quarter correct, but target minutes are further forward in stream
            result = 2
        else:
            # quarter correct, but target minutes are further forward in stream
            result = -2
    elif quarter > fxquarter:
        # target quarter is further forward in stream
        result = -1
    else:
        # target quarter is further back in stream
        result = 1
    return result


def evaluate_frame(fr, tp):
    # INPUT: cv2 frame, tp is integer indicating the type of panel if already identified otherwise 0
    # OUTPUT: resultarray
    mm = -1
    ss = -1
    qt = -1

    # swissbaskettv panel on xsplit
    if tp == 0 or tp == 1:
        # get and evaluate
        extr_gametime = get_gametime(frame, 975, 609, 80, 35, 0, 0)
        # print(
        #     "VL: " + str(row['VideoLink']) + " -- Counter: " + str(count) + " -- Type: " + str(
        #         type) + " -- Gametime: " + extr_gametime)
        if len(extr_gametime) == 4:
            # validation
            if '0000' <= extr_gametime <= '1000':
                mm = int(extr_gametime[0:2])
                ss = int(extr_gametime[2:4])
                # two variant, one for the manual version the other for the scorebug
                extr_quarter = get_gametime(frame, 906, 609, 20, 35, 0, 0)
                if len(extr_quarter) == 1:
                    if '1' <= extr_quarter <= '4':
                        qt = int(extr_quarter)
                        tp = 1
                else:
                    extr_quarter = get_gametime(frame, 936, 609, 20, 35, 0, 0)
                    if len(extr_quarter) == 1:
                        if '1' <= extr_quarter <= '4':
                            qt = int(extr_quarter)
                            tp = 1
                        else:
                            tp = 0

    # tvgraphics panel on keemotion
    if tp == 0 or tp == 2:
        # get and evaluate
        extr_gametime = get_gametime(frame, 565, 648, 55, 25, 0, 0)
        # print(
        #     "VL: " + str(row['VideoLink']) + " -- Counter: " + str(count) + " -- Type: " + str(
        #         type) + " -- Gametime: " + extr_gametime)
        if len(extr_gametime) == 4:
            # validation
            if '0000' <= extr_gametime <= '1000':
                mm = int(extr_gametime[0:2])
                ss = int(extr_gametime[2:4])
                # two variant, one for the manual version the other for the scorebug
                extr_quarter = get_gametime(frame, 669, 645, 17, 30, 0, 0)
                if len(extr_quarter) == 1:
                    if '1' <= extr_quarter <= '4':
                        qt = int(extr_quarter)
                        tp = 2
                    else:
                        tp = 0

    # default keemotion panel (Nyon)
    if tp == 0 or tp == 4:
        # get and evaluate
        extr_gametime = get_gametime(frame, 540, 645, 60, 30, 0, 0)
        # print(
        #     "VL: " + str(row['VideoLink']) + " -- Counter: " + str(count) + " -- Type: " + str(
        #         type) + " -- Gametime: " + extr_gametime)
        if len(extr_gametime) == 4:
            # validation
            if extr_gametime >= '0000' and extr_gametime <= '1000':
                mm = int(extr_gametime[0:2])
                ss = int(extr_gametime[2:4])
                # two variant, one for the manual version the other for the scorebug
                extr_quarter = get_gametime(frame, 669, 648, 12, 25, 0, 0)
                if len(extr_quarter) == 1:
                    if '1' <= extr_quarter <= '4':
                        qt = int(extr_quarter)
                        tp = 4
                    else:
                        tp = 0

    # tvgraphics panel on xsplit
    if tp == 0 or tp == 3:
        # get and evaluate
        extr_gametime = get_gametime(frame, 540, 645, 60, 30, 0, 0)
        # print(
        #     "VL: " + str(row['VideoLink']) + " -- Counter: " + str(count) + " -- Type: " + str(
        #         type) + " -- Gametime: " + extr_gametime)
        if len(extr_gametime) == 4:
            # validation
            if '0000' <= extr_gametime <= '1000':
                mm = int(extr_gametime[0:2])
                ss = int(extr_gametime[2:4])
                # two variant, one for the manual version the other for the scorebug
                extr_quarter = get_gametime(frame, 669, 648, 17, 25, 0, 0)
                if len(extr_quarter) == 1:
                    if '1' <= extr_quarter <= '4':
                        qt = int(extr_quarter)
                        tp = 3
                    else:
                        tp = 0

    return [qt, mm, ss, tp]


def read_reference_font(fname):
    # load the reference font image from disk, convert it to grayscale,
    # and threshold it, such that the digits appear as *white* on a
    # *black* background
    # and invert it, such that the digits appear as *white* on a *black*
    ref = cv2.imread(fname)
    ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY_INV)[1]

    # find contours in the reference image (i.e,. the outlines of the digits)
    # sort them from left to right, and initialize a dictionary to map
    # digit name to the ROI
    refCnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
    refCnts = imutils.grab_contours(refCnts)
    refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]

    # loop over the reference font  contours
    for (i, c) in enumerate(refCnts):
        # compute the bounding box for the digit, extract it, and resize
        # it to a fixed size
        (x, y, w, h) = cv2.boundingRect(c)
        roi = ref[y:y + h, x:x + w]
        roi = cv2.resize(roi, (57, 88))
        # update the digits dictionary, mapping the digit name to the ROI
        digits[i] = roi

    return True


def get_gametime(img, x1, y1, w1, h1, invert, show):
    # convert to grey and apply threshold
    img = img[y1:y1 + h1, x1:x1 + w1]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # flag to see if we need to invert the frame or not
    if invert == 0:
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    else:
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    if show == 1:
        cv2.imshow('frame', thresh)
        cv2.waitKey(1)

    # find contours in the thresholded image, then initialize the
    # list of digit locations
    groupOutput = ''
    digitCnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    digitCnts = imutils.grab_contours(digitCnts)
    # avoid sorting digits with a count of 0 which leads to an error in sort_contours
    if len(digitCnts) > 0:
        digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
        # loop over the digit contours
        for c in digitCnts:
            # compute the bounding box of the individual digit, extract
            # the digit, and resize it to have the same fixed size as
            # the reference OCR-A images
            (x, y, w, h) = cv2.boundingRect(c)
            # eliminate smaller dots
            if 5 < h < 20 and 3 < w < 20:
                roi = thresh[y:y + h, x:x + w]
                roi = cv2.resize(roi, (57, 88))
                # initialize a list of template matching scores
                scores = []
                # loop over the reference digit name and digit ROI
                for (digit, digitROI) in digits.items():
                    # apply correlation-based template matching, take the
                    # score, and update the scores list
                    result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF)
                    (_, score, _, _) = cv2.minMaxLoc(result)
                    scores.append(score)
                # the classification for the digit ROI will be the reference
                # digit name with the *largest* template matching score
                groupOutput += str(np.argmax(scores))
    return groupOutput


digits = {}
# debug produces more status messages
debug = 1
# simulate = 1 skips the actual generation of clips
simulate = 0
# reference font sbtv
read_reference_font('/var/www/html/grabber/Condensed_Reference_Image.jpg')
# read_reference_font('/var/www/html/grabber/Rubik_Reference_Image.jpg')
# datafile
data = pd.read_csv('/var/www/html/grabber/data3.csv', encoding='iso-8859-1')
pd.set_option('display.max_columns', None)
data2 = data.sort_values(['VideoLink', 'GameTime'], ascending=[True, True])
# extract only actions with points scores
data3 = data2[data2['ActionType'].str.contains('pt_r')]

# excluded clubs
excludedclubs = ["LAVAUX", "SION", "KLEINBASEL", "MORGES", "GOLDCOAST", "ZURICH"]

# seconds before and after the action to be clipped
cliplead = 10
cliptrail = 5

# iterate through results
pVideoLink = ''
nextURL = 0
sequence = 0
count = 0

ydl_opts = {'ignoreerrors': True}
for index, row in data3.iterrows():
    # if URL was not parsed so far, then parse it
    videolink = row['VideoLink']
    if videolink != pVideoLink:
        nextURL = 0
        ytfilename = 'https://www.youtube.com/watch?v=' + str(videolink)
        # starttime to measure throughput time for algorithm
        starttime = datetime.datetime.now()
        # create youtube-dl object
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        # set video url, extract video information
        info_dict = ydl.extract_info(ytfilename, download=False)
        pVideoLink = videolink
        # random jumpin point
        count = random.randint(10000,150000)
        sequence = 0

    if nextURL == 0:
        # get variables from iterrow()
        pastcount = []
        playername = row['PlayerName']
        league = row['League']
        clubshort = row['ClubShort']
        actiontype = row['ActionType']
        subtype = row['SubType']
        # continue either with new filename or old one
        miss1 = 0
        miss2 = 0
        miss3 = 0
        xtype = 0
        resultcode = 0
        fquarter = -1
        fminutes = -1
        fseconds = -1
        if info_dict is not None:
            # print(info_dict)
            # get video formats available
            formats = info_dict.get('formats', None)
            for f in formats:
                # I want the 720p resolution
                if (f.get('format_id', None) == '22'):
                    # get the video url
                    url = f.get('url', None)
                    # open url with opencv
                    cap = cv2.VideoCapture(url)

                    # check if url was opened
                    if not cap.isOpened():
                        print('video not opened')
                        exit(-1)

                    # calculate to which quarter and time to move
                    GameTime = row['GameTime']
                    gamenumber = row['GameNumber']
                    hometeam = row['HClubShort']
                    guestteam = row['GClubShort']
                    gamedate = row['Date']
                    quartertimearray = calc_params(GameTime)

                    # set tolerance to 0 for each new player
                    tol = 0

                    # if hometeam is on exclusion list, the break to no waste computing time
                    if hometeam in excludedclubs:
                        print('excluded club: ' + hometeam)
                        nextURL = 1
                        break

                    # should be all integers
                    dbquarter = quartertimearray[0]
                    dbminutes = quartertimearray[1]
                    dbseconds = quartertimearray[2]

                    print(
                        "Looking for: " + playername + "-" + gamenumber + "-" + league + "-" + clubshort + "-" + hometeam + " vs " + guestteam + " " + actiontype + "-" + subtype + "-" + str(
                            dbquarter) + "-" + str(dbminutes).zfill(2) + ":" + str(dbseconds).zfill(2) + videolink[0:11])

                    # check if filename is already existing and the operations can be skipped
                    filepath = "/var/www/html/grabber/dataframes/"
                    temppath = filepath + "temp"

                    filename = playername.replace(" ",
                                                  "") + "-" + gamenumber + "_" + league + "_" + clubshort + "_" + hometeam + "_vs_" + guestteam + "_" + videolink[0:11]
                    filename2 = filename
                    filename += "_" + actiontype + "-" + subtype + "-Q" + str(dbquarter) + "-" + str(dbminutes).zfill(
                        2) + str(dbseconds).zfill(2)

                    outputfilename = "/var/www/html/grabber/dataframes/"
                    outputfilename += "NF_" + playername.replace(" ", "") + "-" + gamenumber + "_" + league + "_" + clubshort + "_" + hometeam + "_vs_" + guestteam + "_" + videolink[0:11]
                    outputfilename += "_" + actiontype + "-" + subtype + "-Q" + str(dbquarter) + "-" + str(dbminutes).zfill(2) + str(dbseconds).zfill(2) + ".jpg"

                    my_file1 = Path(filepath + '/' + filename + '.mp4')
                    my_file2 = Path(outputfilename)

                    if not (my_file1.is_file()) and not (my_file2.is_file()):
                        # look until the end of file
                        while True:
                            # read frame
                            if debug != 0:
                                print("Framecount: " + str(count))

                            ret, frame = cap.read()
                            # check if frame is empty
                            if not ret:
                                print('Error Reading')
                                count = random.randint(0,150000)
                                nextURL = 0
                                break

                            # save previous results
                            pquarter = fquarter
                            pminutes = fminutes
                            pseconds = fseconds

                            # evaluate the current frame
                            resultarray = evaluate_frame(frame, xtype)
                            fquarter = resultarray[0]
                            fminutes = resultarray[1]
                            fseconds = resultarray[2]
                            xtype = resultarray[3]

                            # check if the evaluation of the current frame is plausible, if not, skip
                            if 1 <= pquarter <= 4 and 0 <= pminutes <= 10 and 0 <= pseconds <= 59 and 1 <= fquarter <= 4 and 0 <= fminutes <= 10 and 0 <= fseconds <= 59:
                                deltaseconds = abs((fquarter * 10 * 60 - fminutes * 60 - fseconds) - (pquarter * 10 * 60 - pminutes * 60 - pseconds))
                                print("Deltaseconds: " + str(deltaseconds))
                                if (abs(resultcode) == 3 and deltaseconds > 5) or (abs(resultcode) == 2 and deltaseconds > 50 or (abs(resultcode) == 1 and deltaseconds > 500)):
                                    print("Result not plausible, skip and try next frame")
                                    fquarter = - 1
                                    fminutes = - 1
                                    fseconds = - 1

                            #print ("Resultarray - Q"+str(fquarter)+"_"+str(fminutes).zfill(2)+":"+str(fseconds).zfill(2)+"_"+str(xtype)+"- Tol: "+str(tol))

                            # evaluation of search strategy
                            #  if fquarter == -1 and fminutes == -1 and fseconds == -1:
                            # if there is an error in any of the found attributes
                            if fquarter == -1 or fminutes == -1 or fseconds == -1:
                                # if previous code existing
                                if resultcode != 0:
                                    if miss3 < 10:
                                        count += 20
                                    else:
                                        count = random.randint(10000,150000)
                                        xtype = 0
                                        # cv2.imwrite("C:/Temp/wamp64/www/" + hometeam + "vs." + guestteam + '.jpg', frame)
                                else:
                                    # if nothing found
                                    count = random.randint(10000,150000)
                                    xtype = 0
                                    # cv2.imwrite("C:/Temp/wamp64/www/" + hometeam + "vs." + guestteam + '.jpg', frame)
                            else:
                                # if found check tolerance make it bigger for sbtv solution
                                if xtype == 1:
                                    tol = 3

                                resultcode = compare_result(fquarter, fminutes, fseconds, dbquarter, dbminutes,
                                                            dbseconds, tol)
                                
                            if debug != 0:
                                print("Frame: " + str(fquarter) + "-" + str(fminutes).zfill(2) + ":" + str(
                                    fseconds).zfill(
                                    2) + "; DB: " + str(dbquarter) + "-" + str(dbminutes).zfill(2) + ":" + str(
                                    dbseconds).zfill(
                                    2) + "; Type: " + str(xtype) + "; RCode: " + str(resultcode) + "; Tol: " + str(tol))

                            if resultcode == -1:
                                # quarter found but target quarter earlier
                                count += random.randint(4700, 4900)
                                miss2 += 1
                            elif resultcode == -2:
                                # quarter correct but target minutes earlier
                                count += random.randint(470, 490)
                                miss2 += 1
                            elif resultcode == -3:
                                # quarter and minutes correct but target seconds earlier
                                count += random.randint(20, 45)
                                miss2 += 1
                            elif resultcode == 1:
                                # quarter found but target quarter later
                                count -= random.randint(4900, 5100)
                                miss2 += 1
                            elif resultcode == 2:
                                # quarter correct but target minutes later
                                count -= random.randint(490, 510)
                                miss2 += 1
                            elif resultcode == 3:
                                # quarter and minutes correct but target seconds later
                                count -= random.randint(10, 50)
                                miss2 += 1
                            elif resultcode == 10:
                                # found

                                # Path(filepath).mkdir(parents=True, exist_ok=True)
                                Path(temppath).mkdir(parents=True, exist_ok=True)

                                # write clipseries
                                clipstart = count - cliplead * 60
                                if clipstart < 0:
                                    clipstart = 0

                                if simulate == 0:

                                    for clipcount in range(clipstart, count + cliptrail * 60):
                                        cap.set(cv2.CAP_PROP_POS_FRAMES, clipcount)
                                        ret, frame = cap.read()
                                        if not ret:
                                            break
                                        else:
                                            cv2.imwrite(temppath + '/' + filename + '_' + str(clipcount).zfill(6) + '.jpg',
                                                        frame)

                                    # summarize all the jpg files in an mp4
                                    # print("output")
                                    ff = ffmpy.FFmpeg(inputs={
                                        temppath + '/' + filename + '_%6d.jpg': '-y -framerate 30 -start_number ' + str(
                                            clipstart).zfill(6)}, outputs={filepath + '/' + filename + '.mp4': None})
                                    ff.cmd
                                    ff.run(stdout=open(os.devnull, 'w'))

                                    # print("Sequence: "+str(sequence))
                                    # if (sequence == 0):
                                    # write title image
                                    # write_titleimage(playername, hometeam + " vs. " + guestteam, "MatchNo: " + gamenumber,
                                    #                 gamedate, filepath, filename2 + "_title", 1280, 720, 1)
                                    # filelist.txt needed for full clipmerger
                                    # f = open('filelist.txt', "w")
                                    # f.write("file '" + filepath + "/" + filename2 + "_title.mp4'\r")
                                    # f.write("file '" + filepath + "/" + filename + "_seg.mp4'\r")
                                    # f.close()
                                    # else:
                                    # #     copyfile(filepath + "/" + filename2 + "_clip.mp4", filepath + "/" + filename2 + "_temp.mp4")
                                    # #     os.remove(filepath + "/" + filename2 + "_clip.mp4")
                                    #     f = open('filelist.txt', "w")
                                    #     f.write("file '" + filepath + "/" + filename2 + "_temp.mp4'\r")
                                    #     f.write("file '" + filepath + "/" + filename + "_seg.mp4'\r")
                                    #     f.close()
                                    # concat
                                    # # first time, just merge the title file into output clip
                                    # ff = ffmpy.FFmpeg(inputs={'filelist.txt': '-y -safe 0 -f concat'}, outputs={filepath + '/' + filename2 + '_clip.mp4': '-c copy'})
                                    # ff.cmd
                                    # ff.run()
                                    # os.remove(filepath + "/" + filename2 + "_temp.mp4")

                                    sequence += 1

                                    fp = os.listdir(temppath)
                                    for item in fp:
                                        if item.endswith(".jpg"):
                                            os.remove(os.path.join(temppath, item))
                                    # os.remove(filepath + '/' + 'out.mp4')
                                    # os.remove(filepath + '/' + 'title.mp4')
                                else:
                                    print("Found. Skipping generation of clip")
                                    
                                nextURL = 0
                                break

                            else:
                                # nothing found
                                count += 10000
                                miss1 += 1

                            # if we have a look on the same elements, we try to make the tolerance bigger
                            if pastcount.count(count) > 6 or miss2 > 200:
                                tol = 2
                            # increase tolerance a 2nd time
                            elif pastcount.count(count) > 8 or miss2 > 250:
                                tol = 5
                            # if >10 then no solution found and trigger break
                            elif pastcount.count(count) > 10:
                                miss2 = 11000

                            # if too many misses
                            if miss1 > 100 or miss2 > 300 or (pastcount.count(count) > 10):
                                # outputfilename += '_M1_' + str(miss1) + '_M2_' + str(miss2) + '_PC_' + str(
                                #    pastcount.count(count))
                                if debug != 0:
                                    print("NOT Found: " + outputfilename)
                                cv2.imwrite(outputfilename, frame)

                            # move forward frames
                            if count < 0:
                                count = 0
                            if debug != 0:
                                print("Count: " + str(count) + " Miss1: " + str(miss1) + " Miss2: " + str(
                                    miss2) + " PC: " + str(pastcount.count(count)))

                            # avoid loops because of stream inconsistencies (ie falsely started matches etc.)
                            pastcount.append(count)

                            if miss1 > 100:
                                nextURL = 1
                                break
                            elif miss2 > 300:
                                nextURL = 0
                                break

                            cap.set(cv2.CAP_PROP_POS_FRAMES, count)

                        # release VideoCapture
                        cap.release()
                    else:
                        print('file already existing... skipping')
                #else:
                    # print("format 22 not available")
        #else:
            # print("info_dict error")
        # print time budget
        # print(datetime.datetime.now() - starttime)
    # else:
        # print("nextURL = 1")

    cv2.destroyAllWindows()
