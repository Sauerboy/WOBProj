# ----------------------------------------------
# Script Recorded by Ansys Electronics Desktop Version 2024.2.0
# 21:33:23  Apr 26, 2026
# ----------------------------------------------
import ScriptEnv
import csv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("Test_Array")
# oProject.InsertDesign("HFSS", "HFSSDesign1", "HFSS Terminal Network", "")
oDesign = oProject.SetActiveDesign("HFSSDesign1")
with open('C:\\Users\\asauer31\\OneDrive - Georgia Institute of Technology\\Documents\\ECE4803\\Project\\radii.csv', mode='r') as file:
    reader = csv.reader(file)
    radii = list(reader)

with open('C:\\Users\\asauer31\\OneDrive - Georgia Institute of Technology\\Documents\\ECE4803\\Project\\x_pos.csv', mode='r') as file:
    reader = csv.reader(file)
    x_pos = list(reader)

with open('C:\\Users\\asauer31\\OneDrive - Georgia Institute of Technology\\Documents\\ECE4803\\Project\\y_pos.csv', mode='r') as file:
    reader = csv.reader(file)
    y_pos = list(reader)

oEditor = oDesign.SetActiveEditor("3D Modeler")
for i in range(len(x_pos)):
	for j in range(len(y_pos)):
		index=i*len(y_pos)+j
		oEditor.CreateCylinder(
			[
				"NAME:CylinderParameters",
				"XCenter:="		, str(x_pos[i][0])+"mm",
				"YCenter:="		, str(y_pos[j][0])+"mm",
				"ZCenter:="		, "0mm",
				"Radius:="		, str(radii[i][j])+"mm",
				"Height:="		, "h_copper",
				"WhichAxis:="		, "Z",
				"NumSides:="		, "0"
			], 
			[
				"NAME:Attributes",
				"Name:="		, "Patch"+str(index),
				"Flags:="		, "",
				"Color:="		, "(143 175 143)",
				"Transparency:="	, 0,
				"PartCoordinateSystem:=", "Global",
				"UDMId:="		, "",
				"MaterialValue:="	, "\"copper\"",
				"SurfaceMaterialValue:=", "\"\"",
				"SolveInside:="		, True,
				"ShellElement:="	, False,
				"ShellElementThickness:=", "0mm",
				"ReferenceTemperature:=", "20cel",
				"IsMaterialEditable:="	, True,
				"IsSurfaceMaterialEditable:=", True,
				"UseMaterialAppearance:=", False,
				"IsLightweight:="	, False
			])
# oProject.SaveAs("C:\\Users\\asauer31\\OneDrive - Georgia Institute of Technology\\Documents\\ECE4803\\automated_array.aedt", True)