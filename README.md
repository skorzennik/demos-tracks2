# demos-tracks2

Simple demo script to process a TCX (biking) track. (TCX stands for Training
Center XML).

This was an excise to practice/learn coding in Python (can't really call it
programming - LOL.)

The main script `process-tcx.py` will read a TCX file, compute some of the ride
statistics and plot the route on top of a static map taken from a Google Map
screen-shot (in fact two, one in road mode, one in satellite mode). 

The other `.py` files are the needed libraries (aka modules) used by the main
script.

I tested it on TCX files downloaded from RideWithGPS and MapMyRide. Most of
them include heart rate and cadence information as well as GPS info. 

The script can also plot the route in a Google Map using the `gmplot` module and
produce an `html` file.

If you have a Google Cloud api key, store it in a APIKEY env. var, otherwise
Google Map will add a watermark.

It works fine with Python v3.7 or higher and needs the `gmplot` module as well
as the usual/typical other ones (`numpy`, `matplotlib`, etc). It has been run
under Linux (CentOS 7.x) w/ v3.7 and under Windows 10 w/ v3.9 - sorry I do not
do MacOS. You can install the `gmplot` module with `pip install gmplot` or
`pip install --user gmplot` if you don't get elevated privileges on your
machine (i.e. you can't become root).

I ran it on 182 TCX files and got a few errors (4 or 5), most likely when some
properties are all invalid and I divide by `sum(mask)` that is 0. This might
get fixed in a later version, and I will look into getting the background map
dynamically and better handling such maps. I may also change the plots layout.

This was done for fun and to motivate an old dog to learn new tricks - so caveat emptor.

```
Usage:
    python process-tcx.py [opts] filename

    opts: 
      -useTable                format of stats
      -vsTime|-vsDistance      type of plot
      -useSatellite|-useRoad   type of route bgd map
      -noRoute                 no route figure
      -vmin v                  set velMin to v
      -vmax v                  set velMax to v
      -hrmin h                 set hrMin to h
      -cmin                    c set cadMin to c
      -|gmap|-pdf|-png|-x|-w   type of plot (none, gmap, pdf, png, X, or Windows
    or

    python process-tcx.py
```
    and answer prompts

 I include a few TCX files, the background Google Maps and some examples of outputs

```
   210225.tcx            - test TCX files
   210418.tcx
   210427.tcx
   210501.tcx
   210502.tcx

   gmap-road.jpg         - background map for route
   gmap-satellite.jpg

   stats-210418.png      - output from processing 210418.tcx
   route-210418.png

   stats-210501.png
   route-210501.png
   route-210501-satellite.png

   stats-210502.png
   route-210502.png

   gmap.html             - overplot on Google Map
```

  It is relatively easy to customize the background Google Map for an different
area, see comments in `getGMapImage()` defined in `plottrack.py`

<- Last updated: Sun May  2 15:49:39 2021 -> SGK
