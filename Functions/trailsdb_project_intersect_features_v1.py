import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from trailsdb_project_features_by_type_v1 import projectFeatures_v1
from Build_SQL_Where_Clause import *

'''Return the following for other scripts:

#Get temporary intersection of project's line features and temporary copies of project's point features
tempProjectFeatures = projectProposedIntersect_v1(project_code,reg_date,database_version)
tempIntersectionPathStr = tempFeatures[0]
pointsTempFeaturesList = tempFeatures[1]
pointsTempFeaturesCorrespondingRegisteredFeaturesDict = tempFeatures[2]

'''

#Editing gdb variables
intersectionFeaturePath = tempEditingGdbPath + "\\intersect"

def projectProposedIntersect_v1(project_code,reg_date,database_version):

	# Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbName = gdbVariables[0]
	gdbPath = gdbVariables[1]
	gdbFeaturesRoot = gdbVariables[2]

	# Remove temp feature that might have been left before in editing gdb
	if arcpy.Exists(intersectionFeaturePath):
		arcpy.Delete_management(intersectionFeaturePath)

	# Get project features variables from trailsdb
	projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
	projectLinesFeaturesNamesList = projectFeaturesVariable[0]
	projectLinesFeaturesNamesandPathsDict = projectFeaturesVariable[2]
	projectPointsFeaturesNamesList = projectFeaturesVariable[4]
	projectPointsFeaturesNamesandPathsDict = projectFeaturesVariable[6]

	# Intersect polylines features and add a registration date
	linesIntersectList = []
	arcpy.AddMessage("  Copying project data")
	for currentFeature in projectLinesFeaturesNamesList:
		# Create temp feature with info from project
		# Trailsdb feature path
		currentFeaturePath = projectLinesFeaturesNamesandPathsDict.get(currentFeature)
		# temp feature in memory
		currentTempFeatureName = "temp_" + currentFeature
		if arcpy.Exists(currentTempFeatureName):
			arcpy.Delete_management(currentTempFeatureName)
		# temp feature path in c:\temp\trailsdb_editing
		currentTempFeaturePath = tempEditingGdbPath + "\\" + currentTempFeatureName
		if arcpy.Exists(currentTempFeaturePath):
			arcpy.Delete_management(currentTempFeaturePath)
		# Copying project to trailsdb_editing
		arcpy.MakeFeatureLayer_management(currentFeaturePath,currentTempFeatureName)
		whereClause = buildWhereClause(currentTempFeatureName, "project_code", project_code)
		arcpy.SelectLayerByAttribute_management(currentTempFeatureName,"NEW_SELECTION",whereClause)
		arcpy.CopyFeatures_management(currentTempFeatureName,currentTempFeaturePath)
		if not currentTempFeaturePath in linesIntersectList:
			linesIntersectList.append(currentTempFeaturePath)
	# Intersect all temp features and add and populate a date field
	# Exception for signage projects other than wayfinding (no line features)
	if not len(linesIntersectList) == 0:
		# Exception if there is main project feature is the only line feature (Signage only or trail project like a repair without new info), main trail
		if len(linesIntersectList) == 1:
			currentFeaturePath = linesIntersectList[0]
			currentTempFeatureName = "temp_main_feature"
			if arcpy.Exists(currentTempFeatureName):
				arcpy.Delete_management(currentTempFeatureName)
			arcpy.MakeFeatureLayer_management(currentFeaturePath,currentTempFeatureName)
			whereClause = buildWhereClause(currentTempFeatureName, "project_code", project_code)
			arcpy.SelectLayerByAttribute_management(currentTempFeatureName,"NEW_SELECTION",whereClause)
			arcpy.CopyFeatures_management(currentTempFeatureName,intersectionFeaturePath)
		# Intersect
		if not len(linesIntersectList) == 1:
			arcpy.Intersect_analysis(linesIntersectList, intersectionFeaturePath)
			arcpy.AddField_management(intersectionFeaturePath,"reg_date","DATE")
			dateCursor = arcpy.da.UpdateCursor(intersectionFeaturePath,"reg_date")
			for row in dateCursor:
				row[0] = reg_date
				dateCursor.updateRow(row)

	# Make temp point features
	pointsTempFeaturesList = []
	pointsTempFeaturesCorrespondingRegisteredFeaturesDict = {}
	for currentPointFeature in projectPointsFeaturesNamesList:
		currentPointFeaturePath = projectPointsFeaturesNamesandPathsDict.get(currentPointFeature)
		currentTempPointFeatureName = "temp_" + currentPointFeature
		registeredFeaturePath = gdbFeaturesRoot + currentPointFeature[:-3] + "reg"
		currentTempPointFeaturePath = tempEditingGdbPath + "\\" + currentTempPointFeatureName
		if arcpy.Exists(currentTempPointFeaturePath):
			arcpy.Delete_management(currentTempPointFeaturePath)
		arcpy.MakeFeatureLayer_management(currentPointFeaturePath,currentTempPointFeatureName)
		whereClause = buildWhereClause(currentTempPointFeatureName, "project_code", project_code)
		arcpy.SelectLayerByAttribute_management(currentTempPointFeatureName,"NEW_SELECTION",whereClause)
		arcpy.CopyFeatures_management(currentTempPointFeatureName,currentTempPointFeaturePath)
		pointsTempFeaturesList.append(currentTempPointFeaturePath)
		pointsTempFeaturesCorrespondingRegisteredFeaturesDict.update({currentTempPointFeaturePath:registeredFeaturePath})
	return intersectionFeaturePath,pointsTempFeaturesList,pointsTempFeaturesCorrespondingRegisteredFeaturesDict