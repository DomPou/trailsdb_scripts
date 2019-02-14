import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from trailsdb_project_features_by_type_v1 import projectFeatures_inMemory_v1
from trailsdb_project_validate_data_by_type_v1 import projectDataValidation_inMemory_v1
from trailsdb_project_proposed_or_registered_v1 import projectProposedOrRegistered_inMemory_v1
from trailsdb_project_register_after_validation_v1 import registerValidatedProject_v1
from trailsdb_project_remove_from_proposed_datasets_v1 import removeProjectFromProposedDatasets_v1

# User inputs variables
project_code_value = arcpy.GetParameter(0)
reg_date_value = arcpy.GetParameterAsText(1)

# General Variables
# database_version = trailsdb or trailsdb_tests
database_version = "trailsdb"
gdbVariables = trailsdb_or_tests(database_version)
gdbName = gdbVariables[0]
gdbPath = gdbVariables[1]
gdbFeaturesRoot = gdbVariables[2]
archivesFeaturePath = gdbFeaturesRoot + "fc_projects_archives"

arcpy.AddMessage("Registering project " + str(project_code_value) + " in " + database_version)

# 1 - VALIDATION
# Variables
finalValidation = "True"
allMissingFeatures = []
incompleteFeatures = []

# Check if project is complete or closed
projectStatusValidation = projectProposedOrRegistered_inMemory_v1(project_code_value)
projectDatasetStr = projectStatusValidation[0]
projectStageStr = projectStatusValidation[1]
if not projectDatasetStr == "Registered":
	arcpy.AddError("ERROR - Project is " + projectStageStr + " in Salesforce. Cannot continue registration process")
if projectDatasetStr == "Registered":
	arcpy.AddMessage("Project is " + projectStageStr + " in Salesforce. Registration process can continue.")

	# Getting features included in this project and list of essential features for this type of project
	arcpy.AddMessage("Identifying essential features for this project")
	projectFeaturesVariable = projectFeatures_inMemory_v1(project_code_value, database_version)
	projectNoMissingListValidation = projectFeaturesVariable[10]
	projectMissingListMessage = projectFeaturesVariable[11]

	# Checking for errors
	if projectNoMissingListValidation == "False":
		for errorMessage in projectMissingListMessage:
			arcpy.AddError(errorMessage)
	if projectNoMissingListValidation == "True":
		arcpy.AddMessage("Checking for errors in essential features")
		projectValidationVariables = projectDataValidation_inMemory_v1(project_code_value, database_version)
		projectEssentialFeaturesValidationStatusStr = projectValidationVariables[0]
		projectEssentialFeaturesValidationMissingList = projectValidationVariables[1]
		projectFeaturesLengthValidationStatusStr = projectValidationVariables[2]
		projectFeaturesLengthErrorsList = projectValidationVariables[3]
		if projectEssentialFeaturesValidationStatusStr == "False":
			arcpy.AddError("ERROR - essential feature(s) missing")
			for missingFeature in projectEssentialFeaturesValidationMissingList:
				arcpy.AddMessage("  " + missingFeature)
		if projectFeaturesLengthValidationStatusStr == "False":
			arcpy.AddError("ERROR - feature(s) not identical to fc_project_trail_pro")
			for incorrectFeature in projectFeaturesLengthErrorsList:
				arcpy.AddMessage("  " + incorrectFeature)
		# Proceed if there is no error for this project
		if not projectEssentialFeaturesValidationStatusStr == "False" and not projectFeaturesLengthValidationStatusStr == "False":
			arcpy.AddMessage("Project validated - Registering project")
			arcpy.AddMessage("  Moving project to archive and registered_info")
			registerValidatedProject_v1(project_code_value, reg_date_value, database_version)
			arcpy.AddMessage("  Removing project from proposed datasets")
			removeProjectFromProposedDatasets_v1(project_code_value, database_version)
			arcpy.RefreshActiveView()
