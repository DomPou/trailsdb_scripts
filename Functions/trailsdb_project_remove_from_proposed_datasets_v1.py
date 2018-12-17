import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from trailsdb_project_features_by_type_v1 import projectFeatures_v1
from Build_SQL_Where_Clause import *

def removeProjectFromProposedDatasets_v1(project_code,database_version):

	# Get project features variables from trailsdb
	projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
	projectLinesFeaturesPathsList = projectFeaturesVariable[1]
	projectPointsFeaturesPathsList = projectFeaturesVariable[5]
	# Uses delete features to remove all geometries from this project
	for lineFeature in projectLinesFeaturesPathsList:
		if arcpy.Exists("currentTemp"):
			arcpy.Delete_management("currentTemp")
		arcpy.MakeFeatureLayer_management(lineFeature,"currentTemp")
		whereClause = buildWhereClause("currentTemp", "project_code", project_code)
		arcpy.SelectLayerByAttribute_management("currentTemp","NEW_SELECTION",whereClause)
		arcpy.DeleteFeatures_management("currentTemp")
	for pointFeature in projectPointsFeaturesPathsList:
		if arcpy.Exists("currentTemp"):
			arcpy.Delete_management("currentTemp")
		arcpy.MakeFeatureLayer_management(pointFeature,"currentTemp")
		whereClause = buildWhereClause("currentTemp", "project_code", project_code)
		arcpy.SelectLayerByAttribute_management("currentTemp","NEW_SELECTION",whereClause)
		arcpy.DeleteFeatures_management("currentTemp")
