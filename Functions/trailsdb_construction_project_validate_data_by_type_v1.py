import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

# Needs data produced by trailsdb_project_feature_by_type or similar
def constructionProjectDataValidation_v1(project_code_value,project_Main_Feature_Path,project_Lines_Features_Names,project_Lines_Features_Paths,project_Lines_Features_Names_and_Paths,project_Points_Features_Names,project_Points_Features_Paths,project_Points_Features_Names_and_Paths,project_Essential_Lines_Features_Names,project_Essential_Points_Features_Names):
	# 1 - Check if every essential features for the project contains data
	essential_Features_Validation_Status = "True"
	essential_Features_Validation_Missing = []
	project_Features_Length_Validation = "True"
	project_Features_Length_Errors = []

	for lineFeatureName in project_Essential_Lines_Features_Names:
		if not lineFeatureName in project_Lines_Features_Names:
			essential_Features_Validation_Status = "False"
			essential_Features_Validation_Missing.append(lineFeatureName)
	for pointFeatureName in project_Essential_Points_Features_Names:
		if not pointFeatureName in project_Points_Features_Names:
			essential_Features_Validation_Status = "False"
			essential_Features_Validation_Missing.append(pointFeatureName)

	# 2 - Check if line features are all covering the whole project
	# Main feature length
	projectLength = 0.0
	projectLengthCursor = arcpy.da.SearchCursor(project_Main_Feature_Path,["project_code", "st_length(shape)"])
	for row in projectLengthCursor:
		if row[0] == project_code_value:
			projectLength += row[1]
	for lineFeaturePath in project_Lines_Features_Paths:
		currentFeatureName = project_Lines_Features_Names_and_Paths.get(lineFeaturePath)
		currentLength = 0.0
		currentLengthCursor = arcpy.da.SearchCursor(lineFeaturePath,["project_code", "st_length(shape)"])
		for row in currentLengthCursor:
			currentLength += row[1]
		if not round(currentLength,2) == round(projectLength,2):
			project_Features_Length_Validation = "False"
			project_Features_Length_Errors.append(currentFeatureName)

	return essential_Features_Validation_Status, essential_Features_Validation_Missing, project_Features_Length_Validation, project_Features_Length_Errors