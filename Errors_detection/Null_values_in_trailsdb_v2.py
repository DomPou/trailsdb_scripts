#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,arcpy,smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *
from GIS_email_variables import *

def trailsdbErrorsEmail_NullValue(featureClass, globalIdValue, fieldNameNullValue):

	msg = MIMEMultipart()
	subject = "Trailsdb error - " + featureClass + " - Null value"
	body = """
Error found in trailsdb:
Feature class:
""" + featureClass + """

Error type:
Null value found

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

#Variables
statusList = ["reg","pro"]

#Feature name, field
featuresNoNull = [
	["trail_code","trail_code"],
	["local_trail","local_trail_id"],
	["regional_trail","regional_trail_id"],
	["project_trail", "project_code"],
	["project","project_code"],
	["manager","salesforceid_manager"],
	["owner","salesforceid_owner"],
	["category","category"],
	["network","network"],
	["trail_type","trail_type"],
	["environment","environment"],
	["paddling","paddling"],
	["cross_country_skiing","cross_country_skiing"],
	["dog_sledding","dog_sledding"],
	["fat_biking","fat_biking"],
	["horseback_riding","horseback_riding"],
	["mountain_biking","mountain_biking"],
	["road_cycling","road_cycling"],
	["rollerblading","rollerblading"],
	["snowmobiling","snowmobiling"],
	["snowshoeing","snowshoeing"],
	["walking","walking"],
	["atv","atv"],
	["signage_post", "project_code"],
	["signage_post", "signage_post_type"],
	["signage_trail", "project_code"]
]

for status in statusList:
	for feature in featuresNoNull:
		featureName = "fc_" + feature[0] + "_" + status
		print featureName
		featurePath = gdbFeaturesRoot + featureName
		#Use Exists because project_reg does not exists
		if arcpy.Exists(featurePath):
			#check if field project_code exists and select which search to do
			if len(arcpy.ListFields(featurePath,"project_code")) == 0:
				searchFields = [feature[1],"globalid"]
				searchCursor = arcpy.da.SearchCursor(featurePath,searchFields)
				for row in searchCursor:
					if row[0] is None:
						trailsdbErrorsEmail_NullValue(featureName, row[1], feature[1])
			if not len(arcpy.ListFields(featurePath,"project_code")) == 0:
				searchFields = [feature[1],"project_code","globalid"]
				searchCursor = arcpy.da.SearchCursor(featurePath,searchFields)
				for row in searchCursor:
					if row[0] is None:
						trailsdbErrorsEmail_NullValue(featureName, row[2], feature[1])
					if row[1] is None:
						trailsdbErrorsEmail_NullValue(featureName, row[2], "project_code")