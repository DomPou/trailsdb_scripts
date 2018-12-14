import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

'''Return the following for other scripts:

#Get project features variables from Salesforce
projectFSalesforceVariable = projectStageAndClassification_v1(project_code)
projectTypeInSalesforceStr = projectFSalesforceVariable[0]
projectSubtypesInSalesforceList = projectFSalesforceVariable[1]
projectStateInSalesforceStr = projectFSalesforceVariable[2]
projectStageInSalesforceStr = projectFSalesforceVariable[3]

'''

# Variables
salesforceOpportunity = gdbSalesforceRoot + "opportunity"
salesforceFields = ["projectcode__c","projecttype__c","projectsubtype__c","projectstate__c","stagename"]


def projectStageAndClassification_v1(project_code):
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
