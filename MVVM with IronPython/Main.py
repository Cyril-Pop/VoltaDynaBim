import clr  
import sys
import System
from System.Collections.Generic import List, KeyValuePair
from System.Collections.ObjectModel import ObservableCollection
from System.Threading import Thread, ThreadStart, ApartmentState


#import Revit API
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
import Autodesk.Revit.DB as DB

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument


sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\DLLs')
clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

try:
	clr.AddReference("IronPython.Wpf")
	clr.AddReference('System.Core')
	clr.AddReference('System.Xml')
	clr.AddReference('PresentationCore')
	clr.AddReference('PresentationFramework')
	clr.AddReferenceByPartialName("WindowsBase")
except IOError:
	raise
	
from System.IO import StringReader
from System.Windows.Markup import XamlReader, XamlWriter
from System.Windows import Window, Application
from System.ComponentModel import INotifyPropertyChanged
from System.ComponentModel import PropertyChangedEventArgs

try:
	import wpf
	import time
except ImportError:
	raise
	

class XamlLoader(Window):
	LAYOUT = '''
			<Window
				xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
				xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
				xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
				xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
				xmlns:local="clr-namespace:WpfApplication1"
				mc:Ignorable="d" 
				Height="600" 
				Width="600" 
				ResizeMode="NoResize"
				Title="A" 
				WindowStartupLocation="CenterScreen" 
				Topmost="True" 
				SizeToContent="Width">
				<Grid Margin="10,0,10,10">
					<Label x:Name="selection_label" Content="Select Item" HorizontalAlignment="Left" Height="30"
						VerticalAlignment="Top"/>
						<Button x:Name="button_select" Content="Select" HorizontalAlignment="Center" Height="26" Margin="0,63,0,0" VerticalAlignment="Bottom" Width="200" Click="ButtonClick"/>
						<DataGrid   x:Name="dataGrid" 
									AutoGenerateColumns="False"
									Margin="10,30,10,30"
									BorderThickness="1"
									RowHeaderWidth="0"
									CanUserSortColumns="True"
									CanUserResizeColumns = "False"
									VerticalScrollBarVisibility="Auto"
									ItemsSource="{Binding}">
						<DataGrid.Columns>
							<DataGridTextColumn Header="FamilyName" Binding="{Binding FamilyName}" IsReadOnly="True" Width="250"/>
							<DataGridTextColumn Header="Name" Binding="{Binding Name}" IsReadOnly="True" Width="100"/>
							<DataGridTemplateColumn Header="Param">
								<DataGridTemplateColumn.CellTemplate>
									<DataTemplate>
										<ComboBox x:Name="Combobox"
											ItemsSource="{Binding LstValue}" 
											SelectedItem="{Binding SelectValue, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" 
											Width="200"/>
								</DataTemplate>
							</DataGridTemplateColumn.CellTemplate>
						</DataGridTemplateColumn>
						</DataGrid.Columns>
					</DataGrid>
				</Grid>
			</Window>'''
	
	def __init__(self, data_collection):
		self.ui = wpf.LoadComponent(self, StringReader(XamlLoader.LAYOUT))
		self.ui.Title = "Select Types"
		self.data = data_collection
		self.ui.DataContext = self.data
		
		
	def ButtonClick(self, sender, e):
		self.DialogResult = True
		self.Close()
	
	def __getattr__(self, item):
		"""Maps values to attributes.
		Only called if there *isn't* an attribute with this name
		"""
		return self.ui.FindName(item)

		
class ViewModelBase(INotifyPropertyChanged):
	"""
	base view model class that implements the INotifyPropertyChanged interface
	"""
	def __init__(self):
		self.propertyChangedHandlers = []

	# Define a method to raise the PropertyChanged event
	def RaisePropertyChanged(self, propertyName):
		# Create a PropertyChangedEventArgs object with the name of the changed property
		args = PropertyChangedEventArgs(propertyName)
		for handler in self.propertyChangedHandlers:
			# Invoke each of the registered property changed handlers with the ViewModelBase instance and the event arguments
			handler(self, args)
	# Define a method to add a property changed handler
	def add_PropertyChanged(self, handler):
		self.propertyChangedHandlers.append(handler)
	# Define a method to remove a property changed handler
	def remove_PropertyChanged(self, handler):
		self.propertyChangedHandlers.remove(handler)
		


class MyDataViewModel(ViewModelBase):
	"""
	a view model class that inherits from ViewModelBase
	"""
	def __init__(self):
		ViewModelBase.__init__(self)
		self._Name = ""
		self._FamilyName = ""
		# define a attribute to store the selected value from conbobox (binding)
		self._SelectValue = ""
		self._LstValue = ObservableCollection[System.String]()
	
	# Define all getters and setters properties 
	@property
	def Name(self):
		return self._Name

	@Name.setter
	def Name(self, value):
		self._Name = value
		# Raise the PropertyChanged event with the name of the changed property
		self.RaisePropertyChanged("Name")
		
	@property
	def FamilyName(self):
		return self._FamilyName

	@FamilyName.setter
	def FamilyName(self, value):
		self._FamilyName = value
		# Raise the PropertyChanged event with the name of the changed property
		self.RaisePropertyChanged("FamilyName")
		
		
	@property
	def SelectValue(self):
		return self._SelectValue

	@SelectValue.setter
	def SelectValue(self, value):
		self._SelectValue = value
		# Raise the PropertyChanged event with the name of the changed property
		self.RaisePropertyChanged("SelectValue")
		
	@property
	def LstValue(self):
		return self._LstValue
		
	@LstValue.setter
	def LstValue(self, lst_value):
		self._LstValue = ObservableCollection[System.String](lst_value)
		# Raise the PropertyChanged event with the name of the changed property
		self.RaisePropertyChanged("LstValue")
		
def appThread():
	appThread.form = None
	used_DoorsTypeIds = set(list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().Select(lambda x : x.GetTypeId())))
	net_dict_DType = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors)\
													.WhereElementIsElementType()\
													.Select(lambda x : KeyValuePair[System.String, DB.Element](x.FamilyName +":"+ Element.Name.GetValue(x), x))\
													.ToDictionary(lambda kvp: kvp.Key, lambda kvp: kvp.Value)
																						
	#
	# Create an ObservableCollection of MyDataViewModel objects
	data = ObservableCollection[MyDataViewModel]()
	for doorTypeId in used_DoorsTypeIds:
		doorType = doc.GetElement(doorTypeId)
		en = MyDataViewModel()
		en.Name = Element.Name.GetValue(doorType)
		en.FamilyName = doorType.FamilyName
		# set list for combobox 
		en.LstValue = net_dict_DType.Keys 
		data.Add(en)

	xaml = XamlLoader(data)
	appThread.form = xaml
	xaml.ui.ShowDialog()
	#
	return [[x.SelectValue, net_dict_DType[x.SelectValue] if  net_dict_DType.ContainsKey(x.SelectValue) else None]  for x in appThread.form.data]
	

OUT = appThread()

