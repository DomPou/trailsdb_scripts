import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from trailsdb_project_features_by_type_v1 import projectFeatures_v1
from trailsdb_project_intersect_features_v1 import projectProposedIntersect_v1


# Project code, registration date, trailsdb or trailsdb_test
def registerValidatedProject_v1(project_code,reg_date,database_version):

	# Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbFeaturesRoot = gdbVariables[2]
	archivesFeaturePath = gdbFeaturesRoot + "fc_projects_archives"

	# Get project features variables from trailsdb
	projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
	projectLinesFeaturesPathsList = projectFeaturesVariable[1]
	projectFeatureNameCorrespondingRegisteredPath = projectFeaturesVariable[12]
	operationalDateRequiredStr = projectFeaturesVariable[13]

	# Get temporary intersection of project's line features and temporary copies of project's point features
	tempProjectFeatures = projectProposedIntersect_v1(project_code,reg_date,database_version)
	tempIntersectionPathStr = tempProjectFeatures[0]
	pointsTempFeaturesList = tempProjectFeatures[1]
	pointsTempFeaturesCorrespondingRegisteredFeaturesDict = tempProjectFeatures[2]

	# Append Archive
	arcpy.AddMessage("      Archive")
	try:
		arcpy.Append_management(tempIntersectionPathStr,archivesFeaturePath,"NO_TEST")
	# Exception for signage projects other than wayfinding (no line features)
	except:
		arcpy.AddMessage("          Study or Signage project other than wayfinding. Does not need to be archived")
	# Append line features of project (list of REGISTERED features)
	arcpy.AddMessage("      Line Features")
	for currentLineFeature in projectLinesFeaturesPathsList:
		registeredLineFeature = projectFeatureNameCorrespondingRegisteredPath.get(currentLineFeature)
		arcpy.AddMessage("          " + registeredLineFeature)
		arcpy.Append_management(tempIntersectionPathStr,registeredLineFeature,"NO_TEST")
	if operationalDateRequiredStr == "True":
		arcpy.AddMessage("          " + gdbFeaturesRoot + "fc_operational_date_reg")
		arcpy.Append_management(tempIntersectionPathStr,gdbFeaturesRoot + "fc_operational_date_reg","NO_TEST")
	# Append point features of project (list of TEMP features)
	arcpy.AddMessage("      Point Features")
	for currentTempPointFeature in pointsTempFeaturesList:
		# Feature to append to
		registeredPointFeature = pointsTempFeaturesCorrespondingRegisteredFeaturesDict.get(currentTempPointFeature)
		arcpy.AddMessage("          " + registeredPointFeature)
		arcpy.Append_management(currentTempPointFeature,registeredPointFeature,"NO_TEST")
