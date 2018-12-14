import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from salesforce_objects_projects_stage_and_classification_v1 import projectStageAndClassification_v1

'''Return the following for other scripts:

#Get project features variables from trailsdb
projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
projectLinesFeaturesNamesList = projectFeaturesVariable[0]
projectLinesFeaturesPathsList = projectFeaturesVariable[1]
projectLinesFeaturesNamesandPathsDict = projectFeaturesVariable[2]
projectLinesFeaturesPathsAndNamesDict = projectFeaturesVariable[3]
projectPointsFeaturesNamesList = projectFeaturesVariable[4]
projectPointsFeaturesPathsList = projectFeaturesVariable[5]
projectPointsFeaturesNamesandPathsDict = projectFeaturesVariable[6]
projectPointsFeaturesPathsandNamesDict = projectFeaturesVariable[7]
projectEssentialLinesFeaturesNamesList = projectFeaturesVariable[8]
projectEssentialPointsFeaturesNamesList = projectFeaturesVariable[9]
noMissingListValidationStr = projectFeaturesVariable[10]
missingCombinationMessageList = projectFeaturesVariable[11]
projectCorrespondingRegisteredPath = projectFeaturesVariable[12]
operationalDateRequiredStr = projectFeaturesVariable[13]
projectMainFeaturePathStr = projectFeaturesVariable[14]
projectEssentialLinesFeaturesNamesCONSTRUCTIONList = projectFeaturesVariable[15]
projectEssentialPointsFeaturesNamesCONSTRUCTIONList = projectFeaturesVariable[16]

'''

# List of essential features for types + subtypes + state in Salesforce
salesforceTypesSubtypesStatesEssentials = {
	"Study_Trail_New":["None"],
	"Study_Trail_Existing":["None"],
	"Study_Infrastructure_New":["None"],
	"Study_Infrastructure_Existing":["None"],
	"Study_Re-routing_New":["not used yet"],
	"Study_Re-routing_Existing":["not used yet"],
	"Study_Other_New":["not used yet"],
	"Study_Other_Existing":["None"],
	"Construction_Trail_New":[
		"fc_act_cross_country_skiing_pro",
		"fc_act_dog_sledding_pro",
		"fc_act_fat_biking_pro",
		"fc_act_horseback_riding_pro",
		"fc_act_mountain_biking_pro",
		"fc_act_paddling_pro",
		"fc_act_road_cycling_pro",
		"fc_act_rollerblading_pro",
		"fc_act_snowmobiling_pro",
		"fc_act_snowshoeing_pro",
		"fc_act_walking_pro",
		"fc_atv_pro",
		"fc_category_pro",
		"fc_environment_pro",
		"fc_gis_data_pro",
		"fc_local_trail_pro",
		"fc_manager_pro",
		"fc_network_pro",
		"fc_owner_pro",
		"fc_project_trail_pro",
		"fc_trail_code_pro",
		"fc_trail_type_pro"
	],
	"Construction_Trail_Existing":["fc_project_trail_pro"],
	"Construction_Infrastructure_New":["fc_project_infrastructure_pro"],
	"Construction_Infrastructure_Existing":["None"],
	"Construction_Re-routing_New":["not used yet"],
	"Construction_Re-routing_Existing":["not used yet"],
	"Construction_Wayfinding Signage_New":["fc_signage_trail_pro","fc_signage_post_pro"],
	"Construction_Wayfinding Signage_Existing":["fc_signage_trail_pro","fc_signage_post_pro"],
	"Construction_Interpretive Signage Project_New":["not used yet"],
	"Construction_Interpretive Signage Project_Existing":["not used yet"],
	"Construction_Trailhead Project_New":["not used yet"],
	"Construction_Trailhead Project_Existing":["fc_signage_post_pro"],
	"Construction_Other_New":["not used yet"],
	"Construction_Other_Existing":["not used yet"],
	"Signage_Wayfinding Signage_New":["fc_signage_trail_pro","fc_signage_post_pro"],
	"Signage_Wayfinding Signage_Existing":["fc_signage_trail_pro","fc_signage_post_pro"],
	"Signage_Additional Cautionary Signage_New":["fc_signage_post_pro"],
	"Signage_Additional Cautionary Signage_Existing":["fc_signage_post_pro"],
	"Signage_Interpretive Signage Project_New":["fc_signage_post_pro"],
	"Signage_Interpretive Signage Project_Existing":["fc_signage_post_pro"],
	"Signage_Trailhead Project_New":["fc_signage_post_pro"],
	"Signage_Trailhead Project_Existing":["fc_signage_post_pro"],
	"Signage_Comprehensive Signage Project_New":["fc_signage_post_pro"],
	"Signage_Comprehensive Signage Project_Existing":["fc_signage_post_pro"],
	"Signage_Funding Only Request_New":["not used yet"],
	"Signage_Funding Only Request_Existing":["not used yet"],
	"Signage_Other_New":["not used yet"],
	"Signage_Other_Existing":["not used yet"],
	"Registration_Trail_New":["not used yet"],
	"Registration_Trail_Existing":["not used yet"],
	"Registration_Infrastructure_New":["not used yet"],
	"Registration_Infrastructure_Existing":["not used yet"],
	"Registration_Re-routing_New":["not used yet"],
	"Registration_Re-routing_Existing":["not used yet"],
	"Registration_Wayfinding Signage_New":["not used yet"],
	"Registration_Wayfinding Signage_Existing":["not used yet"],
	"Registration_Additional Cautionary Signage_New":["not used yet"],
	"Registration_Additional Cautionary Signage_Existing":["not used yet"],
	"Registration_Interpretive Signage Project_New":["not used yet"],
	"Registration_Interpretive Signage Project_Existing":["not used yet"],
	"Registration_Trailhead Project_New":["not used yet"],
	"Registration_Trailhead Project_Existing":["not used yet"],
	"Registration_Comprehensive Signage Project_New":["not used yet"],
	"Registration_Comprehensive Signage Project_Existing":["not used yet"],
	"Registration_Funding Only Request_New":["not used yet"],
	"Registration_Funding Only Request_Existing":["not used yet"],
	"Registration_Other_New":["not used yet"],
	"Registration_Other_Existing":["not used yet"],
	"Special_Funding Only Request_New":["not used yet"],
	"Special_Funding Only Request_Existing":["not used yet"],
	"Special_Trail Counters_New":["not used yet"],
	"Special_Trail Counters_Existing":["not used yet"],
	"Special_Other_New":["not used yet"],
	"Special_Other_Existing":["not used yet"]
}

# Operational date required or not
salesforceTypesSubtypesStatesOperationalDate = {
	"Study_Trail_New":"False",
	"Study_Trail_Existing":"False",
	"Study_Infrastructure_New":"False",
	"Study_Infrastructure_Existing":"False",
	"Study_Re-routing_New":"not used yet",
	"Study_Re-routing_Existing":"not used yet",
	"Study_Other_New":"not used yet",
	"Study_Other_Existing":"False",
	"Construction_Trail_New":"True",
	"Construction_Trail_Existing":"False",
	"Construction_Infrastructure_New":"False",
	"Construction_Infrastructure_Existing":"False",
	"Construction_Re-routing_New":"not used yet",
	"Construction_Re-routing_Existing":"not used yet",
	"Construction_Wayfinding Signage_New":"False",
	"Construction_Wayfinding Signage_Existing":"False",
	"Construction_Interpretive Signage Project_New":"not used yet",
	"Construction_Interpretive Signage Project_Existing":"not used yet",
	"Construction_Trailhead Project_New":"not used yet",
	"Construction_Trailhead Project_Existing":"False",
	"Construction_Other_New":"not used yet",
	"Construction_Other_Existing":"not used yet",
	"Signage_Wayfinding Signage_New":"False",
	"Signage_Wayfinding Signage_Existing":"False",
	"Signage_Additional Cautionary Signage_New":"False",
	"Signage_Additional Cautionary Signage_Existing":"False",
	"Signage_Interpretive Signage Project_New":"False",
	"Signage_Interpretive Signage Project_Existing":"False",
	"Signage_Trailhead Project_New":"False",
	"Signage_Trailhead Project_Existing":"False",
	"Signage_Comprehensive Signage Project_New":"False",
	"Signage_Comprehensive Signage Project_Existing":"False",
	"Signage_Funding Only Request_New":"not used yet",
	"Signage_Funding Only Request_Existing":"not used yet",
	"Signage_Other_New":"not used yet",
	"Signage_Other_Existing":"not used yet",
	"Registration_Trail_New":"not used yet",
	"Registration_Trail_Existing":"not used yet",
	"Registration_Infrastructure_New":"not used yet",
	"Registration_Infrastructure_Existing":"not used yet",
	"Registration_Re-routing_New":"not used yet",
	"Registration_Re-routing_Existing":"not used yet",
	"Registration_Wayfinding Signage_New":"not used yet",
	"Registration_Wayfinding Signage_Existing":"not used yet",
	"Registration_Additional Cautionary Signage_New":"not used yet",
	"Registration_Additional Cautionary Signage_Existing":"not used yet",
	"Registration_Interpretive Signage Project_New":"not used yet",
	"Registration_Interpretive Signage Project_Existing":"not used yet",
	"Registration_Trailhead Project_New":"not used yet",
	"Registration_Trailhead Project_Existing":"not used yet",
	"Registration_Comprehensive Signage Project_New":"not used yet",
	"Registration_Comprehensive Signage Project_Existing":"not used yet",
	"Registration_Funding Only Request_New":"not used yet",
	"Registration_Funding Only Request_Existing":"not used yet",
	"Registration_Other_New":"not used yet",
	"Registration_Other_Existing":"not used yet",
	"Special_Funding Only Request_New":"not used yet",
	"Special_Funding Only Request_Existing":"not used yet",
	"Special_Trail Counters_New":"not used yet",
	"Special_Trail Counters_Existing":"not used yet",
	"Special_Other_New":"not used yet",
	"Special_Other_Existing":"not used yet"
}

# For a project, returns all features names and paths containing related data and list of features names and paths
# that SHOULD contain data for this project
def projectFeatures_v1(project_code, database_version):

	# Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbPath = gdbVariables[1]
	gdbFeaturesRoot = gdbVariables[2]

	projectVariables = projectStageAndClassification_v1(project_code)
	projectTypeStr = projectVariables[0]
	projectSubtypesList = projectVariables[1]
	projectStateStr = projectVariables[2]

	project_Lines_Features_Names = []
	project_Lines_Features_Paths = []
	project_Lines_Features_Names_and_Paths = {}
	project_Lines_Features_Path_and_Names = {}
	project_Points_Features_Names = []
	project_Points_Features_Paths = []
	project_Points_Features_Names_and_Paths = {}
	project_Points_Features_Paths_and_Names = {}
	essential_Lines_Features_Names = []
	essential_Points_Features_Names = []
	project_Corresponding_Registered_Path = {}
	essential_Lines_Features_Names_CONSTRUCTION = []
	essential_Points_Features_Names_CONSTRUCTION = []

	# 1 - List of features names and paths that DO contain data for the project
	# list project features in proposed_info other than fc_project_pro
	arcpy.env.workspace = gdbPath + "proposed_info\\"
	for featureWithRoot in arcpy.ListFeatureClasses():
		pathLength = len(gdbFeaturesRoot)
		featurePath = gdbPath + featureWithRoot
		featureName = featurePath[pathLength:]
		if not "fc_project_pro" in featureWithRoot:
			cursor = arcpy.da.SearchCursor(featureWithRoot,"project_code")
			for row in cursor:
				if row[0] == project_code:
					if arcpy.Describe(featureWithRoot).shapeType == "Polyline":
						if not featureName in project_Lines_Features_Names:
							project_Lines_Features_Names.append(featureName)
						if not featurePath in project_Lines_Features_Paths:
							project_Lines_Features_Paths.append(featurePath)
						project_Lines_Features_Names_and_Paths.update({featureName:featurePath})
						project_Lines_Features_Path_and_Names.update({featurePath:featureName})
						project_Corresponding_Registered_Path.update({featurePath:featurePath[:-3] + "reg"})
					if arcpy.Describe(featureWithRoot).shapeType == "Point":
						if not featureName in project_Points_Features_Names:
							project_Points_Features_Names.append(featureName)
						if not featurePath in project_Points_Features_Paths:
							project_Points_Features_Paths.append(featurePath)
						project_Points_Features_Names_and_Paths.update({featureName:featurePath})
						project_Points_Features_Paths_and_Names.update({featurePath:featureName})
	# list project features in proposed_signage_info other than fc_project_signage_pro
	arcpy.env.workspace = gdbPath + "proposed_signage_info\\"
	for featureWithRoot in arcpy.ListFeatureClasses():
		pathLength = len(gdbFeaturesRoot)
		featurePath = gdbPath + featureWithRoot
		featureName = featurePath[pathLength:]
		if not "fc_project_signage_pro" in featureWithRoot:
			cursor = arcpy.da.SearchCursor(featureWithRoot,"project_code")
			for row in cursor:
				if row[0] == project_code:
					if arcpy.Describe(featureWithRoot).shapeType == "Polyline":
						if not featureName in project_Lines_Features_Names:
							project_Lines_Features_Names.append(featureName)
						if not featurePath in project_Lines_Features_Paths:
							project_Lines_Features_Paths.append(featurePath)
						project_Lines_Features_Names_and_Paths.update({featureName:featurePath})
						project_Lines_Features_Path_and_Names.update({featurePath:featureName})
						project_Corresponding_Registered_Path.update({featurePath:featurePath[:-3] + "reg"})
					if arcpy.Describe(featureWithRoot).shapeType == "Point":
						if not featureName in project_Points_Features_Names:
							project_Points_Features_Names.append(featureName)
						if not featurePath in project_Points_Features_Paths:
							project_Points_Features_Paths.append(featurePath)
						project_Points_Features_Names_and_Paths.update({featureName:featurePath})
						project_Points_Features_Paths_and_Names.update({featurePath:featureName})
	# 2 - List of features that SHOULD contain data for the project
	no_Missing_List_Validation = "True"
	operational_Date_Required = "False"
	missing_Combination_Message_List = []
	# create list from subtypes in salesforce_objects table
	for current_project_subtype in projectSubtypesList:
		# Filter projects without subtypes (Special)
		if not current_project_subtype is None:
			currentTypesSubtypesStates = projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr
			currentEssentialsList = salesforceTypesSubtypesStatesEssentials.get(currentTypesSubtypesStates)
			currentOperationalDateRequirement = salesforceTypesSubtypesStatesOperationalDate.get(currentTypesSubtypesStates)
			# Return error message for list not created yet
			if currentEssentialsList is None:
				no_Missing_List_Validation = "False"
				missing_Combination_Message_List.append(projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr + " is a new combination in Salesforce. Modify trailsdb_project_features_by_type")
			if not currentEssentialsList is None:
				for currentFeature in currentEssentialsList:
					# Return error message for new combination in salesforce not in dictionnary
					if currentFeature == "not used yet":
						no_Missing_List_Validation = "False"
						missing_Combination_Message_List.append("First time a project " + currentTypesSubtypesStates + " is registered. Decide essential features needed and modify trailsdb_project_features_by_type")
					if not currentFeature == "not used yet":
						# Ignore projects with no essential features:
						if not currentFeature == "None":
							currentFeaturePath = gdbFeaturesRoot + currentFeature
							if arcpy.Describe(currentFeaturePath).shapeType == "Polyline":
								if not currentFeature in essential_Lines_Features_Names:
									essential_Lines_Features_Names.append(currentFeature)
									if not "signage" in currentFeature:
										essential_Lines_Features_Names_CONSTRUCTION.append(currentFeature)
							if arcpy.Describe(currentFeaturePath).shapeType == "Point":
								if not currentFeature in essential_Points_Features_Names:
									essential_Points_Features_Names.append(currentFeature)
									if not "signage" in currentFeature:
										essential_Points_Features_Names_CONSTRUCTION.append(currentFeature)
		# Check if an operational date has to be added
		if currentOperationalDateRequirement is None:
			no_Missing_List_Validation = "False"
			if not projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr + " is a new combination in Salesforce, modify trailsdb_project_features_by_type" in missing_Combination_Message_List:
				missing_Combination_Message_List.append(projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr + " is a new combination in Salesforce, modify trailsdb_project_features_by_type")
		if currentOperationalDateRequirement == "not used yet":
			no_Missing_List_Validation = "False"
			missing_Combination_Message_List.append("First time a project " + currentTypesSubtypesStates + " is registered, established if an operational date is required and modify trailsdb_project_features_by_type")
		# Change operational_Date_Required to true if any of the combinations returns True
		if currentOperationalDateRequirement == "True":
			operational_Date_Required = "True"

		# 3 - identify main project feature (fc_project_trail_pro or fc_signage_trail_pro)
		# project_Main_Feature_Path = "None"
		if projectTypeStr == "Signage":
			if "Wayfinding Signage" in projectSubtypesList:
				project_Main_Feature_Path = gdbFeaturesRoot + "fc_signage_trail_pro"
		if projectTypeStr == "Signage":
			if not "Wayfinding Signage" in projectSubtypesList:
				project_Main_Feature_Path = "None"
		if not projectTypeStr == "Signage":
			project_Main_Feature_Path = gdbFeaturesRoot + "fc_project_trail_pro"

	return project_Lines_Features_Names, project_Lines_Features_Paths, project_Lines_Features_Names_and_Paths, project_Lines_Features_Path_and_Names, project_Points_Features_Names, project_Points_Features_Paths, project_Points_Features_Names_and_Paths, project_Points_Features_Paths_and_Names, essential_Lines_Features_Names, essential_Points_Features_Names, no_Missing_List_Validation, missing_Combination_Message_List, project_Corresponding_Registered_Path, operational_Date_Required, project_Main_Feature_Path, essential_Lines_Features_Names_CONSTRUCTION, essential_Points_Features_Names_CONSTRUCTION
