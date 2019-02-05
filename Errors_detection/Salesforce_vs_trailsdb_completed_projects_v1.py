import sys, arcpy, smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *
from GIS_email_variables import *

sys.path.append(functionsFolder)
from salesforce_objects_projects_stage_and_classification_v1 import projectStageAndClassification_v1


def trailsdbErrorsEmail_CompletedProjectNotRegistered(projectCode,projectType,projectSubtypes):

	msg = MIMEMultipart()
	subject = "Trailsdb error - " + projectType + " project completed in Salesforce"
	body = """
Project completed in Salesforce but not registered in trailsdb

Project Code:
project_code = """ + str(projectCode) + """

Project Type: 
""" + projectType + """

Project Subtype(s):
""" + str(projectSubtypes) + """
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

def completedProjects():
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
	projectsTableField = "projectcode__c"
	projectsTypesRegisteredInTrailsdb = ["Construction","Signage","Registration"]
	projectsSubtypesRegisteredInTrailsdb = ["Infrastructure","Interpretive Signage Project","Trailhead Project"]
	projectsStagesRegisteredInTraillsdb = ["Complete","Closed"]
	projectCodesSFList = []

	projectCodeSFCursor = arcpy.da.SearchCursor(projectsTablePath,projectsTableField)
	for row in projectCodeSFCursor:
		if not row[0] in projectCodesSFList:
			projectCodesSFList.append(row[0])


	# TrailsDB Info
	# 1 TRAIL Projects in proposed_info that should be registered
	projectsFeatureName = "fc_project_trail_pro"
	projectsFeaturePath = gdbFeaturesRoot + projectsFeatureName
	projectsFeatureField = "project_code"
	projectCodesTrailsdbList = []

	projectCodesTrailsdbCursor = arcpy.da.SearchCursor(projectsFeaturePath,projectsFeatureField)
	for row in projectCodesTrailsdbCursor:
		if not row[0] in projectCodesTrailsdbList:
			projectCodesTrailsdbList.append(row[0])

	for projectCodeTrailsdb in projectCodesTrailsdbList:
		projectFSalesforceVariable = projectStageAndClassification_v1(projectCodeTrailsdb)
		projectTypeInSalesforceStr = projectFSalesforceVariable[0]
		projectSubtypesInSalesforceList = projectFSalesforceVariable[1]
		projectStageInSalesforceStr = projectFSalesforceVariable[3]
		if projectTypeInSalesforceStr in projectsTypesRegisteredInTrailsdb:
			if projectStageInSalesforceStr in projectsStagesRegisteredInTraillsdb:
				trailsdbErrorsEmail_CompletedProjectNotRegistered(projectCodeTrailsdb,projectTypeInSalesforceStr,projectSubtypesInSalesforceList)

	# 2 INFRASTRUCTURE Projects in proposed_info that should be registered
	infrastructureFeatureName = "fc_project_infrastructure_pro"
	infrastructureFeaturePath = gdbFeaturesRoot + infrastructureFeatureName
	infrastructureFeatureField = "project_code"
	infrastructureCodesTrailsdbList = []

	infrastructureCodesTrailsdbCursor = arcpy.da.SearchCursor(infrastructureFeaturePath,infrastructureFeatureField)
	for row in infrastructureCodesTrailsdbCursor:
		if not row[0] in infrastructureCodesTrailsdbList:
			infrastructureCodesTrailsdbList.append(row[0])

	for infrastructureCodeTrailsdb in infrastructureCodesTrailsdbList:
		projectFSalesforceVariable = projectStageAndClassification_v1(infrastructureCodeTrailsdb)
		projectTypeInSalesforceStr = projectFSalesforceVariable[0]
		projectSubtypesInSalesforceList = projectFSalesforceVariable[1]
		projectStageInSalesforceStr = projectFSalesforceVariable[3]
		if projectTypeInSalesforceStr in projectsTypesRegisteredInTrailsdb:
			if projectStageInSalesforceStr in projectsStagesRegisteredInTraillsdb:
				if not len(projectSubtypesInSalesforceList) == 0:
					for subtype in projectSubtypesInSalesforceList:
						if subtype in projectsSubtypesRegisteredInTrailsdb:
							trailsdbErrorsEmail_CompletedProjectNotRegistered(infrastructureCodeTrailsdb,projectTypeInSalesforceStr,projectSubtypesInSalesforceList)

	# 3 WAYFINDING Projects in proposed_signage_info that should be registered
	wayfindingFeatureName = "fc_signage_trail_pro"
	wayfindingFeaturePath = gdbFeaturesRoot + wayfindingFeatureName
	wayfindingFeatureField = "project_code"
	wayfindingTrailsdbList = []

	wayfindingProjectCodesTrailsdbCursor = arcpy.da.SearchCursor(wayfindingFeaturePath,wayfindingFeatureField)
	for row in wayfindingProjectCodesTrailsdbCursor:
		if not row[0] in wayfindingTrailsdbList:
			wayfindingTrailsdbList.append(row[0])

	for wayfindingProjectCodeTrailsdb in wayfindingTrailsdbList:
		projectFSalesforceVariable = projectStageAndClassification_v1(projectCodeTrailsdb)
		projectTypeInSalesforceStr = projectFSalesforceVariable[0]
		projectSubtypesInSalesforceList = projectFSalesforceVariable[1]
		projectStageInSalesforceStr = projectFSalesforceVariable[3]
		if projectTypeInSalesforceStr in projectsTypesRegisteredInTrailsdb:
			if projectStageInSalesforceStr in projectsStagesRegisteredInTraillsdb:
				trailsdbErrorsEmail_CompletedProjectNotRegistered(wayfindingProjectCodeTrailsdb,projectTypeInSalesforceStr,projectSubtypesInSalesforceList)

	# 4 SIGNAGE Projects (other than Wayfinding) in proposed_signage_info that should be registered
	signageFeatureName = "fc_signage_post_pro"
	signageFeaturePath = gdbFeaturesRoot + signageFeatureName
	signageFeatureFields = ["project_code","signage_post_type"]
	signagePostsToRegister = [4,5,6,7]
	signageTrailsdbList = []

	signageProjectCodesTrailsdbCursor = arcpy.da.SearchCursor(signageFeaturePath,signageFeatureFields)
	for row in signageProjectCodesTrailsdbCursor:
		if not row[0] in signageTrailsdbList:
			if row[1] in signagePostsToRegister:
				signageTrailsdbList.append(row[0])

	for signageProjectCodeTrailsdb in signageTrailsdbList:
		projectFSalesforceVariable = projectStageAndClassification_v1(signageProjectCodeTrailsdb)
		projectTypeInSalesforceStr = projectFSalesforceVariable[0]
		projectSubtypesInSalesforceList = projectFSalesforceVariable[1]
		projectStageInSalesforceStr = projectFSalesforceVariable[3]
		if projectTypeInSalesforceStr in projectsTypesRegisteredInTrailsdb:
			if projectStageInSalesforceStr in projectsStagesRegisteredInTraillsdb:
				trailsdbErrorsEmail_CompletedProjectNotRegistered(signageProjectCodeTrailsdb,projectTypeInSalesforceStr,projectSubtypesInSalesforceList)

#completedProjects()