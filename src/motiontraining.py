#!/usr/bin/python

from SimpleCV import *
import os
import numpy
import pygame
import time
from vlctelnet import *
from colortracker import *
from drawgraph import *

################################################
img_expiration = 1
dispsize = (1024,768)
overlay_alpha = 0.5

debug_mode = False

graph_y_offset = 10
		
graph_datasize=200
graph_ymax=50
		
ymax_stepsize = 2
ymax_range = (1,200)

track_options = get_default_options()

#continually change target color to the closest match (to account for changing light, 
#	but actually just causes problems so keep False)
do_update_matchcolor = False

#bbox = (0.25, 0, 0.5, 1)
bbox = (0,0,1,1)
docrop = True

pt0color = Color.BLACK
ptcolor = Color.GREEN

ptcolor_accum = Color.RED

dot_size = 10
motion_threshold = 10
accum_lambda = 0.1
draw_accum = False

#True = do not show camera image on screen (only show tracking results)
hide_face = False
bgcolor = (60,60,60)

do_vlc_movie = False

camprops={"width":640,"height":480}

################################################
# Initialize the camera
# Find the "last" camera in the list of attached cameras.
#		This should select any external camera over any built-in

#cam=Camera(camera_index=0,prop_set={"width":640,"height":480})

if sys.platform.startswith('win'):
	camidx=0
elif sys.platform.startswith('darwin'):
	camidx=1
else:
	print "Listing attached cameras: "
	camidx=0
	for i in range(0,3):
		print "Testing camera "+str(i)
		cam = Camera(camera_index=i)
		if cam.getProperty('width') == 0:
			camidx=i-1
			del cam
			break
		del cam

print "Using camera "+str(camidx)

cam=Camera(camera_index=camidx, prop_set=camprops)

img0 = None

############################
pt = None
pt0 = None
pt_dist = 0
pt_accum = None
pt_dist_accum = 0

#empty_val = 0
empty_val = float('nan')
scroll_trace = True

trace_idx = 0
movement_trace = numpy.zeros((200,3))
movement_accum_trace = numpy.zeros((200,3))

tracegraph = []
accumgraph = []

#############################
if do_vlc_movie:
	VLCTelnet.run_vlc(password="hcp")

	vlc = VLCTelnet(password="hcp")
	vlc.clear()
	scriptdir=os.path.dirname(os.path.realpath(__file__))
	vlc.add(scriptdir+"/../video_clips/Pixar-02.m4v")
	vlc.stop()
	vlc.set_volume(100) #0 to 1024
#############################

display = Display(dispsize)

time0 = time.time()

#matchcolor = Color.YELLOW
#matchcolor = (190,190,80)
#matchcolor = Color.RED
#matchcolor = (0,230,200)
#matchcolor = (80,180,150)
#matchcolor = (116.0, 224.0, 177.0)
matchcolor = (142.0, 166.0, 112.0)
#matchcolor = Color.GREEN

target_colors = ((255,0,0),(255,128,0),(255,255,0),(0,255,0))
dartboard_size = 100
dartboard_scales = (1,.75,.5,.25)

graph_ymax_new = graph_ymax

framecount = 0

framerate_epoch = 1
framerate_start = 0
framerate_time0 = 0
framerate = 0

# Loop to continuously get images
while display.isNotDone():
	# Get Image from camera
	img = cam.getImage() 
	
	if not img0:
		img0 = img
	
	if docrop:
		img = img.crop(bbox[0]*img.width, bbox[1]*img.height, bbox[2]*img.width, bbox[3]*img.height)
	else:
		img = img.resize(w=display.resolution[0])

	img = img.flipHorizontal()
	if display.resolution[1] != img.height:
		display.resolution = img.size()
		
	img_orig = img;

	###############################
	(pt,newcolor) = trackColor(img,matchcolor,track_options)
	###############################

	if pt and do_update_matchcolor:
		matchcolor = newcolor
		
	if display.mouseLeft:
		pt0 = (display.mouseRawX, display.mouseRawY)
		matchcolor = img.medianFilter((9,9)).getPixel(pt0[0],pt0[1])
		
		print "Color: ",img.medianFilter((9,9)).getPixel(pt0[0],pt0[1])

	if display.mouseRight:
		pt1 = (display.mouseRawX, display.mouseRawY)
		graph_ymax_new = math.sqrt((pt1[0]-pt0[0])**2+(pt1[1]-pt0[1])**2)
		#print Color.hsv(img.medianFilter((9,9)).getPixel(display.mouseRawX,display.mouseRawY))

	try:
		key = pygame.key.get_pressed()
	except:
		print "exiting"
		break
	
	if key[pygame.K_RETURN]:
		if do_vlc_movie:
			if vlc.status()['state'] == "playing":
				vlc.pause()
			else:
				vlc.play()
	elif key[pygame.K_SPACE]:
		pt0 = pt
		matchcolor = newcolor
	elif key[pygame.K_UP]:
		graph_ymax_new=graph_ymax + ymax_stepsize
	elif key[pygame.K_DOWN]:
		graph_ymax_new=graph_ymax - ymax_stepsize
	elif key[pygame.K_h]:
		hide_face = not hide_face
		

	if not graph_ymax == graph_ymax_new:
		graph_ymax=min(max(graph_ymax_new,ymax_range[0]),ymax_range[1])
		graph_ymax_new=graph_ymax
		print "Graph height scale: ",graph_ymax
	
	dartboard_size = 1*graph_ymax
	
	if pt0:
		pt0_draw = pt0
	else:
		pt0_draw = (img.width*0.5,img.height*0.5)
		
	if not pt0:
		pt0 = pt

	if hide_face:
		img.dl().rectangle((0,0),(img.width,img.height),color=bgcolor,width=1,filled=True,alpha=255)
  
	if pt0_draw:
		dl_target = DrawingLayer((img.width,img.height))
		if hide_face:
			for c in range(0,len(dartboard_scales)):
				dl_target.circle(map(int,pt0_draw),dartboard_size*dartboard_scales[c],color=target_colors[c],alpha=128,filled=True,antialias=True)
			dl_target.circle(map(int,pt0_draw),dot_size,color=target_colors[c],alpha=0,filled=True,antialias=True)
			c=-1
			dl_target.circle(map(int,pt0_draw),dot_size,color=target_colors[c],alpha=128,filled=True,antialias=True)
			#dl_target.circle(map(int,pt0_draw),graph_ymax,color=pt0color,alpha=255,filled=False,width=min(2,graph_ymax))

		else:
			c=-1
			dl_target.circle(map(int,pt0_draw),dot_size,color=target_colors[c],alpha=128,filled=True,antialias=True)
			dl_target.circle(map(int,pt0_draw),graph_ymax,color=pt0color,alpha=255,filled=False,width=min(2,graph_ymax))

		img.addDrawingLayer(dl_target)
		
	pt_dist=empty_val
	pt_entry=(empty_val,empty_val,empty_val)
	pt_accum_entry=(empty_val,empty_val,empty_val)
	
	if pt:
		pt_dist = math.sqrt((pt[0]-pt0[0])**2+(pt[1]-pt0[1])**2)
		#img.drawCircle(ctr=pt,rad=5,thickness=3,color=ptcolor)
		img.dl().circle(map(int,pt),dot_size,color=ptcolor,alpha=255,filled=True)
		img.dl().circle(map(int,pt0),pt_dist,color=ptcolor,alpha=255,filled=False,width=min(2,pt_dist))
		#img.drawCircle(ctr=pt0,rad=5,thickness=3,color=pt0color)
		pt_entry=(pt[0],pt[1],pt_dist)
		pt_yval = pt_dist
	else:
		pt_yval = empty_val
		
	if not pt_accum:
		pt_accum = pt

	if pt and pt_accum:
		pt_dist_accum = (1-accum_lambda)*pt_dist_accum+accum_lambda*pt_dist
		
		ax = (1-accum_lambda)*pt_accum[0]+accum_lambda*pt[0]
		ay = (1-accum_lambda)*pt_accum[1]+accum_lambda*pt[1]
		pt_accum = (ax,ay)
		
		pt_accum_yval = pt_dist_accum
		if draw_accum:
			img.dl().circle(map(int,pt_accum),5,color=ptcolor_accum,alpha=255,filled=True)
		
		pt_accum_entry=(pt_accum[0],pt_accum[1],pt_dist_accum)
	else:
		pt_accum_yval = empty_val

	movement_accum_trace[trace_idx,0:3]=pt_accum_entry
	movement_trace[trace_idx,:]=pt_entry

	if not tracegraph:
		graphbounds=(0,graph_y_offset,img.width,img.height/2)
		tracegraph = DrawGraph(graphbounds, graph_datasize, scrollable=True)
		accumgraph = DrawGraph(graphbounds, graph_datasize, scrollable=True)
		
	tracegraph.newpoint(pt_yval)
	accumgraph.newpoint(pt_accum_yval)
	

	tracegraph.draw(img.dl(),ymax=graph_ymax,color=ptcolor, linewidth=2)
	if draw_accum:
		accumgraph.draw(img.dl(),ymax=graph_ymax,color=ptcolor_accum, linewidth=2)
		
	trace_idx = (trace_idx + 1) % movement_trace.shape[0]

	img.show()
	
	#if do_vlc_movie and pt_dist > motion_threshold:
	#	vlc.pause()
	##	vlc.play()


	tnow = time.time()
	if framerate_epoch > 0 and tnow - framerate_time0 > framerate_epoch:
		framerate = (framecount-framerate_start)/(tnow-framerate_time0)
		framerate_time0 = tnow
		framerate_start = framecount
		print "fps: ",framerate
		
	if img_expiration > 0 and time.time() - time0 > img_expiration:
		#img.save("/Users/kjamison/Downloads/motiontracking/img_"+time.strftime("%Y%m%d-%H%M%S")+".png")
		time0 = time.time()
            
	framecount = framecount + 1

if do_vlc_movie:
	vlc.pause()
	vlc.logout()
	
