#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from GIS_email_variables import *


def trailsdbScriptSuccess(scriptName):

	msg = MIMEMultipart()
	subject = "Trailsdb script completed - " + scriptName
	body = """
""" + scriptName + """ completed without errors
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

def trailsdbErrorsEmail_misc(message):

	msg = MIMEMultipart()
	subject = "Trailsdb error - misc"
	body = """
""" + message + """
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

def trailsdbErrorsEmail_missingInfoFromSaleforce_projectCode_coordinates(featureClass, projectsCoordinatesList):

	msg = MIMEMultipart()
	subject = "Trailsdb error - " + featureClass + " - Coordinates - Project Code not found in Trailsdb"
	body = """
Error found in trailsdb:
Feature class: """ + featureClass + """

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

def trailsdbErrorsEmail_missingInfoFromSaleforce_projectCode_noCoordinates(featureClass, projectCode, projectName, trailcode, oldCode, location, province, developmentYear, possibleTrailCodesList):

	#Check for empty values
	oldCodeValidated = "None"
	if not oldCode is None:
		oldCodeValidated = oldCode
	locationProvinceValidated = "Unknown"
	if location is None:
		if not province is None:
			locationProvinceValidated = province
	if not location is None:
		locationProvinceValidated = location
		if not province is None:
			locationProvinceValidated = locationProvinceValidated + ", " + province
	developmentYearValidated = "Unknown"
	if not developmentYear is None:
		developmentYearValidated = developmentYear

	msg = MIMEMultipart()
	subject = "Trailsdb error - " + featureClass + " - Project Code not found in Trailsdb"
	body = """
Error found in trailsdb:
Feature class: """ + featureClass + """

Error type: Project Code not found in Trailsdb

Project code:
""" + str(projectCode) + """

Project Name:
""" + projectName + """

Trail Code:
""" + trailcode + """

Old project code (if query return empty table, project was cancelled and is not in archive fc):
phase_code = '""" + oldCodeValidated + """'

Location:
""" + locationProvinceValidated + """

Development Year:
""" + developmentYearValidated + """

Possible Trails (Code linked to Account):
""" + '\r\n'.join(possibleTrailCodesList) + """
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

def trailsdbErrorsEmail_missingInfoFromSaleforce(featureClass, subject, errorTypeTxt, fieldName1, value1, fieldName2, value2):

	#Check for empty values
	value1validated = "None"
	value2validated = "None"
	if not value1 is None:
		value1validated = value1
	if not value2 is None:
		value2validated = value2


	msg = MIMEMultipart()
	subject = "Trailsdb error - " + subject + " - Id not found in Trailsdb"
	body = """
Error found in trailsdb:
Feature class: """ + featureClass + """

Error type: """ + errorTypeTxt + """

Field 1: """ + fieldName1 + """ = """ + value1validated + """

Field 2: """ + fieldName2 + """ = """ + value2validated + """

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

def trailsdbErrorsEmail_notInSaleforce(featureClass, subject, fieldGoodValue, goodValue, fieldBadValue, badValue, possibleValue):

	#Check for empty values
	goodValueValidated = "None"
	badValueValidated = "None"
	possibleValueValidated = "None"
	if not goodValue is None:
		goodValueValidated = goodValue
	if not badValue is None:
		badValueValidated = badValue
	if not possibleValue is None:
		possibleValueValidated = possibleValue

	msg = MIMEMultipart()
	subject = "Trailsdb error - " + subject + " - Id not found in Salesforce"
	body = """
Error found in trailsdb:
Feature class: """ + featureClass + """

Error type: Cannot find this trail account in salesforce_objects

Correct information: """ + fieldGoodValue + """ = """ + goodValueValidated + """

Wrong information: """ + fieldBadValue + """ = """ + badValueValidated + """

Possible right information: """ + possibleValueValidated + """
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

def trailsdbErrorsEmail_projectInWrongDataset(feature, projectCode, projectName):

	projectCodeValidated = "None"
	projectNameValidated = "None"
	if not projectCode is None:
		projectCodeValidated = str(projectCode)
	if not projectName is None:
		projectNameValidated = projectName

	if not "signage" in feature:
		subject = "Trailsdb error - Signage project in " + feature
	if "signage" in feature:
		subject = "Trailsdb error - Construction project in " + feature

	msg = MIMEMultipart()
	body = """
Error found in trailsdb:
Project Code:
project_code = """ + projectCodeValidated + """

Project Name: """ + projectNameValidated + """

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

def trailsdbErrorsEmail_CompletedProjectNotRegistered(projectCode,projectType,projectSubtypes):
	
	msg = MIMEMultipart()
	subject = "Trailsdb error - Project completed in Salesforce"
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