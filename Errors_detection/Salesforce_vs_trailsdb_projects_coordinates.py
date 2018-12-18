import sys, arcpy, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *
from GIS_email_variables import *


def trailsdbErrorsEmail_missingInfoFromSaleforce_projectCode_coordinates(projectsCoordinatesList):

	msg = MIMEMultipart()
	subject = "Trailsdb error - fc_project_pro - Coordinates - Project Code not found in Trailsdb"
	body = """
Error found in trailsdb:
Feature class: fc_project_pro

Copy in a csv:

""" + '\r\n'.join(projectsCoordinatesList) + """
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

def projectsCoordinates():
	# Variables
	projectsTableName = "opportunity"
	projectsTablePath = gdbSalesforceRoot + projectsTableName
	projectsTableFields = ["projectcode__c", "coordinates__latitude__s", "coordinates__longitude__s"]
	projectsFeaturePath = gdbFeaturesRoot + "fc_project_pro"
	projectsFeatureField = "project_code"
	projectsSFList = []
	projectsSFLatitudeDict = {}
	projectsSFLongitudeDict = {}
	projectsTrailsdbList = []
	csvList = ["project_code,latitude,longitude"]
	csvListChanged = 0

	searchCursor1 = arcpy.da.SearchCursor(projectsFeaturePath, projectsFeatureField)
	for row1 in searchCursor1:
		if not row1[0] in projectsTrailsdbList:
			projectsTrailsdbList.append(row1[0])
	searchCursor2 = arcpy.da.SearchCursor(projectsTablePath, projectsTableFields)
	for row2 in searchCursor2:
		if not row2[0] in projectsTrailsdbList and not row2[0] in projectsSFList and not row2[1] is None and not row2[2] is None:
			print row2[0]
			projectsSFList.append(row2[0])
			csvList.append(str(row2[0]) + "," + str(row2[1]) + "," + str(row2[2]))
			csvListChanged = 1

	if csvListChanged == 1:
		trailsdbErrorsEmail_missingInfoFromSaleforce_projectCode_coordinates(csvList)