import numpy as np
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
import matplotlib.transforms as mtransforms
from matplotlib.transforms import Affine2D
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import matplotlib.path as mpath
import matplotlib.lines as mlines
import pandas as pd
import os
import time
from statistics import mean
import warnings

warnings.filterwarnings("ignore")


def moving_average(inputarray, n):
    if len(inputarray) < n:
        outputarray = np.array(inputarray)
    else:
        outputarray = np.convolve(inputarray, np.ones((n,)) / n, mode='valid')
        for i in range(0, n - 1):
            outputarray = np.insert(outputarray, 0, 'nan')
    return outputarray


def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles

    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def draw_radar(fig, gs, data, text1, text2):
    N = len(playerData[0])
    theta = radar_factory(N, frame='polygon')
    # start drawing

    spoke_labels = data.pop(0)
    title, case_data = data[0]

    min = np.min(case_data)
    max = np.max(case_data)

    grid = [round(min, 1), round(min + (max - min) / 3 * 1, 1), round(min + (max - min) / 3 * 2, 1),
            round(max, 1)]

    ax = fig.add_subplot(gs[:, 0], projection='radar')
    plt.style.use('default')
    ax.set_rgrids(grid)

    counter = 0
    for d in case_data:
        line = ax.plot(theta, d)
        ax.fill(theta, d, alpha=0.25)
        if counter == 0:
            lcolor = 'dodgerblue'
        else:
            lcolor = 'darkorange'
        for ti, di in zip(theta, d):
            ax.text(ti, di + 0.3, di, color=lcolor, ha='center', va='center')
        ax.scatter(theta, d, color='crimson', s=10)
        counter += 1
    ax.set_varlabels(spoke_labels)

    labels = ('League Average', 'Player Average')
    legend = ax.legend(labels, loc=(0.9, .95),
                       labelspacing=0.1, fontsize='small')

    fig.text(0.01, 0.965, leaguevalue + ': Player Scorecard',
             horizontalalignment='left', color='black', weight='bold',
             size='large')
    fig.text(0.01, 0.945, title,
             horizontalalignment='left', color='black', weight='bold',
             size='medium')
    fig.text(0.01, 0.930, text1,
             horizontalalignment='left', color='black',
             size='small')
    fig.text(0.01, 0.915, text2,
             horizontalalignment='left', color='black',
             size='small')

    # ax.set_title(title, position=(0.5, 1.1), ha='center')


def draw_grid(fig, gs, data):
    patches = []

    ax = fig.add_subplot(gs[:, 1])
    spoke_labels = data.pop(0)
    title, case_data = data[0]

    # set up 5x5 grid
    grid = np.mgrid[0.2:1.1:5j, 0.2:1.1:5j].reshape(2, -1).T

    for x in range(0, len(case_data[0])):
        # color definitions
        gold = '#FFD700'
        silver = '#C0C0C0'
        bronze = '#CD853F'
        green = '#90EE90'
        # add a fancy box
        fancybox = mpatches.FancyBboxPatch(
            grid[x] - [0.023, 0.052], 0.15, 0.15,
            boxstyle=mpatches.BoxStyle("Round", pad=0.02), fc='#646469', ec='#646469')
        patches.append(fancybox)
        fancybox = mpatches.FancyBboxPatch(
            grid[x] - [0.025, 0.05], 0.15, 0.15,
            boxstyle=mpatches.BoxStyle("Round", pad=0.02), fc='#4343de', ec='#4343de')
        patches.append(fancybox)
        if (case_data[2][x] == 1):
            ecolor = gold
            fcolor = gold
        elif (case_data[2][x] == 2):
            fcolor = silver
            ecolor = silver
        elif (case_data[2][x] == 3):
            fcolor = bronze
            ecolor = bronze
        elif (case_data[2][x] <= 10):
            fcolor = green
            ecolor = green
        else:
            ecolor = '#ffffff'
            fcolor = '#ffffff'

        circle = mpatches.Circle(grid[x] - [-0.05, -0.025], 0.08, fc=fcolor, ec=ecolor)
        patches.append(circle)
        # add text
        plt.text(grid[x][0] + 0.05, grid[x][1] + 0.07, spoke_labels[x], ha="center", family='sans-serif', size=10)
        plt.text(grid[x][0] + 0.05, grid[x][1] + 0.035, str(case_data[0][x]) + "/" + str(round(float(case_data[1][x]))),
                 ha="center", family='sans-serif', size=16)
        plt.text(grid[x][0] + 0.05, grid[x][1] + 0.005, 'Rank', ha="center", family='sans-serif', size=10)
        plt.text(grid[x][0] + 0.05, grid[x][1] - 0.03, str(round(float(case_data[2][x]))), ha="center",
                 family='sans-serif', fontweight='bold', size=20)
        collection = PatchCollection(patches, match_original=True)
        ax.add_collection(collection)
        plt.axis('off')
    return patches


def draw_line(fig, gs, pdata):
    # top left - points over season

    ax = fig.add_subplot(gs[0, 2])
    # print(pdata)
    items = len(pdata[0][1][0])
    plt.plot(pdata[0][1][0], pdata[0][2][0], 'bo')
    plt.plot(pdata[0][1][0], pdata[0][2][0], 'b-')
    plt.plot(pdata[0][1][0], pdata[0][5][0], 'b:')
    plt.tick_params(top='off', bottom='off', left='off', right='off', labelleft='on', labelbottom='on')
    # plt.ylabel('Points (2PT, 3PT, FT)', fontsize=10, fontweight='bold')
    plt.xlabel('Date', fontsize=8, fontweight='bold')
    ax.legend(labels=['2PT+3PT+FT', '_2PT+3PT+FT', 'avg'], fontsize=8)
    yint = []
    locs, labels = plt.yticks()
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)
    for label in ax.xaxis.get_ticklabels():
        # label is a Text instance
        label.set_rotation(45)
        label.set_fontsize(9)

    # middle left - Assists / Rebound over season

    ax = fig.add_subplot(gs[1, 2])
    items = len(pdata[0][2][0])
    pdata[0][4][0] = [-x for x in pdata[0][4][0]]
    pdata[0][7][0] = [-x for x in pdata[0][7][0]]
    plt.plot(pdata[0][1][0], pdata[0][3][0], 'ro')
    plt.plot(pdata[0][1][0], pdata[0][3][0], 'r-')
    plt.plot(pdata[0][1][0], pdata[0][6][0], 'r:')
    plt.plot(pdata[0][1][0], pdata[0][4][0], 'go')
    plt.plot(pdata[0][1][0], pdata[0][4][0], 'g-')
    plt.plot(pdata[0][1][0], pdata[0][7][0], 'g:')
    # plt.ylabel('Assists, Rebounds', fontsize=10, fontweight='bold')
    plt.xlabel('Date', fontsize=8, fontweight='bold')
    ax.legend(labels=['AS', '_AS', 'AS avg', 'TR', '_TR', 'TR avg'], fontsize=8)
    yint = []
    locs, labels = plt.yticks()
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)
    for label in ax.xaxis.get_ticklabels():
        # label is a Text instance
        label.set_rotation(45)
        label.set_fontsize(9)

    # ax = fig.add_subplot(gs[2,2])
    # items = len(pdata[0][3][0])
    # plt.ylabel('Rebounds', fontsize=10, fontweight='bold')
    # yint = []
    # locs, labels = plt.yticks()
    # for each in locs:
    #     yint.append(int(each))
    # plt.yticks(yint)
    # for label in ax.xaxis.get_ticklabels():
    #     # label is a Text instance
    #     label.set_rotation(45)
    #     label.set_fontsize(9)


def draw_byminute(fig, gs, resultmatrix, xrcoord, yrcoord, xfcoord, yfcoord):
    # draw livestat charts
    xlabel = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
              26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]

    # first column
    # top right 1 - scores
    ax = fig.add_subplot(gs[0, 3])
    plt.style.use('seaborn-darkgrid')
    # invert failed attempts
    resultmatrix[1] = [-x for x in resultmatrix[1]]
    resultmatrix[3] = [-x for x in resultmatrix[3]]
    resultmatrix[5] = [-x for x in resultmatrix[5]]
    agglist = [resultmatrix[0][i] + resultmatrix[2][i] for i in range(len(resultmatrix[0]))]
    ax.bar(xlabel, resultmatrix[0], color='midnightblue')
    ax.bar(xlabel, resultmatrix[2], bottom=resultmatrix[0], color='royalblue')
    ax.bar(xlabel, resultmatrix[4], bottom=agglist, color='lightsteelblue')
    agglist = [resultmatrix[1][i] + resultmatrix[3][i] for i in range(len(resultmatrix[0]))]
    ax.bar(xlabel, resultmatrix[1], color='midnightblue')
    ax.bar(xlabel, resultmatrix[3], bottom=resultmatrix[1], color='royalblue')
    ax.bar(xlabel, resultmatrix[5], bottom=agglist, color='lightsteelblue')
    # ax.bar(xlabel, c_assist, bottom=c_ft, color='y')
    # ax.set_ylabel('Scores')
    ax.legend(labels=['2PT', '3PT', 'FT', '2PT', '3PT', 'FT'], fontsize=8)
    plt.ylabel('Fail (<0), Success (>0)', fontsize=8, fontweight='bold')
    plt.xlabel('Game Minutes', fontsize=8, fontweight='bold')
    # only integer y axis
    locs, labels = plt.yticks()
    yint = []
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)

    # middle right 1 - assists
    ax = fig.add_subplot(gs[1, 3])
    plt.style.use('seaborn-darkgrid')
    resultmatrix[10] = [-x for x in resultmatrix[10]]
    resultmatrix[11] = [-x for x in resultmatrix[11]]
    ax.bar(xlabel, resultmatrix[8], color='r')
    ax.bar(xlabel, resultmatrix[10], color='g')
    ax.bar(xlabel, resultmatrix[11], bottom=resultmatrix[10], color='darkgreen')
    # ax.set_ylabel('Scores')
    ax.legend(labels=['assists', 'rebounds'], fontsize=8)
    plt.xlabel('Game Minutes', fontsize=8, fontweight='bold')
    # only integer y axis
    locs, labels = plt.yticks()
    yint = []
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)

    # # bottom right 1 - rebounds
    # # invert defensive rebound
    #
    # ax = fig.add_subplot(gs[2, 3])
    # plt.style.use('seaborn-darkgrid')

    # # ax.set_ylabel('Scores')
    # ax.legend(labels=['o reb', 'd reb'], fontsize=8)
    # # only integer y axis
    # locs, labels = plt.yticks()
    # yint = []
    # for each in locs:
    #     yint.append(int(each))
    # plt.yticks(yint)

    # second column
    # top right - fouls
    resultmatrix[8] = [-x for x in resultmatrix[8]]
    ax = fig.add_subplot(gs[2, 2])
    # plt.style.use('seaborn-darkgrid')
    ax.bar(xlabel, resultmatrix[6], color='g')
    ax.bar(xlabel, resultmatrix[8], color='r')
    ax.legend(labels=['foulon', 'foul'], fontsize=8)
    plt.xlabel('Game Minutes', fontsize=8, fontweight='bold')
    # only integer y axis
    locs, labels = plt.yticks()
    yint = []
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)

    # middle right 2 - block, steal, turnover
    ax = fig.add_subplot(gs[2, 3])
    plt.style.use('seaborn-darkgrid')
    resultmatrix[13] = [-x for x in resultmatrix[13]]
    ax.bar(xlabel, resultmatrix[9], color='g')
    ax.bar(xlabel, resultmatrix[12], bottom=resultmatrix[9], color='g')
    ax.bar(xlabel, resultmatrix[13], color='r')
    # ax.set_ylabel('Scores')
    ax.legend(labels=['block', 'steal', 'turnover'], fontsize=8)
    plt.xlabel('Game Minutes', fontsize=8, fontweight='bold')
    # only integer y axis
    locs, labels = plt.yticks()
    yint = []
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)

    # bottom right 2
    # invert figure from positive to negative
    # scatter chart
    img = plt.imread('/var/www/html/grabber/fiba_courtonly.png')
    ax = fig.add_subplot(gs[3:4, 2:])
    # plt.style.use('seaborn-darkgrid')
    ax.imshow(img, origin='upper', extent=(0, 100, 0, 100), interpolation='nearest', aspect='auto')
    ax.scatter(xrcoord, yrcoord, color='g')
    ax.scatter(xfcoord, yfcoord, color='r')
    plt.axis('off')
    # only integer y axis
    # locs, labels = plt.yticks()
    # yint = []
    # for each in locs:
    #     yint.append(int(each))
    # plt.yticks(yint)


# MAIN CODE
print("Starttime: ", time.strftime("%H:%M:%S", time.localtime()))
origpath = '/var/www/html/grabber/'
destpath = '/var/www/html/grabber/datafiles2/'
filelist = [f for f in os.listdir(destpath) if f.endswith(".png")]
for f in filelist:
    os.remove(os.path.join(destpath, f))

# load data
pd.set_option('display.max_columns', None)
d = pd.read_csv(origpath + 'data2.csv', sep=r'\s*,\s*', header=0, encoding='ISO-8859-1', engine='python')
d2 = pd.read_csv(origpath + 'data3.csv', sep=r'\s*,\s*', header=0, encoding='ISO-8859-1', engine='python')
dff = d.copy().assign(like=True)
d2ff = d2.copy().assign(like=1)

# loop over the leagues
listLeague = d['League'].unique()
for leaguevalue in listLeague:
    # exclude leagues if needed
    # if (leaguevalue.upper() not in ['LNBF', 'LNAM', 'LNAF', 'LNBM', 'SUPERCUPM', 'SUPERCUPF']):
    if (leaguevalue.upper() not in ['XXX']):
        print(leaguevalue)
        # create new dataframe + select rows from dataframe of respective league
        dff2 = dff.loc[dff['League'] == leaguevalue]
        dff2 = dff2.dropna(axis=0, subset=['2PT_R', '2PT_T', '3PT_R', '3PT_T', 'FT_R', 'FT_T', 'OR', 'DR', 'TR', 'AS', 'BP', 'INT', 'B', 'FP', 'FPR'])
        #dff2 = dff2.fillna(0)
        #dff2 = dff2.replace('false', 0)
        #print(dff2)
        d2ff2 = d2ff.loc[d2ff['League'] == leaguevalue]
        # print(dff)
        # get a list of all players in that league
        # print(dff2)
        dffx = dff2.copy()
        # print(dff2)
        listplayer = dffx['PlayerName'].unique()
        # print(listplayer)
        # mean over the league
        dff3 = dff2.mean()
        dff4 = dff2.groupby(by=['PlayerName']).mean()
        #print(dff4)
        #print(dff4)
        # define the ranking
        dff4['RK_2PT_R'] = dff4['2PT_R'].rank(ascending=False, method='min')
        dff4['RK_2PT_T'] = dff4['2PT_T'].rank(ascending=False, method='min')
        dff4['RK_3PT_R'] = dff4['3PT_R'].rank(ascending=False, method='min')
        dff4['RK_3PT_T'] = dff4['3PT_T'].rank(ascending=False, method='min')
        dff4['RK_FT_R'] = dff4['FT_R'].rank(ascending=False, method='min')
        dff4['RK_FT_T'] = dff4['FT_T'].rank(ascending=False, method='min')
        dff4['RK_OR'] = dff4['OR'].rank(ascending=False, method='min')
        dff4['RK_DR'] = dff4['DR'].rank(ascending=False, method='min')
        dff4['RK_TR'] = dff4['TR'].rank(ascending=False, method='min')
        dff4['RK_AS'] = dff4['AS'].rank(ascending=False, method='min')
        dff4['RK_BP'] = dff4['BP'].rank(ascending=False, method='min')
        dff4['RK_INT'] = dff4['INT'].rank(ascending=False, method='min')
        dff4['RK_B'] = dff4['B'].rank(ascending=False, method='min')
        dff4['RK_FP'] = dff4['FP'].rank(ascending=False, method='min')
        dff4['RK_FPR'] = dff4['FPR'].rank(ascending=False, method='min')
        # print(dff4)
        # get the max of each category between the players
        dff5 = dff4.max()
        spokes = ['2PT_S', '2PT_T', '3PT_S', '3PT_T', 'FT_S', 'FT_T', 'OR', 'DR', 'AS', 'BP', 'INT', 'B', 'FP',
                  'FPR']

        for index, row in dff4.iterrows():
            # print average performance
            rankPerf = []

            avgPerf = [round(dff3['2PT_R'], 1), round(dff3['2PT_T'], 1), round(dff3['3PT_R'], 1),
                       round(dff3['3PT_T'], 1), round(dff3['FT_R'], 1), round(dff3['FT_T'], 1), round(dff3['OR'], 1),
                       round(dff3['DR'], 1), round(dff3['AS'], 1), round(dff3['BP'], 1),
                       round(dff3['INT'], 1), round(dff3['B'], 1), round(dff3['FP'], 1), round(dff3['FPR'], 1)]
            # print(avgPerf)
            maxPerf = [round(dff5['2PT_R'], 1), round(dff5['2PT_T'], 1), round(dff5['3PT_R'], 1),
                       round(dff5['3PT_T'], 1), round(dff5['FT_R'], 1), round(dff5['FT_T'], 1), round(dff5['OR'], 1),
                       round(dff5['DR'], 1), round(dff5['AS'], 1), round(dff5['BP'], 1),
                       round(dff5['INT'], 1), round(dff5['B'], 1), round(dff5['FP'], 1), round(dff5['FPR'], 1)]
            # print(avgPerf)
            # print player performance
            playerPerf = [round(row['2PT_R'], 1), round(row['2PT_T'], 1), round(row['3PT_R'], 1),
                          round(row['3PT_T'], 1), round(row['FT_R'], 1), round(row['FT_T'], 1), round(row['OR'], 1),
                          round(row['DR'], 1), round(row['AS'], 1), round(row['BP'], 1),
                          round(row['INT'], 1), round(row['B'], 1), round(row['FP'], 1), round(row['FPR'], 1)]
            #print(playerPerf)
            playerRank = [round(row['RK_2PT_R']), round(row['RK_2PT_T']), round(row['RK_3PT_R']),
                          round(row['RK_3PT_T']), round(row['RK_FT_R']), round(row['RK_FT_T']), round(row['RK_OR']),
                          round(row['RK_DR']), round(row['RK_AS']), round(row['RK_BP']),
                          round(row['RK_INT']), round(row['RK_B']), round(row['RK_FP']), round(row['RK_FPR'])]
            dff.set_index(['TimeStamp'])
            dff6 = dff2.loc[dff2['PlayerName'] == index].groupby(by=['TimeStamp']).mean()
            # print(dff6)

            # loop to collect data on points, assists and rebounds

            points = []
            assists = []
            rebounds = []
            timeStamp = []
            for mtStamp, row in dff6.iterrows():
                timeStamp.append(time.strftime("%d.%m", time.localtime(mtStamp)))
                points.append(round((float(row['2PT_R']) * 2 + float(row['3PT_R']) * 3 + float(row['FT_R'])), 1))
                assists.append(round(float(row['AS']), 1))
                rebounds.append(round(float(row['TR']), 1))

            ma_points = np.around(moving_average(points, 3), decimals=1).tolist()
            ma_assists = np.around(moving_average(assists, 3), decimals=1).tolist()
            ma_rebounds = np.around(moving_average(rebounds, 3), decimals=1).tolist()
            playerData = [spokes, (index, [avgPerf, playerPerf])]
            playerData2 = [spokes, (index, [playerPerf, maxPerf, playerRank])]
            playerData3 = [
                (index, [timeStamp], [points], [assists], [rebounds], [ma_points], [ma_assists], [ma_rebounds])]

            # livestats graphics
            # select data for specific player
            d2ff4 = d2ff2.loc[(d2ff2['PlayerName'] == index)]
            d2ff6 = d2ff4.loc[(d2ff4['ActionType'] == '2pt_r') | (d2ff4['ActionType'] == '3pt_r')]
            d2ff7 = d2ff4.loc[(d2ff4['ActionType'] == '2pt_f') | (d2ff4['ActionType'] == '3pt_f')]
            d2ff8 = d2ff4.loc[(d2ff4['ActionType'] == '2pt_r') | (d2ff4['ActionType'] == '3pt_r') | (
                        d2ff4['ActionType'] == '2pt_f') | (d2ff4['ActionType'] == '3pt_f') | (
                                          (d2ff4['ActionType'] == 'substitution') & (
                                              d2ff4['SubType'] == 'in'))].sort_values(by='GameTime', ascending=True)
            # xrcoord = d2ff6['XCoord']
            xrcoord = np.array(d2ff6['XCoord'], dtype=float)
            # yrcoord = d2ff6['YCoord']
            yrcoord = np.array(d2ff6['YCoord'], dtype=float)
            # xfcoord = d2ff7['XCoord']
            xfcoord = np.array(d2ff7['XCoord'], dtype=float)
            # yfcoord = d2ff7['YCoord']
            yfcoord = np.array(d2ff7['YCoord'], dtype=float)
            # print(d2ff4)
            # make pivot table for player with all stats
            d2ff5 = pd.pivot_table(d2ff4, values='like', index=['GameTime'], columns='ActionType',
                                   aggfunc=lambda x: len(x.dropna()), fill_value=0)
            # print(d2ff5)
            resultmatrix = zeros = [[0] * 40 for _ in range(40)]
            for gametime, row in d2ff5.iterrows():
                gametime = int(gametime)
                if '2pt_r' in d2ff5.columns:
                    resultmatrix[0][gametime - 1] = row.loc['2pt_r']
                if '2pt_f' in d2ff5.columns:
                    resultmatrix[1][gametime - 1] = row.loc['2pt_f']
                if '3pt_r' in d2ff5.columns:
                    resultmatrix[2][gametime - 1] = row.loc['3pt_r']
                if '3pt_f' in d2ff5.columns:
                    resultmatrix[3][gametime - 1] = row.loc['3pt_f']
                if 'freethrow_r' in d2ff5.columns:
                    resultmatrix[4][gametime - 1] = row.loc['freethrow_r']
                if 'freethrow_f' in d2ff5.columns:
                    resultmatrix[5][gametime - 1] = row.loc['freethrow_f']
                if 'foulon' in d2ff5.columns:
                    resultmatrix[6][gametime - 1] = row.loc['foulon']
                if 'assist' in d2ff5.columns:
                    resultmatrix[7][gametime - 1] = row.loc['assist']
                if 'foul' in d2ff5.columns:
                    resultmatrix[8][gametime - 1] = row.loc['foul']
                if 'block' in d2ff5.columns:
                    resultmatrix[9][gametime - 1] = row.loc['block']
                if 'OR' in d2ff5.columns:
                    resultmatrix[10][gametime - 1] = row.loc['OR']
                if 'DR' in d2ff5.columns:
                    resultmatrix[11][gametime - 1] = row.loc['DR']
                if 'steal' in d2ff5.columns:
                    resultmatrix[12][gametime - 1] = row.loc['steal']
                if 'turnover' in d2ff5.columns:
                    resultmatrix[13][gametime - 1] = row.loc['turnover']
            # print(resultmatrix)

            # find the time from substitution to first points action
            # print("got here")
            averageActionTimeSuc = []
            averageActionTimeFail = []
            averageActionTimeIn = 0
            text1 = ''
            text2 = ''
            for gametime, row in d2ff8.iterrows():
                gametime = int(gametime)
                # roll through until the first substitution tag is found
                actionType = row.loc['ActionType']
                # print("GameTime: ", row.loc['GameTime'], actionType)
                if (row.loc['ActionType'] == 'substitution'):
                    averageActionTimeIn = row.loc['GameTime']
                    # print("In: ", averageActionTimeIn)
                # once the substitution tag has been found measure the time for first action
                if (averageActionTimeIn > 0):
                    if ((actionType == '2pt_r') | (actionType == '3pt_r')):
                        # print("Out: ", row.loc['GameTime'] - averageActionTimeIn)
                        averageActionTimeSuc.append(row.loc['GameTime'] - averageActionTimeIn)
                        # print(row.loc['PlayerName'], " ", row.loc['TimeStamp'], ", Average Action Time Success: ", averageActionTimeSuc)
                    elif ((actionType == '2pt_f') | (actionType == '3pt_f')):
                        # print("Out: ", row.loc['GameTime'] - averageActionTimeIn)
                        averageActionTimeFail.append(row.loc['GameTime'] - averageActionTimeIn)
                        # print(row.loc['PlayerName'], " ", row.loc['TimeStamp'], ", Average Action Time Fail: ", averageActionTimeFail)
            if ((len(averageActionTimeFail) > 0) and ((len(averageActionTimeSuc) > 0))):
                if (mean(averageActionTimeSuc) > mean(averageActionTimeFail)):
                    text1 = "Average time from start/subst in to first point tentative: " + str(
                        round(float(mean(averageActionTimeFail)), 1)) + " mins"
            if (len(averageActionTimeSuc) > 0):
                text2 = "Average time from start/subst in to first point success: " + str(
                    round(float(mean(averageActionTimeSuc)), 1)) + " mins"

            # size of pic
            fig = plt.figure(figsize=(20, 12))
            # matrix to shape thesize of  subplot areas
            grwidth = [18, 13, 7, 7]
            grheight = [3, 3, 3, 4]
            gs = fig.add_gridspec(ncols=4, nrows=4, width_ratios=grwidth, height_ratios=grheight)
            # theme for line + draw line chart
            plt.style.use('seaborn-darkgrid')

            # theme for line + draw radar chart
            # print (playerData3)
            draw_line(fig, gs, playerData3)

            draw_byminute(fig, gs, resultmatrix, xrcoord, yrcoord, xfcoord, yfcoord)

            # draw radar
            plt.style.use('default')
            #print(playerData)
            draw_radar(fig, gs, playerData, text1, text2)
            # theme for line + draw radar chart
            plt.style.use('seaborn-darkgrid')

            # draw grid
            draw_grid(fig, gs, playerData2)

            # some formatting
            plt.axis('equal')
            plt.axis('off')
            plt.tight_layout()
            # save to file
            filename = destpath + leaguevalue + "-" + index + ".png"
            plt.savefig(filename)
            plt.close('all')

print("Endtime: ", time.strftime("%H:%M:%S", time.localtime()))
