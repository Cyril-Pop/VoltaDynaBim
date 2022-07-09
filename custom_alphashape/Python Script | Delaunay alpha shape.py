import sys
import clr
import System
from System.Collections.Generic import List

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
import Autodesk.DesignScript.Geometry as DS

clr.AddReference('Tessellation')
import Tessellation as TS
import math


def convex_hull_graham(lstPtx):
	"""
	-typing: 
		(lstPtx : Union[list, List[DS.Point]]) -> List[DS.Curve]
	-description:
		Returns points on convex hull in CCW order according to Graham's scan algorithm. 
		By Tom Switzer .
	-Parameters:
		lstPtx : list of points
	-Return:
		list of Curves
	"""
	# sub fuctions
	def toPts(ptVals):
		return Point.ByCoordinates(ptVals[0],ptVals[1],ptVals[2])
		
	def create_shape(lstpts):
		crvs = []
		for idx, p in enumerate(lstpts):
			if idx > 0:
				crvs.append(Line.ByStartPointEndPoint(lstpts[idx - 1], p))
		return crvs
		
	def cmp(a, b):
		return (a > b) - (a < b)
	
	def turn(p, q, r):
		return cmp((q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1]), 0)
	
	def _keep_left(hull, r):
		while len(hull) > 1 and turn(hull[-2], hull[-1], r) != TURN_LEFT:
			hull.pop()
		if not len(hull) or hull[-1] != r:
			hull.append(r)
		return hull
		
	# main function
	# variables
	TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)
	#
	lstPtx = [[pt.X,pt.Y,pt.Z] for pt in lstPtx]	
	lstPtx = sorted(lstPtx)
	l = reduce(_keep_left, lstPtx, [])
	u = reduce(_keep_left, reversed(lstPtx), [])
	lstPtx = l.extend(u[i] for i in range(1, len(u) - 1)) or l
	lstPtx = [toPts(p) for p in lstPtx]
	return List[DS.Curve](create_shape(lstPtx))

def percentile(data, perc):
	size = len(data)
	return sorted(data)[int(math.ceil((size * perc) / 100)) - 1]


def get_near_distances_points(lstPtx):
	"""
	-typing: 
		(lstPtx : Union[list, List[DS.Point]]) -> list
	-description:
		iterative  function to order points by near point (each point) and get distances
	-Parameters:
		lstPtx : list of points
	-Return:
		list of distance
	""" 
	startPt, endPt = lstPtx[0], lstPtx[-1]
	flag = True
	i = 0
	list_distace = []
	while flag and lstPtx and i < 100000:
		i += 1
		lstPtx.sort(key = lambda x : x.DistanceTo(startPt), reverse = True)
		distaceToEnd1 = lstPtx[-1].DistanceTo(endPt)
		distaceToEnd2 = lstPtx[-2].DistanceTo(endPt)
		nearest = lstPtx.pop()
		list_distace.append(int(startPt.DistanceTo(nearest)))
		startPt = nearest
		if distaceToEnd1 < distaceToEnd2 and distaceToEnd1 < 1:
			flag = False

	return list_distace

def tamariz_alphashape(inputPts, alpha = 0.03):
	"""
	-typing: 
		(inputPts: Union[list, List[DS.Point]], alpha : Union[float, System.Double]) -> List[DS.Curve]
	-description:
		calculate alpha shape from 2D point cloud
	-Parameters:
		inputPts : list of DS.Point
		alpha : the alfa precision
	-Return:
		list of curves
	"""
	print("Start processing")
	inverse_alpha = 1 - alpha
	inputPts = sorted(inputPts, key = lambda p : (p.X, p.Y))
	#take a sample to get max_distance percentile
	if alpha == 0.0:
		uniqueCurv = convex_hull_graham(inputPts)
	else:
		interval = max(2, int(0.001 * len(inputPts)))
		print("interval", interval)
		copyinputPts = inputPts[::interval]
		distances = get_near_distances_points(copyinputPts)
		distances = list(set(distances))
		max_distance = percentile(distances, inverse_alpha * 100)
		print("max_distance", max_distance)
		maxX = max(p.X for p in inputPts)
		maxY = max(p.Y for p in inputPts)
		p0 = DS.Point.ByCoordinates(maxX + 20, maxY + 20, 100)
		inputPts.append(p0)
		delaun_Curves = list(TS.Delaunay.ByPoints(inputPts))
		triangl_curves = []
		triangl_curves = [delaun_Curves[i:i+3] for i in range(0, len(delaun_Curves), 3) if all(not c.StartPoint.IsAlmostEqualTo(p0) for c in delaun_Curves[i:i+3])]
		triangl_curves = [sublst  for sublst in triangl_curves if all(c.Length < max_distance for c in sublst)]
		flat_curve = [j for i in triangl_curves for j in i]
		lines_serialze = ["{},{}".format(c.PointAtParameter(0.5), c.Length) for c in flat_curve]
		unique_str = [i for i in lines_serialze if lines_serialze.count(i) == 1]
		uniqueCurv = List[DS.Curve]([flat_curve[lines_serialze.index(i)] for i in unique_str])
	return uniqueCurv
	

inputPts = IN[0]
alpha = IN[1]

OUT = tamariz_alphashape(inputPts, alpha)
