import clr
import sys
import System
from System.Collections.Generic import List
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
import Autodesk.DesignScript.Geometry as DS

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
import Autodesk.Revit.DB as DB

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = uiapp.ActiveUIDocument

class FaceSelection(ISelectionFilter):
	def AllowElement(self, e):
		return True

	def AllowReference(self, ref, point):
		if ref.ElementReferenceType == ElementReferenceType.REFERENCE_TYPE_SURFACE:
			return True
		else:
			return False

viewFamilyType = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements().Find(lambda x : x.ViewFamily == ViewFamily.Section)
v = None
margin_c = 0.4
#
TaskDialog.Show("Selection", "Pick Point on a Planar Face")
ref = uidoc.Selection.PickObject(ObjectType.PointOnElement, FaceSelection(), "Pick Point on a Planar Face")
# get Face Geometry
sel_elem = doc.GetElement(ref)
if isinstance(sel_elem, RevitLinkInstance):	
	tf1 = sel_elem.GetTotalTransform()
	linkDoc = sel_elem.GetLinkDocument()
	elem = linkDoc.GetElement(ref.LinkedElementId)
	if isinstance(elem, FamilyInstance):
		tf2 = elem.GetTotalTransform()
		tf1 *= tf2
	face_ref2 = ref.CreateReferenceInLink()
	face = elem.GetGeometryObjectFromReference(face_ref2)
else:
	elem = sel_elem
	face = elem.GetGeometryObjectFromReference(ref)
	if isinstance(elem, FamilyInstance):
		tf1 = sel_elem.GetTotalTransform()
	else:
		tf1 = Transform.Identity
#
bbxUV = face.GetBoundingBox()
midpoint = tf1.OfPoint(face.Evaluate((bbxUV.Min + bbxUV.Max) * 0.5))
# get the max point on face
pt_maxUV = tf1.OfPoint(face.Evaluate(bbxUV.Max))
pt_minUV = tf1.OfPoint(face.Evaluate(bbxUV.Min))
maxptZface = max([pt_maxUV, pt_minUV], key = lambda x : x.Z)
selectPoint = ref.GlobalPoint
# get faceNormal and compute the margin for section View
faceNormal = tf1.OfVector(face.ComputeNormal((bbxUV.Min + bbxUV.Max) * 0.5).Negate())
bbxElem = elem.get_BoundingBox(None)
minUV = bbxUV.Min
maxUV = bbxUV.Max
midleUV = (bbxUV.Min + bbxUV.Max) * 0.5
marginCropbox = UV(margin_c, margin_c) # margin_c -> 0.4
# calculate minUV and maxUV for section
min_uv = minUV - midleUV - marginCropbox
max_uv = maxUV - midleUV + marginCropbox	
# calculate Basis for section BBX
zV = faceNormal
if faceNormal.CrossProduct(XYZ.BasisZ).IsAlmostEqualTo(XYZ.Zero):
	xV = XYZ.BasisY.CrossProduct(faceNormal).Normalize()
else:
	xV = XYZ.BasisZ.CrossProduct(faceNormal).Normalize()
yV = zV.CrossProduct(xV).Normalize()
#
t = Transform.Identity
t.Origin = midpoint
t.BasisX = xV
t.BasisY = yV
t.BasisZ = zV
#
sectionBox = BoundingBoxXYZ()
sectionBox.Enabled = True
sectionBox.Min =  XYZ(min_uv.U, min_uv.V, -2)
sectionBox.Max =  XYZ(max_uv.U, max_uv.V, 0.5)
sectionBox.Transform = t
#
TransactionManager.Instance.EnsureInTransaction(doc)
#
v = DB.ViewSection.CreateSection(doc, viewFamilyType.Id, sectionBox)
v.get_Parameter(BuiltInParameter.VIEWER_BOUND_FAR_CLIPPING).Set(1)
#
# fix some outline on vertical and horizontal view section 
crsm = v.GetCropRegionShapeManager()
# fix with horizontal faces -> use face_curvLoop with offset
if abs(faceNormal.Z) > 0.99:
	face_curvLoop = face.GetEdgesAsCurveLoops()[0]
	curveloop_shape = CurveLoop.CreateViaTransform(face_curvLoop, tf1)
	curveloop_shape = CurveLoop.CreateViaOffset(curveloop_shape, 1.02, v.ViewDirection)
	crsm.SetCropShape(curveloop_shape)
		
# check with vertical faces
# rotate 90 degre the 'outline curveloop shape' if any curve of 'curveloop shape' are not near to maxptface point
elif abs(faceNormal.Z) < 0.01:
	curveloop_shape = crsm.GetCropShape()[0]
	tf3 = Transform.CreateRotationAtPoint(faceNormal, System.Math.PI * 0.5, midpoint)
	candiate_curveloop_shape = CurveLoop.CreateViaTransform(curveloop_shape, tf3)
	maxZCurveLoop = max(c.GetEndPoint(i).Z for c in curveloop_shape for i in range(2))
	if not margin_c - 0.01 <= abs(maxZCurveLoop - maxptZface.Z) < margin_c + 0.1:
		crsm.SetCropShape(candiate_curveloop_shape)
		
else:
	pass
#
TransactionManager.Instance.TransactionTaskDone()
TransactionManager.Instance.ForceCloseTransaction()
#
uidoc.RequestViewChange(v)
OUT = face, selectPoint.ToPoint(), midpoint.ToPoint(), maxptZface.ToPoint(), faceNormal
