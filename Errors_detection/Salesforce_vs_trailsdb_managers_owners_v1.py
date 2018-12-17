#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, arcpy, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *
from GIS_email_variables import *

sys.path.append(functionsFolder)
from trailsdb_queries_Intersect_Two_Feature_Classes_v1 import *

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

	# Check for empty values
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

def managersOwnersErrors():
	# Salesforce_objects part
	# Variables
	accountTableName = "account"
	accountTablePath = gdbSalesforceRoot + accountTableName
	accountTableFields = ["id","name"]
	trailAccountTableName = "trailaccount__c"
	trailAccountTablePath = gdbSalesforceRoot + trailAccountTableName
	trailAccountFields = ["name","owner__c","manager__c","account__c"]

	# Dictionaries and List for validation in trailsdb
	accountsDict = {}
	accountsDict2 = {}
	trailAccountsSalesforce_Owner_List = []
	trailAccountsSalesforce_Manager_List = []
	idsSalesforce_Owner_List = []
	idsSalesforce_Manager_List = []
	validationDict = {}


	cursorAccounts = arcpy.da.SearchCursor(accountTablePath,accountTableFields)
	for rowAccount in cursorAccounts:
		# First dictionary to add the info in trails db
		accountsDict.update({rowAccount[0]:rowAccount[1]})
		# Another dict dealing with the 70 characters limit in Salesforce for the validation in the end
		accountsDict2.update({rowAccount[1][:70]:rowAccount[0]})
	cursorTrailAccountsSalesforce = arcpy.da.SearchCursor(trailAccountTablePath,trailAccountFields)
	for rowTrailAccountSalesforce in cursorTrailAccountsSalesforce:
		# Owners
		if int(rowTrailAccountSalesforce[1]) == 1:
			if not rowTrailAccountSalesforce[0] in trailAccountsSalesforce_Owner_List:
				trailAccountsSalesforce_Owner_List.append(rowTrailAccountSalesforce[0])
				idsSalesforce_Owner_List.append(rowTrailAccountSalesforce[3])
		# Managers
		if int(rowTrailAccountSalesforce[2]) == 1:
			if not rowTrailAccountSalesforce[0] in trailAccountsSalesforce_Manager_List:
				trailAccountsSalesforce_Manager_List.append(rowTrailAccountSalesforce[0])
				idsSalesforce_Manager_List.append(rowTrailAccountSalesforce[3])

	# Trailsdb part
	# Variables
	statusList = ["reg","pro"]
	toIntersectList = ["manager","owner"]
	validationField = "trail_account_name"
	validationDict = {"manager":trailAccountsSalesforce_Manager_List,"owner":trailAccountsSalesforce_Owner_List}
	possibleValuesDict = {"manager":idsSalesforce_Manager_List,"owner":idsSalesforce_Owner_List}

	# Intersect fc_trail_code with fc_manager and fc_owner
	for feature in toIntersectList:
		mergeFeaturePath = gdbFeaturesRoot_queries + "diss_int_trail_code_" + feature + "_all"
		fieldsCriteria = ["trail_code", feature]
		salesforceidField = feature[:5] + "_salesforceid_" + feature
		intersectList = []
		mergeList = []

		for status in statusList:
			fc1 = "fc_trail_code_" + status
			fc2 = "fc_" + feature + "_" + status
			# function from trailsdb_queries_Intersect_Two_Feature_Classes
			name = intersectFeatureClassesFromTrailsdb_returnName_v1(fc1, fc2)
			intersectList.append(name)

		# Dissolve intersects
		for feature2 in intersectList:
			feature2Path = gdbFeaturesRoot_queries + feature2
			feature2Fields = arcpy.ListFields(feature2Path)
			dissolveFields = []
			for feature2Field in feature2Fields:
				for fieldCriteria in fieldsCriteria:
					if fieldCriteria in feature2Field.name:
						dissolveFields.append(feature2Field.name)
			dissolveFeaturePath = gdbFeaturesRoot_queries + "diss_" + feature2

			if arcpy.Exists(dissolveFeaturePath):
				arcpy.Delete_management(dissolveFeaturePath)
			arcpy.Dissolve_management(feature2Path,dissolveFeaturePath,dissolveFields,"","MULTI_PART")

			mergeList.append(dissolveFeaturePath)

		# Merge pro and reg together, add text field for concatenate of code and owner or manager name
		if arcpy.Exists(mergeFeaturePath):
			arcpy.Delete_management(mergeFeaturePath)
		arcpy.Merge_management(mergeList,mergeFeaturePath)
		# 70 characters (limit salesforce) + 6 characters (9999: )
		arcpy.AddField_management(mergeFeaturePath,validationField,"TEXT",76)

		# Validate trailsdb data
		# First part, check if salesforceid in trailsdb is good and update trail_account_name in _all
		possibleIDList = possibleValuesDict.get(feature)
		cursorUpdate = arcpy.da.UpdateCursor(mergeFeaturePath,["trail_trail_code", salesforceidField, validationField])
		for rowUpdate in cursorUpdate:
			accountNameGet = accountsDict.get(rowUpdate[1])
			if accountNameGet is None:
				currentPossibleValue = ""
				# Check for a similar id in saleforce to help determine if it is an input mistake in trailsdb or a changed value in Saleforce
				for currentIdValue in possibleIDList:
					if rowUpdate[1] in currentIdValue:
						currentPossibleValue = currentIdValue
				trailsdbErrorsEmail_notInSaleforce(mergeFeaturePath, feature, "trail_trail_code", rowUpdate[0], salesforceidField, rowUpdate[1], currentPossibleValue)
			if not accountNameGet is None:
				rowUpdate[2] = rowUpdate[0] + ": " + accountNameGet
				cursorUpdate.updateRow(rowUpdate)
		# Second part, look if every trail_account_name in Salesforce are in trailsdb
		salesforceList = validationDict.get(feature)
		trailsdbList = []
		# Get all trail accounts in trailsdb
		cursorTrailAccountsTrailsdb = arcpy.da.SearchCursor(mergeFeaturePath,validationField)
		for rowTrailAccountTrailsdb in cursorTrailAccountsTrailsdb:
			# To avoid errors due to delay in updating salesforce_objects
			if not rowTrailAccountTrailsdb[0] is None:
				# Limiting name to Salesforce characters limit for the validation
				currentTrailAccount = rowTrailAccountTrailsdb[0][:76]
				if not currentTrailAccount in trailsdbList:
					trailsdbList.append(rowTrailAccountTrailsdb[0][:76])
		# Compare trail accounts in trailsdb to trails accounts in salesforce_objects
		for trailAccountSF in salesforceList:
			if not trailAccountSF in trailsdbList:
				salesforceAccountId = accountsDict2.get(trailAccountSF[6:])
				trailsdbErrorsEmail_missingInfoFromSaleforce(mergeFeaturePath, feature, "Trail account in Salesforce but not in trailsdb", "account name", trailAccountSF, "salesforce id", salesforceAccountId)

managersOwnersErrors()