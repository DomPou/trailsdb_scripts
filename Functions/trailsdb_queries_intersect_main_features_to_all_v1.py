import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from trailsdb_queries_Intersect_Two_Feature_Classes_v1 import intersectFeatureClassesFromTrailsdb_returnName_v1


#Trailsdb
statusList = ["reg","pro"]
mainFeatureList = ["trail_code","project_trail","manager","owner"]
datasetsDict = {"reg":"registered_info","pro":"proposed_info"}
intersectFeaturesList = []

def intersectMainFeaturesToAll_v1(database_version):
	'''Intersect main features to all others in trailsdb_queries'''

	# General Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbPath = gdbVariables[1]
	gdbFeaturesRoot = gdbVariables[2]

	#Registered or proposed
	for status in statusList:
		#Main feature to intersect everything to
		for currentMainFeature in mainFeatureList:
			currentDataset = datasetsDict.get(status)
			#Feature containing the main code for the final intersect
			mainFeatureName = "fc_" + currentMainFeature + "_" + status
			mainFeaturePath = gdbFeaturesRoot + mainFeatureName
			arcpy.env.workspace = gdbPath + currentDataset + "\\"
			#List all line features in proper dataset other than the main feature
			for featureWithRoot in arcpy.ListFeatureClasses():
				if not mainFeatureName in featureWithRoot:
					if arcpy.Describe(featureWithRoot).shapeType == "Polyline":
						pathLength = len(gdbFeaturesRoot)
						featurePath = gdbPath + featureWithRoot
						featureName = featurePath[pathLength:]
						print featureName
						intersectFeatureName = intersectFeatureClassesFromTrailsdb_returnName_v1(mainFeatureName,featureName,database_version)
						intersectFeaturesList.append(intersectFeatureName)

	return intersectFeaturesList

#print intersectMainFeaturesToAll_v1(database_version)