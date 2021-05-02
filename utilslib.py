#
# utilities:
#  formatTime()
#  formatTimeLabels()
#  findIfDST()
#  putID()
#  saveFig()
# <- Last updated: Sat May  1 20:39:23 2021 -> SGK
#
from datetime import datetime
import sys, os
#
# ------------------------------------------------------------------------
# format time t (in min) to HH:MM:SS or MM:SS.S
def formatTime(t):
    """
    str = formatTime(t)
      t    - input value, in minutes
      str - returns a HH:MM:SS or MM:SS.S string representing time, t
    
    """
    if t > 10:
        h = int(t)//60
        m = round(t%60)
        s = round((t - m - h*60)/60)
        str = '{:02d}:{:02d}:{:02d}'.format(h, m, s)
    else:
        m = int(t)
        s = (t-m)*60
        ms = round((s - int(s))*10)
        s = int(s)
        str = '{:02d}:{:02d}.{:01d}'.format(m, s, ms)
    return str
#
# ------------------------------------------------------------------------
# format ticks from minutes to HH:MM
def formatTimeLabels(t, pos):
    """
    used to format x ticks as HH:MM
    """
    h = int(t)//60
    m = round(t%60)
    return '{:02d}:{:02d}'.format(h, m)
#
# ------------------------------------------------------------------------
# find out if tz (Unix epoch time) corresponds to DST in US
def findIfDST(tz):
    """
    return True or False if it is DST for tz (Unix epoch) in the US 
    """
    #
    # grabbed from
    # https://en.wikipedia.org/wiki/Daylight_saving_time_in_the_United_States
    dstInfo = {}
    dstInfo[2015] = 'March 8:November 1'
    dstInfo[2016] = 'March 13:November 6'
    dstInfo[2017] = 'March 12:November 5'
    dstInfo[2018] = 'March 11:November 4'
    dstInfo[2019] = 'March 10:November 3'
    dstInfo[2020] = 'March 8:November 1'
    dstInfo[2021] = 'March 14:November 7'
    dstInfo[2022] = 'March 13:November 6'
    dstInfo[2023] = 'March 12:November 5'
    dstInfo[2024] = 'March 10:November 3'
    dstInfo[2025] = 'March 9:November 2'
    dstInfo[2026] = 'March 8:November 1'
    dstInfo[2027] = 'March 14:November 7'
    dstInfo[2028] = 'March 12:November 5'
    dstInfo[2029] = 'March 11:November 4'
    #
    # what year
    dateTime = datetime.fromtimestamp(tz)
    year = dateTime.year
    #
    # get the DST limits
    (t0,t1) = dstInfo[year].split(':')
    t0 += ' '+str(year)
    t1 += ' '+str(year)
    #
    # convert to Unix epoch time (sec since 1970)
    timeFormat = '%B %d %Y'
    tFr = datetime.strptime(t0, timeFormat).timestamp()
    tTo = datetime.strptime(t1, timeFormat).timestamp()
    #
    # simple test if inside DST limits
    if (tz > tFr and tz < tTo):
        isDST = True
    else:
        isDST = False
    #
    ### print ('>>', dstInfo[year], isDST)
    #
    return isDST;
#
# ------------------------------------------------------------------------
# put an identifier on a figure
def putID(plt):
    """
    draw an identifier string on the lower left of the figure as follows:
      date user@host (full-path-to-script)
    """
    #
    # get the script name
    string = sys.argv[0]
    # add the full path
    if not string.startswith('/'):
        string = os.getcwd() + '/' + string
    # get the time now -> string
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    # add user and host name
    string = now+' '                            + \
        os.environ.get('USER', 'nobody')        + \
        '@'+os.environ.get('HOSTNAME', 'undef') + \
        ' ('+string+')'
    # put the text in the lower left of the 'paper'
    #  need a coord translation to paper units
    transform = plt.gcf().transFigure
    # lower left, small font
    plt.text(0.025, 0.025, string, transform=transform, fontsize=6)
#
# ------------------------------------------------------------------------
#
# save the figure to a file
def saveFig(fig, plotType,
            name = 'myplot'):
    """
    save the figure to a file of given type
      filename = name-USER.plotType

      plotType can be 'pdf',  'png' or any extention accepted by
      matplolib.savefig()
    """
    #
    saveFn = name + '-' + os.environ.get('USER', 'nobody') + '.'+plotType
    fig.savefig(saveFn)
    print (name+": plot saved in '"+saveFn+"'")
