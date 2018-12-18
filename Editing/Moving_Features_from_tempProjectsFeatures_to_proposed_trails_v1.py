import sys, datetime

startTime = time.time()

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(editingFolder)
from Editing_Variables_v1 import *

sys.path.append(functionsFolder)
from Build_SQL_Where_Clause import *

# Script Variables
featuresList = []
# Line features in trailsdb - Proposed
arcpy.env.workspace = gdbFeaturesRoot + "proposed_info\\"
for feature in arcpy.ListFeatureClasses(feature_type='Line'):
	featuresList.append(feature)
# Line features in trailsdb - Proposed Signage
arcpy.env.workspace = gdbFeaturesRoot + "proposed_signage_info\\"
for feature in arcpy.ListFeatureClasses(feature_type='Line'):
	featuresList.append(feature)

projectsFeatureFields = {}
featuresFields = {}

# Step 1: Remove layer from dataframe to remove lock
mxd = arcpy.mapping.MapDocument("CURRENT")
for df in arcpy.mapping.ListDataFrames(mxd):
	for lyr in arcpy.mapping.ListLayers(mxd, "", df):
		if lyr.name == "tempProjectsFeature":
			arcpy.mapping.RemoveLayer(df,lyr)

# Step 2: Create list and dictionaries of field to rename to move info to proposed_trails
for field in fieldsProjectsFeature:
	featureName = field[1]
	projectField = field[0]
	featureField = field[2]
	currentProjectFields = projectsFeatureFields.get(featureName)
	if currentProjectFields is None:
		currentProjectFields = [projectField]
	else:
		currentProjectFields.append(projectField)
	featuresFields.update({projectField:featureField})
	projectsFeatureFields.update({featureName:currentProjectFields})

# Step 3: Use list and dictionaries to append right fields to proposed_trails features
tempProjectsFeatureFields = arcpy.ListFields(tempProjectsFeaturePath)
for feature in featuresList:
	arcpy.AddMessage(feature)
	featurePath_regular = gdbPath + feature
	currentFields = []
	if feature[len(featuresRoot):len(featuresRoot)+4] <> "topo":
		if not feature[len(featuresRoot):] in featuresToIgnore:
			projectFields = projectsFeatureFields.get(feature[len(featuresRoot):])
			for field in projectFields:
				featureField = featuresFields.get(field)
				currentFields.append(featureField)
				arcpy.AlterField_management(tempProjectsFeaturePath, field, featureField,"")
		arcpy.Append_management(tempProjectsFeaturePath, featurePath_regular, "NO_TEST")
		for field in currentFields:
			if not field == "project_code":
				arcpy.DeleteField_management(tempProjectsFeaturePath, field)

stopTime = time.time()
arcpy.AddMessage("Time to move features to proposed_trails = %02d:%02d:%02d" % (int(stopTime-startTime)/3600,int(((stopTime-startTime)%3600)/60),int((stopTime-startTime)%60)))