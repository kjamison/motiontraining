from SimpleCV import *
import numpy as np

def hueDistance1(color1,color2):
	if isinstance(color1,  (float,int,long,complex)):
		color1_hue = color1
	else:
		color1_hue = Color.hsv(color1)[0]

	if isinstance(color2,  (float,int,long,complex)):
		color2_hue = color2
	else:
		color2_hue = Color.hsv(color2)[0]

	if color1_hue < 90:
		hue_loop = 180
	else:
		hue_loop = -180
	#set whether we need to move back or forward on the hue circle

	distances = np.minimum( np.abs(color2_hue - color1_hue), np.abs(color2_hue - (color1_hue + hue_loop)))
	distances = 255.0*distances/90.0
	return distances
		
def colorDistance1(color1,color2):
	distances = spsd.cdist([color1], [color2]) #calculate the distance each pixel is
	distances = distances[0][0]
	return distances
		
def get_default_options():
	options = {
		'cdist_min_sat': 50,
		'cdist_min_val': 50,
		'binarize_threshold': 30,
		'min_circ_diam': 5,
		'max_circ_diam': 200,
		'max_circshape': 1,
		'debug_mode': False,
		'draw_blob': False
	}
	return options
	
def trackColor(img,matchcolor,options=None):
	if not options:
		options = get_default_options()
		
	cdist = img.blur((3,3)).hueDistance(matchcolor,minsaturation=options['cdist_min_sat'],minvalue=options['cdist_min_val'])
	#cdist = img.medianFilter((5,5)).colorDistance(matchcolor)

	cmask = cdist.binarize(thresh=options['binarize_threshold'])
	#counts = cdist.getGrayNumpy()
	#print counts.size()
	#.dilate(4).erode(8)
	
	
	pt = None
	newcolor = matchcolor
	
	blobs = img.findBlobsFromMask(cmask)
	if not blobs:
		return (pt,newcolor)

	#for b in blobs[::-1]:
	for b in blobs[-1::]:
		xy = b.centroid()
		circdist = b.circleDistance()
		a = b.area()
		mc = b.meanColor()
		colordist = colorDistance1(matchcolor,mc)	
		huedist = hueDistance1(matchcolor,mc)
		#print a,circdist
		if options['draw_blob']:
			b.draw(width=1,color=Color.RED)
		#el = cv2.fitEllipse(numpy.asarray(b.contour()))

		if a > options['min_circ_diam']**2 and a < options['max_circ_diam']**2 and b.isCircle(options['max_circshape']):
			#matchcolor = mc[::-1]
			#mc = img.medianFilter((5,5)).getPixel(int(xy[0]),int(xy[1]))
			if options['debug_mode']:
				print colordist,huedist

			newcolor = mc
			#print mc
			#print "good:",a,circdist
			#b.drawMinRect(width=2,color=Color.WHITE)
			#ptcolor = Color.GREEN
			pt = xy
			break
		else:
			if options['debug_mode']:
				print "missing:",a,circdist

	return (pt,newcolor)
