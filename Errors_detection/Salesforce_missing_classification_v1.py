import sys, arcpy, smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *
from GIS_email_variables import *

sys.path.append(functionsFolder)
from salesforce_objects_projects_stage_and_classification_v1 import projectStageAndClassification_v1

#Salesforce Info
projectsTableName = "opportunity"
projectsTablePath = gdbSalesforceRoot + projectsTableName
projectsTableFields = ["id", "projectcode__c"]

def salesforceErrorsEmail_MissingProjectClassification(projectCode,field):
	"""

	:rtype: object
	"""
	msg = MIMEMultipart()
	subject = "Salesforce error - " + field + " missing"
	body = """
Missing """ + field + """ in:
""" + str(projectCode) + """
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

#List of project code in Salesforce
projectCodesSFList = []
projectCodeSFCursor = arcpy.da.SearchCursor(projectsTablePath,projectsTableFields)
for row in projectCodeSFCursor:
	if not row[1] in projectCodesSFList:
		projectCodesSFList.append(row[1])

for project_code in projectCodesSFList:
	projectVariables = projectStageAndClassification_v1(project_code)
	projectTypeStr = projectVariables[0]
	projectSubtypesList = projectVariables[1]
	projectStateStr = projectVariables[2]
	if projectTypeStr is None:
		salesforceErrorsEmail_MissingProjectClassification(project_code, "Project Type")
	if len(projectSubtypesList) == 0:
		if not projectTypeStr == "Special" and not projectTypeStr == "Registration":
			salesforceErrorsEmail_MissingProjectClassification(project_code, "Project Subtypes")
	if projectStateStr is None:
		salesforceErrorsEmail_MissingProjectClassification(project_code, "Project State")
