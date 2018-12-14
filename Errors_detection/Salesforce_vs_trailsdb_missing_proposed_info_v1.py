'''
THIS SCRIPT ONLY LOOK AT THE PROPOSED_INFO FEATURES BECAUSE THE SIGNAGE INFORMATION USUALLY COMES LATER

'''

import sys, arcpy, smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *
from GIS_email_variables import *

sys.path.append(functionsFolder)
from salesforce_objects_projects_stage_and_classification_v1 import projectStageAndClassification_v1
from trailsdb_project_validate_data_by_type_v1 import projectDataValidation_v1
from trailsdb_project_proposed_or_registered_v1 import projectProposedOrRegistered_v1



# General Variables
# database_version = trailsdb or trailsdb_tests
database_version = "trailsdb"
gdbVariables = trailsdb_or_tests(database_version)
gdbName = gdbVariables[0]
gdbPath = gdbVariables[1]
gdbFeaturesRoot = gdbVariables[2]
archivesFeaturePath = gdbFeaturesRoot + "fc_projects_archives"

# Salesforce Info
projectsTableName = "opportunity"
projectsTablePath = gdbSalesforceRoot + projectsTableName
projectsTableFields = ["id", "projectcode__c"]
requirementsTableName = "opportunityrequirement__c"
requirementsTablePath = gdbSalesforceRoot + requirementsTableName
requirementsTableFields = ["name", "opportunityname__c", "status__c"]
gisRequirementStr = "GIS alignment / Signage plan"
projectCodesSFList = []
salesforceIdProjectCodeDict = {}
projectIdGisDoneList = []
proposedProjectCodesSFList = []

def trailsdbErrorsEmail_IncompleteProjectInProposedInfo(projectCode, missingEssentialList, wrongLengthList):

	msg = MIMEMultipart()
	subject = "Trailsdb error - Incomplete Project in Proposed_info or proposed_signage_info"
	body = """
Incomplete Project in Proposed_info or proposed_signage_info

Project Code:
project_code = """ + str(projectCode) + """

Missing essential(s): 
""" + '\r\n'.join(missingEssentialList) + """

Wrong Length(s):
""" + '\r\n'.join(wrongLengthList) + """
    """

	msg['From'] = gisAddress
	msg['To'] = trailsdbErrorsAddress
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain', "utf-8"))
	text=msg.as_string()
	# Send the message via our SMTP server
	server = smtplib.SMTP('smtp.office365.com', 587)
	server.ehlo()
	server.starttls()
	server.login(gisAddress, gisPassword)
	server.sendmail(gisAddress, trailsdbErrorsAddress, text)
	server.quit()

# List of project code in Salesforce
projectCodeSFCursor = arcpy.da.SearchCursor(projectsTablePath,projectsTableFields)
for row in projectCodeSFCursor:
	if not row[1] in projectCodesSFList:
		projectCodesSFList.append(row[1])
		salesforceIdProjectCodeDict.update({row[0]:row[1]})


# List project with GIS alignment / Signage plan is set to Done in Salesforce
requirementSearchCursor = arcpy.da.SearchCursor(requirementsTablePath,requirementsTableFields)
for row in requirementSearchCursor:
	if row[0] == gisRequirementStr:
		if row[2] == "Done":
			currentProjectCode = salesforceIdProjectCodeDict.get(row[1])
			if not currentProjectCode in projectIdGisDoneList:
				projectIdGisDoneList.append(currentProjectCode)



notRequiredInTrailsdbList = ["Cancelled", "New", "Under Review", "Eligible - Postponed", "Submit for Approval", "Committe Review", "Ineligible", "Eligible - Rejected"]
for projectSF in projectCodesSFList:
	# Check if project GIS is set to Done
	if projectSF in projectIdGisDoneList:
		# Check if project is proposed and add to list
		projectStatusValidation = projectProposedOrRegistered_v1(projectSF)
		projectDatasetStr = projectStatusValidation[0]
		projectStageStr = projectStatusValidation[1]
		if projectDatasetStr == "Proposed":
			# Check if project was not cancelled
			# Get project features variables from Salesforce
			projectFSalesforceVariable = projectStageAndClassification_v1(projectSF)
			projectStageInSalesforceStr = projectFSalesforceVariable[3]
			if not projectStageInSalesforceStr in notRequiredInTrailsdbList:
				if not projectSF in proposedProjectCodesSFList:
					proposedProjectCodesSFList.append(projectSF)

for proposedProject in proposedProjectCodesSFList:
	# Getting features included in this project and list of essential features for this type of project
	projectValidationVariables = projectDataValidation_v1(proposedProject, database_version)
	projectFeaturesLengthValidationStatusStr = projectValidationVariables[2]
	projectFeaturesLengthErrorsList = projectValidationVariables[3]
	projectEssentialFeaturesValidationStatusCONSTRUCTIONStr = projectValidationVariables[4]
	projectEssentialFeaturesValidationMissingCONSTRUCTIONList = projectValidationVariables[5]
	projectFeaturesLengthDoubleList = projectValidationVariables[6]
	# Send email for errors in projects
	if projectEssentialFeaturesValidationStatusCONSTRUCTIONStr == "False" or (projectFeaturesLengthValidationStatusStr == "False" and projectFeaturesLengthDoubleList == "False"):
		trailsdbErrorsEmail_IncompleteProjectInProposedInfo(proposedProject, projectEssentialFeaturesValidationMissingCONSTRUCTIONList, projectFeaturesLengthErrorsList)