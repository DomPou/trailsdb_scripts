import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(salesforceFolder)
from Get_objects_in_memory_v1 import *

'''Return the following for other scripts:

#Get project features variables from Salesforce
projectFSalesforceVariable = projectStageAndClassification_v1(project_code)
projectTypeInSalesforceStr = projectFSalesforceVariable[0]
projectSubtypesInSalesforceList = projectFSalesforceVariable[1]
projectStateInSalesforceStr = projectFSalesforceVariable[2]
projectStageInSalesforceStr = projectFSalesforceVariable[3]

'''

def projectStageAndClassification_v1(project_code):

	# Variables
	salesforceOpportunity = gdbSalesforceRoot + "opportunity"
	salesforceFields = ["projectcode__c", "projecttype__c", "projectsubtype__c", "projectstate__c", "stagename"]

	# Get project type
	# Empty variables to avoid return errors on server
	projectTypeInSF = ""
	projectSubtypesInSF = []
	projectStateInSF = ""
	projectStageInSF = ""

	projectTypeCursor = arcpy.da.SearchCursor(salesforceOpportunity, salesforceFields)
	for row in projectTypeCursor:
		if row[0] == project_code:
			projectTypeInSF = row[1]
			tempProjectSubtypesInSF = row[2]
			if not tempProjectSubtypesInSF is None:
				projectSubtypesInSF = row[2].split(', ')
			projectStateInSF = row[3]
			projectStageInSF = row[4]

	return projectTypeInSF, projectSubtypesInSF, projectStateInSF, projectStageInSF

def projectStageAndClassification_inMemory_v1(project_code):

	# Variables
	arcpy.AddMessage("  Getting project information from Salesforce")
	salesforceOpportunity = "in_memory\\opportunity"
	salesforceFields = ["projectcode__c", "projecttype__c", "projectsubtype__c", "projectstate__c", "stagename"]

	# Create temporary table
	salesforceObjects_inMemory("Opportunity")

	#if arcpy.Exists(salesforceOpportunity):
	#	for field in arcpy.ListFields(salesforceOpportunity):
	#		if field.name in salesforceFields:
	#			arcpy.AddMessage(field.name)

	# Get project type
	# Empty variables to avoid return errors on server
	projectTypeInSF = ""
	projectSubtypesInSF = []
	projectStateInSF = ""
	projectStageInSF = ""

	projectTypeCursor = arcpy.da.SearchCursor(salesforceOpportunity, salesforceFields)
	for row in projectTypeCursor:
		if row[0] == project_code:
			projectTypeInSF = row[1]
			tempProjectSubtypesInSF = row[2]
			if not tempProjectSubtypesInSF is None:
				projectSubtypesInSF = row[2].split(', ')
			projectStateInSF = row[3]
			projectStageInSF = row[4]
			arcpy.AddMessage(projectSubtypesInSF)

	return projectTypeInSF, projectSubtypesInSF, projectStateInSF, projectStageInSF