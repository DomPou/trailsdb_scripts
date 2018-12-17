#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, arcpy,smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from Send_email_with_Microsoft_Exchange import trailsdbErrorsEmail_UnknownValue

def trailsdbErrorsEmail_UnknownValue(featureClass, globalIdValue, fieldNameNullValue):

	msg = MIMEMultipart()
	subject = "Trailsdb error - " + featureClass + " - Null value"
	body = """
Error found in trailsdb:
Feature class:
""" + featureClass + """

Error type:
Unknown value found

Definition query:
globalid = '""" + globalIdValue + """'

Field with Null value:
""" + fieldNameNullValue + """
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

def unknownValue():
	#Variables
	statusList = ["reg","pro"]

	#Feature name, field
	featuresNoNull = [
		["environment","environment"],
		["signage_post", "signage_post_type"],
		["trail_type","trail_type"]
	]

	for status in statusList:
		for feature in featuresNoNull:
			featureName = "fc_" + feature[0] + "_" + status
			featurePath = gdbFeaturesRoot + featureName
			#Use Exists because project_reg does not exists
			if arcpy.Exists(featurePath):
				searchFields = [feature[1], "globalid"]
				searchCursor = arcpy.da.SearchCursor(featurePath,searchFields)
				for row in searchCursor:
					if row[0] == 0:
						trailsdbErrorsEmail_UnknownValue(featureName, row[1], feature[1])

unknownValue()