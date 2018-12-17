import arcpy, smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *
from GIS_email_variables import *

sys.path.append(functionsFolder)
from Build_SQL_Where_Clause import *

def trailsdbErrorsEmail_GISalignmentDone(projectCode):

	msg = MIMEMultipart()
	subject = "Trailsdb error - GIS alignment done in Salesforce"
	body = """
Gis Alignment done in Salesforce but not present in trails

Project Code:
project_code = """ + str(projectCode) + """
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

def gisDone():
	# Variables
	# Salesforce
	projectsTableName = "opportunity"
	projectsTablePath = gdbSalesforceRoot + projectsTableName
	projectsTableFields = ["id","projectcode__c","projecttype__c","projectsubtype__c","stagename","oldprojectcode__c"]
	requirementsTableName = "opportunityrequirement__c"
	requirementsTablePath = gdbSalesforceRoot + requirementsTableName
	requirementsTableFields = ["name","opportunityname__c","status__c"]
	gisRequirementStr = "GIS alignment / Signage plan"

	# trailsdb
	statusList = ["reg","pro"]
	alignmentFeatureRoot = gdbFeaturesRoot + "fc_project_trail_"
	alignmentSignageFeaturePath = gdbFeaturesRoot + "fc_signage_trail_"
	postSignageFeatureRoot = gdbFeaturesRoot + "fc_signage_post_"
	postSignageFeatureFields = ["project_code", "signage_post_type"]
	wayfindingValues = [1,2,3,8]
	infrastructureFeatureRoot = gdbFeaturesRoot + "fc_project_infrastructure_"

	projectIdAndCodeDict = {}
	projectIdGisDoneList = []
	projectCodeTrailsdbList = []

	# make a dict of project ids and codes
	projectsSearchCursor = arcpy.da.SearchCursor(projectsTablePath,projectsTableFields)
	for row in projectsSearchCursor:
		# ignore cancelled or ineligible projects
		if row[4] <> "Cancelled" and row[4] <> "Ineligible":
			# ignore studies
			if row[2] <> "Study":
				# ignore old projects because the data for them is not that good
				if row[5] is None:
					projectIdAndCodeDict.update({row[0]:row[1]})

	# make a list of project ids where the gis requirement is set to Done
	requirementSearchCursor = arcpy.da.SearchCursor(requirementsTablePath,requirementsTableFields)
	for row in requirementSearchCursor:
		if row[0] == gisRequirementStr:
			if row[2] == "Done":
				if not row[1] in projectIdGisDoneList:
					projectIdGisDoneList.append(row[1])


	# make a list of project codes in trailsdb
	# proposed and registered
	for status in statusList:
		projectPath = alignmentFeatureRoot + status
		signageAlignmentPath = alignmentSignageFeaturePath + status
		signagePostPath = postSignageFeatureRoot + status
		infrastructurePath = infrastructureFeatureRoot + status
		projectCodesSearchCursor = arcpy.da.SearchCursor(projectPath,"project_code")
		signageAlignmentSearchCursor = arcpy.da.SearchCursor(signageAlignmentPath,"project_code")
		signagePostSearchCursor = arcpy.da.SearchCursor(signagePostPath,postSignageFeatureFields)
		infrastructureSearchCursor = arcpy.da.SearchCursor(infrastructurePath,"project_code")
		for row in projectCodesSearchCursor:
			if not row[0] in projectCodeTrailsdbList:
				projectCodeTrailsdbList.append(row[0])
		for row in signageAlignmentSearchCursor:
			if not row[0] in projectCodeTrailsdbList:
				projectCodeTrailsdbList.append(row[0])
		for row in signagePostSearchCursor:
			if not row[1] in wayfindingValues:
				if not row[0] in projectCodeTrailsdbList:
					projectCodeTrailsdbList.append(row[0])
		for row in infrastructureSearchCursor:
			if not row[0] in projectCodeTrailsdbList:
				projectCodeTrailsdbList.append(row[0])

	# compare lists
	for projectId in projectIdGisDoneList:
		currentProjectCode = projectIdAndCodeDict.get(projectId)
		if not currentProjectCode is None and not currentProjectCode in projectCodeTrailsdbList:
			trailsdbErrorsEmail_GISalignmentDone(currentProjectCode)
