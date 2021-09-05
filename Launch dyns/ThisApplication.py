
import clr
import System
clr.AddReferenceByName("RevitAPI.dll");
clr.AddReferenceByName("RevitAPIUI.dll");

from Autodesk.Revit import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Macros import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from System.Collections.Generic import *
from System.Collections import *
from System import *
from math import *

clr.AddReference('System.Windows.Forms')
import System.Windows.Forms
from System.Windows.Forms import *

clr.AddReference('DynamoRevitDS')
import Dynamo 
import ModuleDYN
from ModuleDYN import LauncherDyn

class ThisApplication (ApplicationEntryPoint):
    #region Revit Macros generated code
    def FinishInitialization(self):
        ApplicationEntryPoint.FinishInitialization(self)
        self.InternalStartup()
    
    def OnShutdown(self):
        self.InternalShutdown()
        ApplicationEntryPoint.OnShutdown(self)
    
    def InternalStartup(self):
        self.Startup()
    
    def InternalShutdown(self):
        self.Shutdown()
    #endregion
    
    def Startup(self):
        self
        
    def Shutdown(self):
        self
     
    
    # Transaction mode
    def GetTransactionMode(self):
        return Attributes.TransactionMode.Manual
    
    # Addin Id
    def GetAddInId(self):
        return '070DE949-16BC-44E8-B48F-3130314165B2'

    def HelloWorld(self):
        LauncherDyn.LaunchDyn(self, r'D:\DIVERS Pour Articles Blogs BIM\Launch DynamoScript\Test Hello Word.dyn')
        
    def GroupColor(self):
        LauncherDyn.LaunchDyn(self, r'D:\DIVERS Pour Articles Blogs BIM\Launch DynamoScript\group by distance.dyn')
        
        
    def TestMulti(self):
        LauncherDyn.LaunchMultiDyn(self, [ r'D:\DIVERS Pour Articles Blogs BIM\Launch DynamoScript\Test Hello Word.dyn', 
                                           r'D:\DIVERS Pour Articles Blogs BIM\Launch DynamoScript\group by distance.dyn'])        
      
