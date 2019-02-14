import sys, arcpy

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(functionsFolder)
from trailsdb_project_features_by_type_v1 import projectFeatures_v1
from trailsdb_project_features_by_type_v1 import projectFeatures_inMemory_v1

'''Return the following for other scripts:

#Get project features variables from trailsdb
projectValidationVariables = projectDataValidation_v1(project_code,database_version)
projectEssentialFeaturesValidationStatusStr = projectValidationVariables[0]
projectEssentialFeaturesValidationMissingList = projectValidationVariables[1]
projectFeaturesLengthValidationStatusStr = projectValidationVariables[2]
projectFeaturesLengthErrorsList = projectValidationVariables[3]
projectEssentialFeaturesValidationStatusCONSTRUCTIONStr = projectValidationVariables[4]
projectEssentialFeaturesValidationMissingCONSTRUCTIONList = projectValidationVariables[5]
projectFeaturesLengthDoubleList = projectValidationVariables[6]
'''

# Needs data produced by trailsdb_project_feature_by_type or similar
def projectDataValidation_v1(project_code,database_version):

    #Get project features variables from trailsdb
    projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
    projectMainFeaturePathStr = projectFeaturesVariable[14]
    projectLinesFeaturesNamesList = projectFeaturesVariable[0]
    projectLinesFeaturesPathsList = projectFeaturesVariable[1]
    projectLinesFeaturesPathsAndNamesDict = projectFeaturesVariable[3]
    projectPointsFeaturesNamesList = projectFeaturesVariable[4]
    projectEssentialLinesFeaturesNamesList = projectFeaturesVariable[8]
    projectEssentialPointsFeaturesNamesList = projectFeaturesVariable[9]
    projectEssentialLinesFeaturesNamesCONSTRUCTIONList = projectFeaturesVariable[15]
    projectEssentialPointsFeaturesNamesCONSTRUCTIONList = projectFeaturesVariable[16]
    
    #1 - Check if every essential features for the project contains data

    essential_Features_Validation_Status = "True"
    essential_Features_Validation_Missing = []
    project_Features_Length_Validation = "True"
    project_Features_Length_Double_Validation = "False"
    project_Features_Length_Errors = []
    essential_Features_Validation_Status_CONSTRUCTION = "True"
    essential_Features_Validation_Missing_CONSTRUCTION = []

    for lineFeatureName in projectEssentialLinesFeaturesNamesList:
        if not lineFeatureName in projectLinesFeaturesNamesList:
            essential_Features_Validation_Status = "False"
            essential_Features_Validation_Missing.append(lineFeatureName)

    for lineFeatureName_CONSTRUCTION in projectEssentialLinesFeaturesNamesCONSTRUCTIONList:
        if not lineFeatureName_CONSTRUCTION in projectLinesFeaturesNamesList:
            essential_Features_Validation_Status_CONSTRUCTION = "False"
            essential_Features_Validation_Missing_CONSTRUCTION.append(lineFeatureName_CONSTRUCTION)
    
    for pointFeatureName in projectEssentialPointsFeaturesNamesList:
        #Some projects like Infrastructure_Existing don't have any, so they are filtered
        if not pointFeatureName == "None":
            if not pointFeatureName in  projectPointsFeaturesNamesList:
                essential_Features_Validation_Status = "False"
                essential_Features_Validation_Missing.append(pointFeatureName)

    for pointFeatureName_CONSTRUCTION in projectEssentialPointsFeaturesNamesCONSTRUCTIONList:
        #Some projects like Infrastructure_Existing don't have any, so they are filtered
        if not pointFeatureName_CONSTRUCTION == "None":
            if not pointFeatureName_CONSTRUCTION in  projectPointsFeaturesNamesList:
                essential_Features_Validation_Status_CONSTRUCTION = "False"
                essential_Features_Validation_Missing_CONSTRUCTION.append(pointFeatureName_CONSTRUCTION)

    #2 - Check if line features are all covering the whole project
    #Main feature length for construction and wayfinding projects
    lengthTimeTwoPossibleList = ["fc_local_trail_pro","fc_regional_trail_pro"]
    lengthDoubleList = []
    if not projectMainFeaturePathStr == "None":
        projectLength = 0.0
        projectLengthCursor = arcpy.da.SearchCursor(projectMainFeaturePathStr,["project_code", "st_length(shape)"])
        for row in projectLengthCursor:
            if row[0] == project_code:
                projectLength += row[1]
        for lineFeaturePath in projectLinesFeaturesPathsList:
            currentFeatureName = projectLinesFeaturesPathsAndNamesDict.get(lineFeaturePath)
            currentLength = 0.0
            currentLengthCursor = arcpy.da.SearchCursor(lineFeaturePath,["project_code", "st_length(shape)"])
            for row in currentLengthCursor:
                if row[0] == project_code:
                    currentLength += row[1]
            if not round(currentLength,2) == round(projectLength,2):
                project_Features_Length_Validation = "False"
                project_Features_Length_Errors.append(currentFeatureName)
                if round(currentLength,2) == round(projectLength*2,2):
                    if currentFeatureName in lengthTimeTwoPossibleList:
                        lengthDoubleList.append(currentFeatureName)
    # Check if project_Features_Length_Errors only contains features that are and can be twice as long
    if set(project_Features_Length_Errors) == set (lengthDoubleList):
        project_Features_Length_Double_Validation = "True"

    return essential_Features_Validation_Status, essential_Features_Validation_Missing, project_Features_Length_Validation, project_Features_Length_Errors, projectEssentialLinesFeaturesNamesCONSTRUCTIONList, projectEssentialPointsFeaturesNamesCONSTRUCTIONList, project_Features_Length_Double_Validation


def projectDataValidation_inMemory_v1(project_code, database_version):
    # Get project features variables from trailsdb
    projectFeaturesVariable = projectFeatures_inMemory_v1(project_code, database_version)
    projectMainFeaturePathStr = projectFeaturesVariable[14]
    projectLinesFeaturesNamesList = projectFeaturesVariable[0]
    projectLinesFeaturesPathsList = projectFeaturesVariable[1]
    projectLinesFeaturesPathsAndNamesDict = projectFeaturesVariable[3]
    projectPointsFeaturesNamesList = projectFeaturesVariable[4]
    projectEssentialLinesFeaturesNamesList = projectFeaturesVariable[8]
    projectEssentialPointsFeaturesNamesList = projectFeaturesVariable[9]
    projectEssentialLinesFeaturesNamesCONSTRUCTIONList = projectFeaturesVariable[15]
    projectEssentialPointsFeaturesNamesCONSTRUCTIONList = projectFeaturesVariable[16]

    # 1 - Check if every essential features for the project contains data

    essential_Features_Validation_Status = "True"
    essential_Features_Validation_Missing = []
    project_Features_Length_Validation = "True"
    project_Features_Length_Double_Validation = "False"
    project_Features_Length_Errors = []
    essential_Features_Validation_Status_CONSTRUCTION = "True"
    essential_Features_Validation_Missing_CONSTRUCTION = []

    for lineFeatureName in projectEssentialLinesFeaturesNamesList:
        if not lineFeatureName in projectLinesFeaturesNamesList:
            essential_Features_Validation_Status = "False"
            essential_Features_Validation_Missing.append(lineFeatureName)

    for lineFeatureName_CONSTRUCTION in projectEssentialLinesFeaturesNamesCONSTRUCTIONList:
        if not lineFeatureName_CONSTRUCTION in projectLinesFeaturesNamesList:
            essential_Features_Validation_Status_CONSTRUCTION = "False"
            essential_Features_Validation_Missing_CONSTRUCTION.append(lineFeatureName_CONSTRUCTION)

    for pointFeatureName in projectEssentialPointsFeaturesNamesList:
        # Some projects like Infrastructure_Existing don't have any, so they are filtered
        if not pointFeatureName == "None":
            if not pointFeatureName in projectPointsFeaturesNamesList:
                essential_Features_Validation_Status = "False"
                essential_Features_Validation_Missing.append(pointFeatureName)

    for pointFeatureName_CONSTRUCTION in projectEssentialPointsFeaturesNamesCONSTRUCTIONList:
        # Some projects like Infrastructure_Existing don't have any, so they are filtered
        if not pointFeatureName_CONSTRUCTION == "None":
            if not pointFeatureName_CONSTRUCTION in projectPointsFeaturesNamesList:
                essential_Features_Validation_Status_CONSTRUCTION = "False"
                essential_Features_Validation_Missing_CONSTRUCTION.append(pointFeatureName_CONSTRUCTION)

    # 2 - Check if line features are all covering the whole project
    # Main feature length for construction and wayfinding projects
    lengthTimeTwoPossibleList = ["fc_local_trail_pro", "fc_regional_trail_pro"]
    lengthDoubleList = []
    if not projectMainFeaturePathStr == "None":
        projectLength = 0.0
        projectLengthCursor = arcpy.da.SearchCursor(projectMainFeaturePathStr, ["project_code", "st_length(shape)"])
        for row in projectLengthCursor:
            if row[0] == project_code:
                projectLength += row[1]
        for lineFeaturePath in projectLinesFeaturesPathsList:
            currentFeatureName = projectLinesFeaturesPathsAndNamesDict.get(lineFeaturePath)
            currentLength = 0.0
            currentLengthCursor = arcpy.da.SearchCursor(lineFeaturePath, ["project_code", "st_length(shape)"])
            for row in currentLengthCursor:
                if row[0] == project_code:
                    currentLength += row[1]
            if not round(currentLength, 2) == round(projectLength, 2):
                project_Features_Length_Validation = "False"
                project_Features_Length_Errors.append(currentFeatureName)
                if round(currentLength, 2) == round(projectLength * 2, 2):
                    if currentFeatureName in lengthTimeTwoPossibleList:
                        lengthDoubleList.append(currentFeatureName)
    # Check if project_Features_Length_Errors only contains features that are and can be twice as long
    if set(project_Features_Length_Errors) == set(lengthDoubleList):
        project_Features_Length_Double_Validation = "True"

    return essential_Features_Validation_Status, essential_Features_Validation_Missing, project_Features_Length_Validation, project_Features_Length_Errors, projectEssentialLinesFeaturesNamesCONSTRUCTIONList, projectEssentialPointsFeaturesNamesCONSTRUCTIONList, project_Features_Length_Double_Validation