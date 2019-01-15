import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from trailsdb_queries_intersect_main_features_to_all_v1 import intersectMainFeaturesToAll_v1

# General Variables
# database_version = trailsdb or trailsdb_tests
database_version = "trailsdb_tests"
gdbVariables = trailsdb_or_tests(database_version)
gdbName = gdbVariables[0]
gdbPath = gdbVariables[1]
gdbFeaturesRoot = gdbVariables[2]

# Trailsdb
statusList = ["reg","pro"]
#mainFeatureList = ["trail_code","project_trail","manager","owner"]
mainFeatureList = ["trail_code"]

# Trailsdb_queries
intersectedFeaturesDict = intersectMainFeaturesToAll_v1(database_version)

for status in statusList:
	for currentMainFeature in mainFeatureList:
		intersectFeaturesList = intersectedFeaturesDict.get(currentMainFeature + "_" + status)
		for currentFeature in intersectFeaturesList:
			print currentFeature


