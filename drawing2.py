import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import unidecode
from bs4 import BeautifulSoup
import datetime
import time
import os


def shortteamname(teamname):
    global colors
    teamname = unidecode.unidecode(teamname)
    for i in colors:
        if teamname.upper().find(i) >= 0:
            # print(teamname.upper(), i)
            return (i)
            break
    # print(teamname.upper(), "N/A")
    return ("N/A")


def drawing(timestamp):
    # drawing
    global d
    global dff
    global leaguevalue
    dff2 = dff.copy()
    # column carrying data
    datacolumn = dff2.columns[3]
    # problem about summing and sorting that does not aggregate all values
    dff2 = dff2[dff2['TimeStamp'] <= timestamp]
    dff2 = dff2.groupby(['PlayerName', 'ClubShort']).sum()
    dff2[datacolumn] = pd.to_numeric(dff2[datacolumn], downcast='integer', errors='coerce')
    dff2 = dff2.sort_values(datacolumn, ascending=False).head(10)
    dff2 = dff2[::-1]
    dff2 = dff2.reset_index()
    #group_lk = dff2.set_index('PlayerName')['ClubShort'].to_dict()

    ax.clear()
    dx = dff2[datacolumn].max() / 200
    for index, row in dff2.iterrows():
        pcolor = colors[shortnames.index(row['ClubShort'])]
        ax.barh(index, row[datacolumn], color = pcolor)
        ax.text(row[datacolumn] - dx, index, row['PlayerName'], size=14, weight=600, ha='right', va='bottom')
        ax.text(row[datacolumn] - dx, index - .25, row['ClubShort'], size=10, color='#444444', ha='right', va='baseline')
        ax.text(row[datacolumn] + dx, index, f'{row[datacolumn]:,.0f}', size=14, ha='left', va='center')
    # polish

    #for i, (value, name) in enumerate(zip(dff2[datacolumn], dff2['PlayerName'])):

    # ... polished styles
    ax.text(1, 0.4, datetime.datetime.fromtimestamp(timestamp).strftime('%d.%m.%y'), transform=ax.transAxes,
            color='#777777', size=46, ha='right', weight=800)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=12)
    ax.set_yticks([])
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-')
    ax.set_axisbelow(True)
    ax.text(0, 1.12, 'Leagues (all phases) :' + leaguevalue,
            transform=ax.transAxes, size=16, weight=600, ha='left')
    ax.text(0, 1.07, 'Aggregated Stats: ' + datacolumn,
            transform=ax.transAxes, size=16, weight=600, ha='left')
    ax.text(1, 0, 'source: Basketplan.ch, Thomas Kohler', size=6, transform=ax.transAxes, ha='right',
            color='#777777', bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
    plt.box(False)
    return (fig, ax)


# main code
origpath = '/var/www/html/grabber/'
destpath = '/var/www/html/grabber/datafiles/'
filelist = [f for f in os.listdir(destpath) if f.endswith(".mp4")]
for f in filelist:
    os.remove(os.path.join(destpath, f))
# variable init

shortnames = ['MARTIGNY', 'LUZERN', 'ARLESHEIM', 'CASSARATE', 'MENDRISIOTTO', 'PRILLY', 'COSSONAY', 'CAROUGE',
              'BLONAY', 'DEL', 'SION', 'BIENNE', 'GOLDCOAST', 'ARBEDO', 'HELIOS', 'MONTHEY', 'VEVEY', 'STARWINGS',
              'VILLARS', 'WINTERTHUR', 'BELLINZONA', 'MEYRIN', 'BADEN', 'BONCOURT', 'MASSAGNO', 'RIVA', 'ELITE',
              'NEUCHATEL', 'NYON', 'CENTRAL', 'TROISTORRENTS', 'LUGANO', 'ZURICH', 'AARAU', 'MORGES', 'COLLOMBEY',
              'FRIBOURG', 'PULLY LAUSANNE', 'PULLY', 'GENEVE', 'BERNEX', 'CHENE', 'AGAUNE', 'RENENS', 'SARINE',
              'KLEINBASEL', 'GC', 'LANCY', 'VAL', 'SOLOTHURN', 'JURA', 'SACONNEX', 'LAVAUX', 'EPALINGES', 'BERN',
              'DIVAC', 'OLTEN', 'STB', 'VACALLO', 'VIGANELLO', 'NONE']

colors = ['orchid', 'dodgerblue', 'indianred', 'royalblue', 'yellow', 'gainsboro', 'tomato', 'green',
          'lightblue', 'gainsboro', 'royalblue', 'yellow', 'tomato', 'yellow', 'lightblue', 'red', 'darkred', 'green',
          'red', 'blue', 'lightblue', 'yellow', 'gainsboro', 'yellow', 'orange', 'red', 'royalblue',
          'green', 'lightblue', 'gainsboro', 'orchid', 'tomato', 'white', 'dodgerblue', 'indianred', 'royalblue',
          'green', 'lightblue', 'gainsboro', 'orchid', 'tomato', 'white', 'dodgerblue', 'indianred', 'royalblue',
          'lightblue', 'gainsboro', 'royalblue', 'yellow', 'tomato', 'yellow', 'lightblue', 'red', 'darkred', 'green',
          'lightblue', 'gainsboro', 'royalblue', 'yellow', 'tomato', 'white']

# load data
d = pd.read_csv(origpath + 'data2.csv', sep=r'\s*,\s*', header=0, encoding='ISO-8859-1', engine='python')
# generate data
listLeague = d['League'].unique()
for leaguevalue in listLeague:
    if (leaguevalue.upper() not in ['xxx']):
        for dcolumn in range(12, 32):
            print(leaguevalue)
            print(dcolumn)
            # select rows that correspond to league - refresh from dff from d to get clean data
            dff = d.copy()
            dff = dff.loc[dff['League'] == leaguevalue]
            # columns 12, 15, 18, 28, 29, 30 to be jumped over (make no sense for aggregation)
            if (dcolumn not in [14, 17, 20, 30, 31, 32]):
                # select cols that are needed to draw
                dff = dff.iloc[:, [2, 4, 5, dcolumn]]
                listTimeStamp = dff['TimeStamp']
                myarray = np.unique(np.asarray(listTimeStamp))
                print(np.count_nonzero(myarray))
                # only produce the graph when there is at least one date
                if np.count_nonzero(myarray) > 0:
                    fig, ax = plt.subplots(figsize=(15, 8))
                    # animation (either on screen or in file)
                    display = 2

                    Writer = animation.writers['ffmpeg']
                    writer = Writer(fps=1)

                    #animate range(mindate,maxdate,24*3600) means to advance by 1 day as the timestamp is in seconds
                    animator = animation.FuncAnimation(fig, drawing, myarray, blit=False, interval=300, repeat=False)
                    if (display == 1):
                        plt.show()
                    else:
                        #filename = destpath + leaguevalue + "-" + str(dcolumn) + "-" + str(counter) +".png"
                        #plt.savefig(filename)
                        filename = destpath + leaguevalue.replace(" ", "") + "-" + str(dcolumn-2) + ".mp4"
                        animator.save(filename, writer=writer)
                    plt.close('all')
