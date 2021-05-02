#
# track lib: read and process a TCX file
#  readTrack()
#  processTrack()
# <- Last updated: Sun May  2 15:11:00 2021 -> SGK
#
import re
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from datetime import datetime
from math import cos,sin,atan,pi,sqrt
#
# get some of my utiliies
from utilslib import formatTime, findIfDST
#
# ---------------------------------------------------------------------------
# read a TCX file, using xml.etree.ElementTree to parse the xml
#   found how to do this by googling
def readTrack(fn,
              silent = False):
    """
    read a TCX file (fn) and returns a Data Frame (pandas)
    """
    #
    # data array of values
    data = []
    if not silent:
        print('reading', fn)
    #
    with open(fn) as xml_file:
        # get the xml string
        xml_str = xml_file.read()
        #
        # do some parsing
        xml_str = re.sub(' xmlns="[^"]+"', '', xml_str, count=1)
        root = ET.fromstring(xml_str)
        activities = root.findall('.//Activity')
        for activity in activities:
            # assume that tha activity is biking
            ## print('-- {} --'.format(activity.attrib['Sport']))
            #
            # get the tracking points
            tracking_points = activity.findall('.//Trackpoint')
            # loop on them
            for tracking_point in list(tracking_points):
                children = list(tracking_point)
                ## str was to help debugging this
                ## str = ''
                # get this point values
                vals = {}
                for i in children:
                    #
                    # position -> lat/lon
                    if i.tag == 'Position':
                        for c in list(i):
                            ## str += c.tag+'='+c.text+' '
                            vals[c.tag] = c.text
                    #
                    # HR, need to get the value
                    elif i.tag == 'HeartRateBpm':
                        for c in list(i):
                            ## str += 'HR='+c.text+' '
                            vals['HeartRateBpm'] = c.text
                    #
                    # other info line cadence
                    else:
                        ## str += i.tag+'='+i.text+' '
                        vals[i.tag] = i.text
                        ## print(str)
                    data.append(vals)
    #
    ## print('data read')
    # stuff it in a pandas DataFrame
    df = pd.DataFrame(data)
    #
    # return that data frame
    return (df)
#
# ------------------------------------------------------------------------
# process (analyze) the track, passed as a data frame
#   return a numpy data array,
#         with info (which column hold what var and units)
#         and the stats
def processTrack(trackDF,
                 useTable = False, # print stats as a table
                 velMin =  6.0,    # min vel to be moving [mph]
                 velMax = 50.0,    # max valid velocity
                 grdMax = 15.0,    # max valid grade
                 cadMin = 10,      # min cadence for stats
                 hrMin  = 50,      # min HR      for stats
                 lonRef = -71.3646464, # some lon/lat ref locations
                 latRef =  42.4358983,
                 silent = False):
    """
    process/analyze the track, return a data array and print some stats
        as read in the trackDF data frame
    options:
        useTable    print stats as a table if True
        velMin      min vel to be moving [mph]
        velMax      max valid velocity
        grdMax      max valid abs(grade)
        cadMin      min cadence for stats
        hrMin       min HR      for stats
        lonRef = -71.3646464    # some lon/lat ref locations
        latRef =  42.4358983
    """
    #
    # format of time stamps
    timeFormat = '%Y-%m-%dT%H:%M:%S'
    #
    # start time, convert to Unix time (seconds elaspsed since 1970)
    t0 = trackDF['Time'][0]
    # adjust time stamp format for diff TCX
    if ('Z' in t0):
        timeFormat += 'Z'
        tz = datetime.strptime(t0, timeFormat).timestamp()
    elif ('+00:00' in t0):
        timeFormat += '+00:00'
        tz = datetime.strptime(t0, timeFormat).timestamp()
    else:
        tz = datetime.strptime(t0, timeFormat).timestamp()
    #
    # how many lines and columns
    nLines = len(trackDF)
    nCols  = 20
    # create an empy numpy array
    data   = np.empty((nCols, nLines))
    #
    # some constants and conversion factors
    earthRad = 6367.449 # km
    deg2rad  = pi/180.0
    km2mi    = 0.621371
    mtr2feet = 3.28084
    #
    # initialize some accumulators
    distance    = 0.0
    mvgDistance = 0.0
    mvgTime     = 0.0
    vsum        = 0.0
    nsum        = 0
    #
    velMinKmh = velMin/km2mi
    #
    # loop on the lines of the data frame
    for i in range(nLines):
        # time
        tt = trackDF['Time'][i]
        t0 = datetime.strptime(tt, timeFormat).timestamp()
        #
        data[0, i] = (t0 - tz)/3600.                  # delta t
        data[1, i] = float(trackDF['LongitudeDegrees'][i]) # lon
        data[2, i] = float(trackDF['LatitudeDegrees'][i])  # lat
        #
        # alt, hr, cad if present and valid
        try:
            alt = float(trackDF['AltitudeMeters'][i])
        except:
            alt = 0.0
        try:
            hr  = float(trackDF['HeartRateBpm'][i])
        except:
            hr  = 0.0
        try:
            cad = float(trackDF['Cadence'][i])
        except:
            cad = 0.0
        #
        # minor radius correction, alt is in meters
        rad = earthRad + alt/1000.0
        #
        # ii is prev pt, ii=0 for i=0
        if i == 0:
            ii = 0
            rdx = rad*cos(data[2, i]*deg2rad) # rho = rad*cos(lat)
        else:
            ii = i-1
        # x,y positions in km
        #
        xpos = rdx * atan( (data[1, i]-lonRef)*deg2rad )
        ypos = rad * atan( (data[2, i]-latRef)*deg2rad )
        #
        dx = rdx * atan( (data[1, i]-data[1, ii])*deg2rad )
        dy = rad * atan( (data[2, i]-data[2, ii])*deg2rad )
        #
        delta_dist = sqrt(dx**2+dy**2)          # in km
        delta_time = (data[0, i] - data[0, ii]) # in hr
        if (delta_time > 0):
            velocity = delta_dist/delta_time    # km/h
        else:
            velocity = 0
        # grade, remember alt is in meter
        if (delta_dist > 0) and not np.isnan(delta_dist):
            grade = (alt - data[3, ii])/(delta_dist*1000.0)*100 # [%]
            # ignore crazy grades
            if (grade > grdMax) or (grade < -grdMax):
                grade = 0
        else:
            grade = 0
        #
        # save the values
        data[3, i] = alt
        data[4, i] = hr
        data[5, i] = cad
        data[6, i] = xpos
        data[7, i] = ypos
        data[8, i] = dx
        data[9, i] = dy
        #
        data[10, i] = delta_dist 
        data[11, i] = delta_time
        data[12, i] = velocity 
        data[13, i] = grade
        #
        # accumulate traveled disk
        if not np.isnan(delta_dist):
            distance += delta_dist
        #
        # accumuate moving time and dist and sum(veloc)
        if (velocity > velMinKmh):
            mvgDistance += delta_dist
            mvgTime     += delta_time*3600. # back in sec
            vsum += velocity
            nsum += 1
        #
        # compute the mean avg velocity so far
        if (nsum > 1):
            meanMVel = vsum/nsum
            # set it to be at least to velMin at begining
            if meanMVel < velMinKmh:
                meanMVel = velMinKmh
        else:
            meanMVel = velMinKmh
        #
        # more vars
        data[14, i] = meanMVel
        data[15, i] = distance 
        data[16, i] = mvgDistance 
        data[17, i] = mvgTime 
    #
    # convert data to minutes, mph, feet
    data[ 0, :] *= 60.0
    data[ 3, :] *= mtr2feet
    #
    data[ 6, :] *= km2mi
    data[ 7, :] *= km2mi
    data[ 8, :] *= km2mi
    data[ 9, :] *= km2mi
    #
    data[11, :] *= 60.0
    data[12, :] *= km2mi
    data[14, :] *= km2mi
    data[15, :] *= km2mi
    data[16, :] *= km2mi
    data[17, :] *= 60.0
    #
    totalTime    = data[0, -1]
    mvgTime     /= 60.0
    distance    *= km2mi
    mvgDistance *= km2mi
    #
    if not silent:
        print('data decoded')
    #
    # saves which col is what:unit as a space sep string
    infos = 'Time:min Longitude:o Latitude:o Altitude:ft ' + \
              'HeartRate:bpm Cadence:rpm ' + \
              'XPosition:x YPosition:y DeltaXPos:x DeltaYPos:y ' + \
              'DeltaDist:d DeltaTime:min ' + \
              'Velocity:mph Grade:% MeanMVel:mph' + \
              'Distance:mi MovingDistance:mi MovingTime:min '
    #
    # covert infos -> index[] and units[]
    index = {}
    units = {}
    i = 0
    for wx in infos.split():
        w = wx.split(':')
        index[w[0]] = i
        units[w[0]] = w[1]
        i += 1
    #
    # compute some more stats, properly masked
    mask1 = data[index['Velocity'],  :] > velMin
    mask2 = data[index['Velocity'],  :] < velMax
    mask3 = data[index['HeartRate'], :] > hrMin
    mask4 = data[index['Cadence'],   :] > cadMin
    #
    # moving vel stats
    mask    = mask1 & mask2
    avgMVel = sum(data[index['Velocity'],  mask])/sum(mask)
    maxMVel = max(data[index['Velocity'],  mask])
    #
    # HR stats
    mask    = mask1 & mask2 & mask3
    sumMask = sum(mask)
    if (sumMask > 0):
        avgHR   = sum(data[index['HeartRate'], mask])/sumMask
        maxHR   = max(data[index['HeartRate'], mask])
    else:
        avgHR = 0.0
        maxHR = 0.0
    #
    # cadence stats
    mask    = mask1 & mask2 & mask4
    sumMask = sum(mask)
    if (sumMask > 0):
        avgCad  = sum(data[index['Cadence'],   mask])/sumMask
        maxCad  = max(data[index['Cadence'],   mask])
    else:
        avgCad = 0.0
        maxCad = 0.0
        #
    #
    # are we in DST?
    isDST = findIfDST(tz);
    # convert time to EST or EDT
    if isDST:
        tz -= 4*3600
        xtz = ' EDT'
    else:
        tz -= 5*3600
        xtz = ' EST'
    #
    # tz -> string representing time
    tz = str(datetime.fromtimestamp(tz))+xtz
    #
    stats = {}
    stats['startTime']    = tz
    stats['totalTime']    = totalTime
    stats['movingTime']   = mvgTime
    stats['distance']     = distance
    stats['mvgDistance']  = mvgDistance
    stats['avgMVel']      = avgMVel
    stats['maxMVel']      = maxMVel
    stats['avgHeartRate'] = avgHR
    stats['maxHeartRate'] = maxHR
    stats['avgCadence']   = avgCad
    stats['maxCadence']   = maxCad
    #
    # print ride stats
    if useTable:
        fmtStr = '{} {:8s} {:8s} {:7s} ' + \
            '{:6.2f} {:6.2f} {:6.2f} {:6.2f} '   + \
            '{:6.2f} {:6.2f} {:6.2f} {:6.2f} ' 
        print(fmtStr.format(tz,
                            formatTime(totalTime),
                            formatTime(mvgTime),
                            formatTime(totalTime-mvgTime),
                            distance, mvgDistance,
                            avgMVel, maxMVel,
                            avgCad, maxCad,
                            avgHR, maxHR))
        
    else:
        fmtStr = 'moving velocity range: [{:.2f}, {:.2f}] mph'
        print(fmtStr.format(velMin, velMax))
        fmtStr = 'Started  {}'
        print(fmtStr.format(tz))
        #
        fmtStr = 'Time     total={} moving={} paused={}'
        print(fmtStr.format(formatTime(totalTime),
                            formatTime(mvgTime),
                            formatTime(totalTime-mvgTime)))
        fmtStr = 'Distance total={:6.2f} moving={:6.2f} mi'
        print(fmtStr.format(distance, mvgDistance))
        fmtStr = 'Velocity average={:6.2f} max={:6.2f} mph'
        print(fmtStr.format(avgMVel, maxMVel))
        fmtStr = 'Cadence  average={:6.2f} max={:6.2f} rpm'
        print(fmtStr.format(avgCad, maxCad))
        fmtStr = 'HR       average={:6.2f} max={:6.2f} bpm'
        print(fmtStr.format(avgHR, maxHR))
    #
    # return data, infos and stats
    return (data, infos, stats)
