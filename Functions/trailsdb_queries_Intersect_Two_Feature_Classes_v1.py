import sys, arcpy, string

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from Build_SQL_Where_Clause import *

#Field join, field
tablesJoinedFields =[
	["local_trail_id","local_trail_name_en"],
	["local_trail_id","local_trail_name_fr"],
	["project_code","project_name"],
	["regional_trail_id","regional_trail_name_en"],
	["regional_trail_id","regional_trail_name_fr"],
	["trail_code","trail_code_name_en"],
	["trail_code","trail_code_name_fr"],
]

def intersectFeatureClassesFromTrailsdb_returnName_v1(mainFeatureName, intersectFeatureName, database_version):
	# General Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbFeaturesRoot = gdbVariables[2]

	"""Intersect a feature Class with a Main Feature Class"""

	# Main feature variables
	mainFeature = gdbFeaturesRoot + mainFeatureName
	# Identify the main feature's name root and shorten it to avoid final name longer than arcsde's limit
	if mainFeatureName[-5:] == "admin":
		mainFeatureRoot = mainFeatureName[3:-6]
	else:
		mainFeatureRoot = mainFeatureName[3:-4]
	mainFeatureFields = arcpy.ListFields(mainFeature)
	intersectFeature = gdbFeaturesRoot + intersectFeatureName
	inFeatureDesc = arcpy.Describe(intersectFeature)
	featureShapeType = inFeatureDesc.shapeType
	intersectFeatureFields = arcpy.ListFields(intersectFeature)

	# Output variables
	# Identify the intersected feature's name root and shorten it to avoid final name longer than arcsde's limit
	if intersectFeatureName[-5:] == "admin":
		nameFeatureEnd = intersectFeatureName[-6:]
		endPos = -6
	else:
		nameFeatureEnd = intersectFeatureName[-4:]
		endPos = -4
	if intersectFeatureName[:3] == "fc_":
		intersectFeatureRoot = intersectFeatureName[3:endPos]
		if intersectFeatureName[:7] == "fc_act_":
			intersectFeatureRoot = intersectFeatureName[7:endPos]


	outFeatureName = "int_" + mainFeatureRoot + "_" + intersectFeatureRoot + nameFeatureEnd
	outFeature = gdbFeaturesRoot_queries + outFeatureName
	# output Fields
	fieldsToIgnoreOrDeleteMain = ["objectid", "shape", "globalid", "created_user", "created_date", "last_edited_user", "last_edited_date"]
	fieldsToIgnoreOrDeleteIntersect = ["objectid", "shape", "globalid", "created_user", "created_date", "last_edited_user"]
	outFeatureFields = []
	outFeatureFieldsNewNames = {}
	outFeatureFieldsType = {}
	if featureShapeType == "Polyline":
		outFeatureFields.append("length")
		outFeatureFieldsType.update({"length":"FLOAT"})

	outFeatureFieldsWithDomain = []
	outFeatureFieldsDomains = {}
	outFeatureFieldsTable = {}

	# Add main feature's fields and intersect feature's fields to lists and dictionaries use to create output feature
	for field in mainFeatureFields:
		if not field.name in fieldsToIgnoreOrDeleteMain:
				if not field.name in outFeatureFields:
					outFeatureFields.append(field.name)
					outFeatureFieldsNewNames.update({field.name:mainFeatureRoot[:5] + "_" + field.name})
					outFeatureFieldsType.update({field.name:field.type})
					for tableField in tablesJoinedFields:
						if tableField[0] == field.name:
							if not tableField[1] in outFeatureFields:
								outFeatureFields.append(tableField[1])
								outFeatureFieldsType.update({tableField[1]:"TEXT"})
								outFeatureFieldsTable.update({tableField[1]:tableField[0]})
					if field.domain != "":
						outFeatureFieldsWithDomain.append(field.name)
						outFeatureFieldsDomains.update({field.name:field.domain})
	for field in intersectFeatureFields:
		if not field.name in fieldsToIgnoreOrDeleteIntersect:
			if not field.name in outFeatureFields:
				outFeatureFields.append(field.name)
				outFeatureFieldsNewNames.update({field.name:intersectFeatureRoot[:5] + "_" + field.name})
				outFeatureFieldsType.update({field.name:field.type})
				for tableField in tablesJoinedFields:
					if tableField[0] == field.name:
						if not tableField[1] in outFeatureFields:
							outFeatureFields.append(tableField[1])
							outFeatureFieldsType.update({tableField[1]:"TEXT"})
							outFeatureFieldsTable.update({tableField[1]:tableField[0]})
				if field.domain != "":
					outFeatureFieldsWithDomain.append(field.name)
					outFeatureFieldsDomains.update({field.name:field.domain})

	# Intersect feature
	if arcpy.Exists(outFeature):
		arcpy.Delete_management(outFeature)

	arcpy.Intersect_analysis([mainFeature, intersectFeature], outFeature)

	for field in outFeatureFieldsWithDomain:
		fieldDomain = outFeatureFieldsDomains.get(field)
		arcpy.AssignDomainToField_management(outFeature, field, fieldDomain)

	for field in arcpy.ListFields(outFeature):
		if not field.name in outFeatureFields:
			try:
				arcpy.DeleteField_management(outFeature, field.name)
			except: continue
		if field.name in outFeatureFields:
			newName = outFeatureFieldsNewNames.get(field.name)
			try:
				arcpy.AlterField_management(outFeature, field.name, newName)
			except: continue

	return outFeatureName

#intersectFeatureClassesFromTrailsdb_returnName_v1("fc_trail_code_reg", "fc_atv_reg", "trailsdb")