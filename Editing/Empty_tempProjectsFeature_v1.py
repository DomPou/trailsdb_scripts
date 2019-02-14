import sys

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(editingFolder)
from Editing_Variables_v1 import *

# Step 1: Remove layer from dataframe if in it to remove lock
mxd = arcpy.mapping.MapDocument("CURRENT")
for df in arcpy.mapping.ListDataFrames(mxd):
	for lyr in arcpy.mapping.ListLayers(mxd, "", df):
		if lyr.name == "tempProjectsFeature":
			arcpy.mapping.RemoveLayer(df,lyr)

# Step 2: delete old layer if exists
arcpy.AddMessage("Creating empty tempProjectsFeature")
if arcpy.Exists(tempProjectsFeaturePath):
	arcpy.Delete_management(tempProjectsFeaturePath)

# Step 3: create layer in db queries and add fields
arcpy.CreateFeatureclass_management(tempEditingGdbPath, tempProjectsFeatureName, "POLYLINE", "", "DISABLED", "DISABLED", projection)

for field in fieldsProjectsFeature:
	fieldName = field[0]
	fieldType = field[3]
	fieldDomain = field[4]
	try:
		arcpy.AddField_management(tempProjectsFeaturePath, fieldName, fieldType,"","","","","","",fieldDomain)
	except:
		continue

# Step 4: add layer to dataframe
layerToAdd = arcpy.mapping.Layer(tempProjectsFeaturePath)
for df in arcpy.mapping.ListDataFrames(mxd):
	arcpy.mapping.AddLayer(df, layerToAdd, "TOP")

stopTime = time.time()
arcpy.AddMessage("Time to make tempProjectsFeature = %02d:%02d:%02d" % (int(stopTime-startTime)/3600,int(((stopTime-startTime)%3600)/60),int((stopTime-startTime)%60)))
