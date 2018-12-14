import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from salesforce_objects_projects_stage_and_classification_v1 import projectStageAndClassification_v1

# Variables
RegisteredProjectsStages = ["Closed", "Complete"]

# Check in salesforce_objects if a project should be in a proposed or registered dataset
def projectProposedOrRegistered_v1(project_code):

	# salesforce_objects data
	projectVariables = projectStageAndClassification_v1(project_code)
	projectStageStr = projectVariables[3]

	dataset = ""
	if projectStageStr in RegisteredProjectsStages:
		dataset = "Registered"
	if not projectStageStr in RegisteredProjectsStages:
		dataset = "Proposed"

	return dataset, projectStageStr
