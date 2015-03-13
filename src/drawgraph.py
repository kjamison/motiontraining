from SimpleCV import *
import numpy as np

class DrawGraph:

	def __init__(self):
		pass
		
	def __init__(self, display_bounds, datasize, scrollable=True):
		
		self.graph_x_offset = display_bounds[0]
		self.graph_y_offset = display_bounds[1]
		self.graph_w = display_bounds[2]-display_bounds[0]
		self.graph_h = display_bounds[3]-display_bounds[1]
		self.is_scrollable = scrollable
		
		self.graph_idx=0
		
		self.graph_data_size=datasize
		self.graph_x=np.array(range(datasize))
		self.graph_data=np.zeros((datasize,1))
		
	################################################
	def __drawlines_with_nan__(self,drawinglayer,points,color=Color.BLACK,width=1):
		#drawinglayer.lines(points,color=color,width=width)
		#return
		nanpts=np.any(np.isnan(points),axis=1)
		if np.all(nanpts):
			return
		nanpts=np.append([1],np.append(nanpts,[1]))
		d=np.diff(nanpts)

		drawstart=(d==-1).nonzero()[0]
		drawstop=(d==1).nonzero()[0]
		
		for i in range(0,len(drawstart)):
			i1=drawstart[i]
			i2=drawstop[i]
			if i2-i1 <= 1:
				continue
			drawinglayer.lines(points[i1:i2,:],color=color,width=width)
		
	def newpoint(self,newval):
		self.graph_idx += 1
		if not self.is_scrollable:
			self.graph_idx %= self.graph_data_size
				
		if self.is_scrollable and self.graph_idx >= self.graph_data_size:
			self.graph_data[:-1] = self.graph_data[1:]
			self.graph_data[-1] = newval
		else:
			self.graph_data[self.graph_idx] = newval
				
	def reset(self):
		self.graph_idx = 0
		
	def update_graph_bounds(self, graph_bounds):
		self.graph_x_offset = graph_bounds[0]
		self.graph_y_offset = graph_bounds[1]
		self.graph_w = graph_bounds[2]-graph_bounds[0]
		self.graph_h = graph_bounds[3]-graph_bounds[1]
		
	def draw(self,drawinglayer,ymax,color=Color.BLACK,linewidth=1):
		if self.graph_idx <= 1:
			return
			
		w = self.graph_w
		h = self.graph_h
		idx = self.graph_idx
		sz = self.graph_data_size
		
		y_scaled = self.graph_data[:idx+1]/ymax
		y_scaled[y_scaled>1] = 1
		
		y = (drawinglayer.height-self.graph_y_offset)-y_scaled*h
		x = self.graph_x_offset+self.graph_x[:idx+1]*w/sz
		
		self.__drawlines_with_nan__(drawinglayer,np.array((x,y)).T,color,linewidth)
