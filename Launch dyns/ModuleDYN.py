
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

clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')
import System.Drawing
import System.Windows.Forms

from System.Drawing import *
from System.Windows.Forms import *

clr.AddReference('DynamoRevitDS')
import Dynamo 

class LauncherDyn():
    @staticmethod
    def LaunchDyn(uiapp, pathScript):
        result = MessageBox.Show("Lancer le Script Dynamo?\n\nOui -> Lance le script\nNon -> Edite le script","Editer ou Lancer?", MessageBoxButtons.YesNo )
        dynamoRevit = Dynamo.Applications.DynamoRevit()
        dynamoApp = Dynamo.Applications
        if result == DialogResult.Yes:
            journalData = Dictionary[str, str]()
            journalData.Add(Dynamo.Applications.JournalKeys.ShowUiKey, False.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.AutomationModeKey, True.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.DynPathKey, "")
            journalData.Add(Dynamo.Applications.JournalKeys.DynPathExecuteKey, True.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.ForceManualRunKey, False.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.ModelShutDownKey, True.ToString() )
            journalData.Add(Dynamo.Applications.JournalKeys.ModelNodesInfo, False.ToString())
            #
            dynamoRevitCommandData = dynamoApp.DynamoRevitCommandData()
            dynamoRevitCommandData.Application = uiapp
            dynamoRevitCommandData.JournalData = journalData
            #
            dynamoRevit.ExecuteCommand(dynamoRevitCommandData)
            dynamoRevit.RevitDynamoModel.OpenFileFromPath(pathScript, True)
            dynamoRevit.RevitDynamoModel.ForceRun() 
            #
            currentWorkspaceNodes = dynamoRevit.RevitDynamoModel.CurrentWorkspace.Nodes     
            if any("Warning" in n.State.ToString() for n in currentWorkspaceNodes):
                dynFile = System.IO.Path.GetFileName(pathScript)
                trayIcon = NotifyIcon() 
                trayIcon.Text = "Erreur Script"
                trayIcon.Visible = True
                trayIcon.Icon = System.Drawing.Icon.ExtractAssociatedIcon(Application.ExecutablePath)
                trayIcon.ShowBalloonTip(600, "Erreur Script", "Script '{}' Execute avec erreur".format(dynFile), ToolTipIcon.Warning)            
            
        else:
            journalData = Dictionary[str, str]()
            journalData.Add(Dynamo.Applications.JournalKeys.ShowUiKey, True.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.AutomationModeKey, False.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.DynPathKey, pathScript)
            journalData.Add(Dynamo.Applications.JournalKeys.DynPathExecuteKey, False.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.ForceManualRunKey, False.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.ModelShutDownKey, False.ToString() )
            journalData.Add(Dynamo.Applications.JournalKeys.ModelNodesInfo, True.ToString())
            #
            dynamoRevitCommandData = dynamoApp.DynamoRevitCommandData()
            dynamoRevitCommandData.Application = uiapp
            dynamoRevitCommandData.JournalData = journalData
            #
            dynamoRevit.ExecuteCommand(dynamoRevitCommandData)
            dynamoRevit.RevitDynamoModel.OpenFileFromPath(pathScript, True) 
            
    @staticmethod
    def LaunchMultiDyn(uiapp, lstpathScript):
        for pathScript in lstpathScript:
            dynamoRevit = Dynamo.Applications.DynamoRevit()
            dynamoApp = Dynamo.Applications
            journalData = Dictionary[str, str]()
            journalData.Add(Dynamo.Applications.JournalKeys.ShowUiKey, False.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.AutomationModeKey, True.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.DynPathKey, "")
            journalData.Add(Dynamo.Applications.JournalKeys.DynPathExecuteKey, True.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.ForceManualRunKey, False.ToString())
            journalData.Add(Dynamo.Applications.JournalKeys.ModelShutDownKey, True.ToString() )
            journalData.Add(Dynamo.Applications.JournalKeys.ModelNodesInfo, False.ToString())
            #
            dynamoRevitCommandData = dynamoApp.DynamoRevitCommandData()
            dynamoRevitCommandData.Application = uiapp
            dynamoRevitCommandData.JournalData = journalData
            #
            dynamoRevit.ExecuteCommand(dynamoRevitCommandData)
            dynamoRevit.RevitDynamoModel.OpenFileFromPath(pathScript, True)
            dynamoRevit.RevitDynamoModel.ForceRun() 