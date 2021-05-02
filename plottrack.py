#
# plot the track and its properties
#  getGMapImage()
#  doPlot()
# <- Last updated: Sat May  1 17:11:20 2021 -> SGK
#
import numpy as np
from math import cos,sin,atan,pi,sqrt
#
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
#
# extra function from my .py files
from utilslib import formatTime, formatTimeLabels, putID, saveFig
from dlsq_fit import dlsq_fit
#
# ------------------------------------------------------------------------
# get the Google Map image
# return the image and its boundaries (in miles)
def getGMapImage(useRoad,
                 lonRef = -71.3646464, # some lon/lat ref locations
                 latRef =  42.4358983):  
    """
    read a screen shot of a google map and return it as an image
      plus the bounding box of the image in miles wrt to a ref lat/lon

      useRoad is True then read gmap-road.jpg
                 False          gmap-satellite.jpg
       both jpg must be in the cwd

    I saved such a pair of images using a screen shot of google map, 
      and calibrated it to get lon/lat at two positions
      to derive the image scaling by dropping two markers,
      saving these two extra images and measuring the markers 
      location in pixel units.

    This is set for an area where I go biking
      you can do the same to customize this for a different area.
    """
    #
    # grabbed a map and two known coords at zoom = 12
    ## https://www.google.com/maps/@42.4358983,-71.3646464,12z
    ## (latRef, lonRef) = (42.4358983, -71.3646464)
    #
    if useRoad:
        ## 1510 x 864, x/y pos of two markers
        gmapImage = plt.imread("gmap-road.jpg")
        (xps1, yps1) = ( 132.5, 740.5)
        (xps2, yps2) = (1326.5, 117.5)
        marker = '.b'
        color = 'red'
    else:
        ## 1514 x 867, x/y pos of two markers
        gmapImage = plt.imread("gmap-satellite.jpg")
        (xps1, yps1) = ( 132.5, 740.5+4)
        (xps2, yps2) = (1326.5, 117.5+4)
        marker = '.y'
        color = 'yellow'
    #
    # lon/lat of these two markers
    (lat1, lon1) = (42.523128, -71.579051)
    (lat2, lon2) = (42.365291, -71.169124)
    #
    # cut/trim this image to remove ugly bits from the screen shot
    (h, w, d)    = gmapImage.shape
    (xcut, xtrm) = ( 0, 0)
    (ycut, ytrm) = (65, 0)
    xps1 -= xcut
    xps2 -= xcut
    yps1 -= ytrm
    yps2 -= ytrm
    xmax  = w-xtrm
    ymax  = h-ytrm
    gmapImage = gmapImage[ycut:ymax, xcut:xmax, :]
    (imageHeight, imageWidth, imageDepth) = gmapImage.shape
    #
    # conversion factors
    deg2rad  = pi/180.0
    km2mi    = 0.621371  # km to mi
    #
    # convert to miles
    earthRad = 6367.449  # km
    earthRad *= km2mi    # mi
    # some simple spherical trig
    earthRho = earthRad*cos(latRef*deg2rad)
    #
    xVal1 = earthRho*atan((lon1-lonRef)*deg2rad)
    yVal1 = earthRad*atan((lat1-latRef)*deg2rad)
    #
    xVal2 = earthRho*atan((lon2-lonRef)*deg2rad)
    yVal2 = earthRad*atan((lat2-latRef)*deg2rad)
    #
    # get the x scaling xV = xOff + xScl * xP
    xScl = (xVal2-xVal1)/(xps2-xps1)
    xOff = xVal2 - xps2*xScl
    #
    # get the y scaling yV = yOff + yScl * yP
    yScl = (yVal2-yVal1)/(yps2-yps1)
    yOff = yVal2 - yps2*yScl
    #
    # boundingbox in miles relative to ref lat/lon
    xMin = xOff                    
    yMin = yOff                    
    xMax = xOff + xScl*imageWidth
    yMax = yOff + yScl*imageHeight
    #
    # return needed vars
    return (gmapImage, xMin, xMax, yMin, yMax, marker, color)
#
# ------------------------------------------------------------------------
# plot the track
def doPlot(data, infos, stats,
           plotType = 'pdf',      # type of plot
           noRoute  = False,      # don't show route
           useRoad  = False,      # overplot on road or satellite image
           plotVS   = 'Time',     # props vs time or distance
           plotSize = (12, 8),    # size of plot windows
           velMin   = 6.0,        # define when moving etc
           velMax   = 100.0,
           cadMin   = 50):
    """
    plot the data
      fig1: route on top of a map or using google map -> html
      fig2: ride properties vs time or distance

      plotType     type of plot like 'pdf' or 'x'
      noRoute      don't show route if True
      useRoad      overplot on road (True) or satellite image (False)
      plotVS       props vs time or distance
      plotSize     size of plot windows
      velMin       define when moving, etc
      velMax       
      cadMin   
    """
    #
    # decode infos -> index[] and units[]
    nCols, nLines = data.shape
    index = {}
    units = {}
    i = 0
    for wx in infos.split():
        w = wx.split(':')
        index[w[0]] = i
        units[w[0]] = w[1]
        i += 1
    #
    # get the stats
    avgMVel = stats['avgMVel']
    maxMVel = stats['maxMVel']
    avgHR   = stats['avgHeartRate']
    maxHR   = stats['maxHeartRate']
    avgCad  = stats['avgCadence']
    maxCad  = stats['maxCadence']
    #
    # find the max(running mean moving velocity)
    ix = index['MeanMVel']
    mxxVel = max(data[ix, :])
    #
    # reject NaN postn values
    ix = index['XPosition']
    iy = index['YPosition']
    mask1 = np.logical_not(np.isnan(data[ix, :]))
    mask2 = np.logical_not(np.isnan(data[iy, :]))
    mask0 = mask1 & mask2
    #
    # reject velocities outside [velMin, velMax]
    iv = index['Velocity']
    mask1 = data[iv, :] > velMin
    mask2 = data[iv, :] < velMax
    #
    # final mask
    mask = mask0 & mask1 & mask2 ## & mask3
    #
    fmtStr = 'Started {}\n' + \
        'Time total {}, moving {}, paused {}\n' + \
        'Distance traveled total {:.1f}, moving {:.1f} mi\n' + \
        'Minimun moving velocity {:.1f} mph'
    str = fmtStr.format(stats['startTime'],
                        formatTime(stats['totalTime']),
                        formatTime(stats['movingTime']),
                        formatTime(stats['totalTime']- stats['movingTime']),
                        stats['distance'],  stats['mvgDistance'], velMin)
    #  
    if not noRoute:
        #
        # draw first figure, unless noRoute is True
        fig1 = plt.figure(figsize = plotSize)
        #
        # get x/y position arrays of the ride
        ix = index['XPosition']
        iy = index['YPosition']
        xPos = data[ix, mask]
        yPos = data[iy, mask]
        #
        # get the Google map and its bounding box (in miles)
        #  plus which marker and color to use
        (gmapImage, xMin, xMax, yMin, yMax, \
         marker, color) = getGMapImage(useRoad)
        #
        # display the image
        plt.imshow(gmapImage, extent=[xMin, xMax, yMin, yMax])
        #
        ## mark the border
        ## plt.plot([xMin,xMax], [yMin, yMax], '.b')
        # plot the route w/ set markers
        plt.plot(xPos, yPos, marker, markersize= 1.0 )
        # title and labels
        plt.title('Route')
        plt.xlabel('x-position [mi]')
        plt.ylabel('y-position [mi]')
        # add some text
        xx = xMin+0.5
        yy = yMax-0.5
        #
        fmtStr = '\nVelocity average {:6.2f} max {:6.2f} mph\n' + \
            'Cadence average {:6.2f} max {:6.2f} rpm\n' + \
            'HR average {:6.2f} max {:6.2f} bpm'
        strX = str + fmtStr.format(avgMVel, maxMVel,
                                   avgCad,  maxCad,
                                   avgHR,   maxHR)
        plt.text(xx, yy, strX, color = color, va = 'top')
        #
        # add an ID on fig1 if not plotting on screen
        if not ((plotType == 'x') or (plotType == 'w')):
            putID(plt)
    #
    # draw second figure
    fig2 = plt.figure(figsize = plotSize)
    #
    # what to plot?
    #  specify Var1-Var2
    if (plotVS == 'Time'):
        plotList = 'Time-Velocity Time-HeartRate Time-Altitude ' + \
            'Time-Cadence Time-Grade Grade-Velocity'
    else:
        plotList = 'MovingDistance-Velocity MovingDistance-HeartRate ' + \
            'MovingDistance-Altitude ' + \
            'MovingDistance-Cadence MovingDistance-Grade Grade-Velocity'
    #
    # init frame index
    k = 1
    # loop on plot list, broken at spaces
    for p in plotList.split():
        v = p.split('-')
        #
        # index for variables
        ix = index[v[0]]
        iy = index[v[1]]
        #
        # set the subplot on a 3x2 grid
        ax = plt.subplot(3, 2, k)
        #
        # do not plot low cadence values
        if (v[1] == 'Cadence'):
            m = data[iy, :] > cadMin
            m = m & mask
        else:
            m = mask
        #
        # plot the data, using small dot (pixel) as marker
        ax.plot(data[ix, m], data[iy, m], ',')
        #
        # if vs time, use my tick labels
        #  and set the x-label
        if (v[0] == 'Time'):
            ax.xaxis.set_major_formatter(FuncFormatter(formatTimeLabels))
            plt.xlabel(v[0]+' [hh:mm]')
        else:
            plt.xlabel(v[0]+' ['+units[v[0]]+']')
        #
        # set y-label and title
        plt.ylabel('['+units[v[1]]+']')
        plt.title(v[1])
        #
        # set xp/yp as min/max of x/y
        xp = np.empty(2)
        yp = np.empty(2)
        xp[0] = min(data[ix, mask])
        xp[1] = max(data[ix, mask])
        #
        # add'l stuff depending on which var is being plotted
        if (v[0] == 'Grade'):
            #
            # if plot vs grade, add a linear fit
            (n, c) = dlsq_fit(data[ix, m], data[iy, m])
            yp[0] = c[0] + c[1]*xp[0]
            yp[1] = c[0] + c[1]*xp[1]
            # draw the lin fit, w/ a green dot-dashed line
            plt.plot(xp, yp, '-.g')
            #
            # where to put text, assume v[1] is velocity
            xx = xp[0]
            yy = min(data[iy, m])
            plt.text(xx, yy, '{:.1f} mph/10%'.format(c[1]*10),color='g')
        #
        else:
            if (v[1] == 'Velocity'):
                #
                # draw line at avg moving velocity
                yp[0] = avgMVel
                yp[1] = avgMVel 
                plt.plot(xp, yp, '-.r')
                # draw the up-to-then mean moving velocity, in green
                ix = index[v[0]]
                iy = index['MeanMVel']
                plt.plot(data[ix, mask], data[iy, mask], color='g')
                #
                # add the avg mvg vel, max(mean mvg vel) and max(vel)
                #   in red, green and blue
                xx = xp[0]
                yy = avgMVel+1
                plt.text(xx, yy, '{:.1f}'.format(avgMVel), color = 'r')
                #
                xx = -(xp[1]-xp[0])*.05 + xp[1]
                yy = maxMVel-4
                plt.text(xx, yy, '{:.1f}'.format(maxMVel), color = 'b')
                #
                yy = mxxVel+1
                plt.text(xx, yy, '{:.1f}'.format(mxxVel), color = 'g')
                #
            if (v[1] == 'HeartRate'):
                #
                # draw line at avg HR 
                yp[0] = avgHR
                yp[1] = avgHR 
                plt.plot(xp, yp, '-.r')
                #
                # add the avg and max HR in red and blue
                xx = xp[0]
                yy = avgHR+2
                plt.text(xx, yy, '{:.1f}'.format(avgHR), color = 'r')
                #
                xx = -(xp[1]-xp[0])*.075 + xp[1]
                yy = maxHR-8
                plt.text(xx, yy, '{:.1f}'.format(maxHR), color = 'b')
                #
            if (v[1] == 'Cadence'):
                #
                # draw line at avg cadence
                yp[0] = avgCad
                yp[1] = avgCad 
                plt.plot(xp, yp, '-.r')
                #
                # add avg and max cadence in red and blue
                xx = xp[0]
                yy = avgCad+5
                plt.text(xx, yy, '{:.1f}'.format(avgCad), color = 'r')
                #
                xx = -(xp[1]-xp[0])*.075 + xp[1]
                yy = maxCad-20
                plt.text(xx, yy, '{:.1f}'.format(maxCad), color = 'b')
        #
        # next one
        k += 1
    #
    # done, add the string str to last frame
    #  alignmt is va == vert aligmt set to 'top'
    xx = min(data[ix, mask])
    yy = max(data[iy, mask])
    plt.text(xx, yy, str, fontsize = 6, va = 'top')
    #
    # use tight layout
    fig2.tight_layout()
    #
    # either show the plot
    if (plotType == 'x') or (plotType == 'w'):
        plt.show()
    # or save it to a file (pdf or png)
    else:
        # add the ID to the 2nd fig
        putID(plt)
        # save them to two files (unless noRoute == True)
        if not noRoute:
            saveFig(fig1, plotType, name='route')
        saveFig(fig2, plotType, name='stats')
