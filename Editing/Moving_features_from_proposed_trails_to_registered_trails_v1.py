import sys, arcpy
from Editing_Variables import *

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append("C:\\Users\\DPoulin\\OneDrive\\Trailsdb_OneDrive\\Scripts\\Functions")
from Build_SQL_Where_Clause import *


#User inputs variables
project_code_value = arcpy.GetParameter(0)
reg_date_value = arcpy.GetParameterAsText(1)


#Script variables
salesforceOpportunity = gdbSalesforceRoot + "opportunity"
salesforceFields = ["projectcode__c","projecttype__c","stagename"]
archivesFeaturePath = gdbFeaturesRoot + "fc_projects_archives"
#contruction projects trailsdb
projectFeaturePath_construction = gdbFeaturesRoot + "fc_project_trail_pro"
selectionFeaturePath_construction = tempEditingGdbPath + "\\temp_fc_project_trail_pro"
#selectionFeaturePathBuffer_construction = tempEditingGdbPath + "\\buffer_fc_project_trail_pro"
#signage projects trailsdb
projectFeaturePath_signage = gdbFeaturesRoot + "fc_signage_trail_pro"
selectionFeaturePath_signage = tempEditingGdbPath + "\\temp_fc_signage_trail_pro"
selectionFeaturePath_signagePost = tempEditingGdbPath + "\\temp_fc_signage_post_pro"
#selectionFeaturePathBuffer_signage = tempEditingGdbPath + "\\buffer_fc_signage_trail_pro"
intersectionFeaturePath = tempEditingGdbPath + "\\intersect"

def appendArchive():
    arcpy.Append_management(intersectionFeaturePath, archivesFeaturePath, "NO_TEST")

def appendArchiveSignage():
    arcpy.Append_management(selectionFeaturePath_signage, archivesFeaturePath, "NO_TEST")

def appendLineFeatures(lineFeaturesToAppendTo):
    for feature in lineFeaturesToAppendTo:
        arcpy.Append_management(intersectionFeaturePath,feature,"NO_TEST")

def appendLineFeaturesSignage(lineFeaturesToAppendTo):
    for feature in lineFeaturesToAppendTo:
        arcpy.Append_management(selectionFeaturePath_signage,feature,"NO_TEST")

def appendPointFeatures(listOfFeaturesToAppendTo):
    #To copy signage posts from proposed signage to registered
    for feature in listOfFeaturesToAppendTo:
        #Copy only to features existing in registered_info (projects coordinates are not in it)
        if arcpy.Exists(feature):
            if arcpy.Describe(feature).shapeType == "Point":
                tempFeature = gdbPath + feature[50:-3] + "pro"
                arcpy.Append_management(tempFeature, feature,"NO_TEST")

def calculateProjectLength():
    #Calulate total length of project for future validation
    length = 0.0
    projectLengthCursor = arcpy.da.SearchCursor(selectionFeaturePath, "shape_Length")
    for row in projectLengthCursor:
        length = length + row[0]
    return length

def deleteOld():
    #Delete temp features created by this script in tempEditingGdb
    if arcpy.Exists(selectionFeaturePath_construction):
        arcpy.Delete_management(selectionFeaturePath_construction)
    #if arcpy.Exists(selectionFeaturePathBuffer_construction):
    #	arcpy.Delete_management(selectionFeaturePathBuffer_construction)
    if arcpy.Exists(selectionFeaturePath_signage):
        arcpy.Delete_management(selectionFeaturePath_signage)
    #if arcpy.Exists(selectionFeaturePathBuffer_signage):
    #	arcpy.Delete_management(selectionFeaturePathBuffer_signage)
    #if arcpy.Exists(validationFeaturePath):
    #	arcpy.Delete_management(validationFeaturePath)
    if arcpy.Exists(intersectionFeaturePath):
        arcpy.Delete_management(intersectionFeaturePath)

def deleteProposedProject(featuresWithProjectToDelete):
    for feature in featuresWithProjectToDelete:
        #Safety to make sur projects coordinates are not deleted
        if not "fc_project_pro" in feature and not "fc_project_signage_pro" in feature:
            arcpy.env.workspace = gdbPath_admin
            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(False, True)
            edit.startOperation()
            deleteProjectCursor = arcpy.da.UpdateCursor(gdbFeaturesRoot_admin + feature,"project_code")
            for row in deleteProjectCursor:
                if row[0] == project_code_value:
                    deleteProjectCursor.deleteRow()
            edit.stopOperation()
            edit.stopEditing(True)

def essentialFeatures(projectType):
    #Establish essential features for current project
    essentialFeaturesDict = {}
    essentialFeaturesStudy = []
    essentialFeaturesConstruction = []
    essentialFeaturesSignage = []
    for featureProject in fieldsProjectsFeature:
        if featureProject[5] == "essential":
            if not featureProject[1] in essentialFeaturesConstruction:
                essentialFeaturesConstruction.append(featureProject[1])
                essentialFeaturesDict.update({"Construction":essentialFeaturesConstruction})
        if featureProject[6] == "essential":
            if not featureProject[1] in essentialFeaturesStudy:
                essentialFeaturesStudy.append(featureProject[1])
                essentialFeaturesDict.update({"Study":essentialFeaturesStudy})
    for featureSignage in fieldsSignageProjectsFeature:
        if featureSignage[5] == "essential":
            if not featureProject[1] in essentialFeaturesSignage:
                essentialFeaturesSignage.append(featureSignage[1])
                essentialFeaturesDict.update({"Signage":essentialFeaturesSignage})
    finalEssentialList = essentialFeaturesDict.get(projectType)
    return finalEssentialList

def essentialAndLengthValidation(mainFeatureLength, tempFeaturesList, featuresEssentialList):
    emptyFeatures = []
    noEssentialEmptyFeatures = "True"
    noLengthErrors = "True"
    tempFeaturesList2 = []
    essentialEmptyFeaturesList = []
    lengthErrorsFeaturesList = []
    for featureEssentialValidation in tempFeaturesList:
        if arcpy.Exists(featureEssentialValidation):
            #Remove empty features and check if they are essentials
            if not arcpy.management.GetCount(featureEssentialValidation)[0] == "0":
                tempFeaturesList2.append(featureEssentialValidation)
            if arcpy.management.GetCount(featureEssentialValidation)[0] == "0":
                emptyFeatures.append(featureEssentialValidation)
                arcpy.Delete_management(featureEssentialValidation)
                #Check if empty feature is essential
                if featureEssentialValidation in featuresEssentialList:
                    noEssentialEmptyFeatures = "False"
                    essentialEmptyFeaturesList.append(featureEssential)
    for nonEmptyFeatures in tempFeaturesList2:
        #Alignment features
        if arcpy.Describe(nonEmptyFeatures).shapeType == "Polyline":
            #Check if current feature total length equals the project length
            for featureLengthValidation in tempFeaturesList2:
                currentLength = 0.0
                lengthCursor = arcpy.da.SearchCursor(nonEmptyFeatures,"shape_Length")
                for row in lengthCursor:
                    currentLength += row[0]
                if not round(currentLength,2) == round(mainFeatureLength,2):
                    noLengthErrors = "False"
                    lengthErrorsFeaturesList.append(nonEmptyFeatures)
    return (tempFeaturesList2, noEssentialEmptyFeatures, noLengthErrors, essentialEmptyFeaturesList, lengthErrorsFeaturesList)

def projectTypeSalesforce():
    #Identify type of project to determine where to append features
    projectTypeCursor = arcpy.da.SearchCursor(salesforceOpportunity,salesforceFields)
    for row in projectTypeCursor:
        if row[0] == project_code_value:
            projectTypeInSF = row[1]
    return projectTypeInSF

def projectStageSalesforce():
    #Identify type of project to determine where to append features
    projectTypeCursor = arcpy.da.SearchCursor(salesforceOpportunity,salesforceFields)
    for row in projectTypeCursor:
        if row[0] == project_code_value:
            projectStageInSF = row[2]
    return projectStageInSF

def projectFeaturesValidation(projectType,projectLength):
    #Check if project exists
    projectFound = "False"
    if projectType  == "Study":
        searchCursorValidation = arcpy.da.SearchCursor(gdbFeaturesRoot + "fc_project_pro","project_code")
        for row in searchCursorValidation:
            if row[0] == project_code_value:
                projectFound = "True"
        if not projectFound == "True":
            arcpy.AddMessage("Project code " + str(project_code_value) + " is not in proposed_trails")
    if projectType  == "Construction":
        searchCursorValidation = arcpy.da.SearchCursor(gdbFeaturesRoot + "fc_project_pro","project_code")
        for row in searchCursorValidation:
            if row[0] == project_code_value:
                if projectLength <> 0.0:
                    projectFound = "True"
        if not projectFound == "True":
            arcpy.AddMessage("Project code " + str(project_code_value) + " is not in proposed_trails")
    if projectType  == "Signage":
        searchCursorValidation = arcpy.da.SearchCursor(gdbFeaturesRoot + "fc_project_signage_pro","project_code")
        for row in searchCursorValidation:
            if row[0] == project_code_value:
                projectFound = "True"
        if not projectFound == "True":
            arcpy.AddMessage("Project code " + str(project_code_value) + " is not in proposed_signage")
    return projectFound

def selectionFeaturesProject():
    #Create Temporary features containing info related to the project code
    featuresSelectedList = []
    tempFeaturesCreatedList = []
    #Line features in trailsdb - Proposed
    arcpy.env.workspace = gdbFeaturesRoot + "proposed_info\\"
    for featureSelectionProject in arcpy.ListFeatureClasses():
        #Avoid the two layers that are not changing in the registering process
        if not "fc_project_pro" in featureSelectionProject and not "fc_project_signage_pro" in featureSelectionProject:
            featuresSelectedList.append(featureSelectionProject[17:])
    #Line features in trailsdb - Proposed Signage
    arcpy.env.workspace = gdbFeaturesRoot + "proposed_signage_info\\"
    for featureSelectionProject in arcpy.ListFeatureClasses():
        featuresSelectedList.append(featureSelectionProject[17:])
    for featureSelectionProject in featuresSelectedList:
        #Path to features used and created
        featureSelectionProjectPath = gdbFeaturesRoot + featureSelectionProject
        editingFeatureSelectionProjectPath = tempEditingGdbPath + "\\temp_" + featureSelectionProject
        #Add created feature to list of temp features, and delete it if a bug let it there the last time
        tempFeaturesCreatedList.append(editingFeatureSelectionProjectPath)
        if arcpy.Exists(editingFeatureSelectionProjectPath):
            arcpy.Delete_management(editingFeatureSelectionProjectPath)
        #Create temp feature for current project code
        arcpy.MakeFeatureLayer_management(featureSelectionProjectPath,"temp" + featureSelectionProject)
        whereClause = buildWhereClause("temp" + featureSelectionProject, "project_code", project_code_value)
        arcpy.SelectLayerByAttribute_management("temp" + featureSelectionProject,"NEW_SELECTION",whereClause)
        arcpy.CopyFeatures_management("temp" + featureSelectionProject,editingFeatureSelectionProjectPath)
    return tempFeaturesCreatedList

def validationMessages(projectType, emptyFeaturesValidation, emptyFeaturesErrors, lengthValidation,lengthValidationErrors,emptySignageFeaturesValidation):
    finalValidation = "True"
    if not emptyFeaturesValidation == "True":
        finalValidation = "False"
        arcpy.AddMessage("Cannot continue, the following features are empty: ")
        for feature in emptyFeaturesErrors:
            arcpy.AddMessage("	" + feature)
    if not lengthValidation == "True":
        finalValidation = "False"
        arcpy.AddMessage("Cannot continue, the following features are not covering the whole project: ")
        for feature in lengthValidationErrors:
            arcpy.AddMessage("	" + feature)
    if projectType == "Signage":
        if not emptySignageFeaturesValidation == "True":
            finalValidation = "False"
            arcpy.AddMessage("Cannot continue, fc_signage_trail_pro is empty")
    return finalValidation

#Check if temp layers in this script already exists and delete them
deleteOld()

#Variables: Type and Stage (salesforce) of project
projectType = projectTypeSalesforce()
projectStage = projectStageSalesforce()

#Start validation process
arcpy.AddMessage("Validating project data in trailsdb")

#Choose proper features path according to Project Type in Salesforce
if projectType == "Study" or projectType == "Construction":
    projectFeaturePath = projectFeaturePath_construction
    selectionFeaturePath = selectionFeaturePath_construction
#selectionFeaturePathBuffer = selectionFeaturePathBuffer_construction
if projectType == "Signage":
    projectFeaturePath = projectFeaturePath_signage
    selectionFeaturePath = selectionFeaturePath_signage

#selectionFeaturePathBuffer = selectionFeaturePathBuffer_signage

#Create temp features for current project and store them in a list
featuresList = selectionFeaturesProject()

#Variable : Length (trailsdb)
lengthProject = calculateProjectLength()

#Check if project exists and if it is in the right dataset according to Salesforce
projectValidation = projectFeaturesValidation(projectType,lengthProject)
if projectValidation == "True":
    #Validate data in trailsdb before registering
    #Features that have to contain information for this project
    featuresEssential = essentialFeatures(projectType)
    #Validate information before registering it and return variables needed for registration process
    valuesValidation = essentialAndLengthValidation(lengthProject,featuresList,featuresEssential)
    featuresProject = valuesValidation[0]
    emptyFeaturesValidation = valuesValidation[1]
    lengthValidation = valuesValidation[2]
    emptyFeaturesErrors = valuesValidation[3]
    lengthValidationErrors = valuesValidation[4]
    #Check that at least one signage feature is in the list of selected features if it's a signage project
    emptySignageFeaturesValidation = "False"
    if projectType == "Signage":
        for feature in featuresProject:
            tempPath = tempEditingGdbPath + "\\temp_" + signageFeature
            if feature == tempPath:
                emptySignageFeaturesValidation = "True"
    #Return messages for every type of errors or allow registering process
    projectFeaturesValidation = validationMessages(projectType, emptyFeaturesValidation, emptyFeaturesErrors, lengthValidation,lengthValidationErrors,emptySignageFeaturesValidation)
    #Start registering process
    if projectFeaturesValidation == "True":
        #List of polylines features to intersect and append
        lineFeaturesList = []
        deleteProjectList = []
        pointOrlineFeaturesToAppendToList = []
        lineToAppendList = [gdbFeaturesRoot + "fc_operational_date_reg"]
        for feature1 in featuresProject:
            if arcpy.Describe(feature1).shapeType == "Polyline":

                #To remove once script is separated from construction, it is for the line arcpy.Intersect_analysis(lineFeaturesList, intersectionFeaturePath)
                lineFeaturesList.append(feature1)

                lineToAppendList.append(gdbFeaturesRoot + feature1[34:-3] + "reg")
                pointOrlineFeaturesToAppendToList.append(gdbFeaturesRoot + feature1[34:-3] + "reg")
                deleteProjectList.append(feature1[34:])
            if arcpy.Describe(feature1).shapeType == "Point":
                pointOrlineFeaturesToAppendToList.append(gdbFeaturesRoot + feature1[34:-3] + "reg")
                deleteProjectList.append(feature1[34:])
        #Intersect polylines features and add a registration date
        arcpy.Intersect_analysis(lineFeaturesList, intersectionFeaturePath)
        arcpy.AddField_management(intersectionFeaturePath,"reg_date","DATE")
        dateCursor = arcpy.da.UpdateCursor(intersectionFeaturePath,"reg_date")
        for row in dateCursor:
            row[0] = reg_date_value
            dateCursor.updateRow(row)
        #Append intersection to proper features classes according to project type
        arcpy.AddMessage(str(project_code_value) + " - " + projectType)
        if projectType == "Study":
            appendArchive()
            deleteProposedProject(deleteProjectList)
        if projectType == "Construction":
            if projectStage == "Cancelled":
                arcpy.AddMessage("	" + projectStage + " - Moving to archive")
                appendArchive()
                deleteProposedProject(deleteProjectList)
            if projectStage == "Closed":
                arcpy.AddMessage("	" + projectStage + " - Moving to registered and archive")
                appendArchive()
                appendLineFeatures(lineToAppendList)
                appendPointFeatures(pointOrlineFeaturesToAppendToList)
                deleteProposedProject(deleteProjectList)
        if projectType == "Signage":
            #Remove fc_operational_date_reg from the features to append because not used in signage projects
            lineToAppendList.remove(gdbFeaturesRoot + "fc_operational_date_reg")
            if projectStage == "Cancelled":
                arcpy.AddMessage("	" + projectStage + " - Moving to archive")
                appendArchiveSignage()
                deleteProposedProject(deleteProjectList)
            if projectStage == "Closed":
                arcpy.AddMessage("	" + projectStage + " - Moving to registered and archive")
                appendArchiveSignage()
                appendLineFeaturesSignage(lineToAppendList)
                appendPointFeatures(pointOrlineFeaturesToAppendToList)
                deleteProposedProject(deleteProjectList)
        #Delete temp features that are still in trailsdb_editing
        for featureToDelete in featuresList:
            if arcpy.Exists(featureToDelete):
                arcpy.Delete_management(featureToDelete)
    if not projectFeaturesValidation == "True":
        arcpy.AddMessage("Registration process cancelled")
if not projectValidation == "True":
    arcpy.AddMessage("Registration process cancelled")
