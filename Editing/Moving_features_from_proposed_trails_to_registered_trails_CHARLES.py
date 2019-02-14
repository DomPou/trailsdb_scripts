import sys, arcpy

# Salesforce connection properties
userSF = 'dpoulin@tctrail.ca'
passwordSF = 'A2XlW42tw9SL'
securityToken = '6KxCh6z7CegggqBx5HMeG67Fs'
passwordTOKEN = passwordSF + securityToken

# trailsdb variables
instance = "TCT45"
gdbUser = "dpoulin"
gdbUserPassword = "Welcome2you"
dbAdmin = "postgres"
dbAdminPassword = "Welcome2you"
gdbAdminAndPassword = "sde"
gdbName = "trailsdb"
gdbName_tests = "trailsdb_tests"
gdbPath = "Database Connections\\" + gdbName + ".sde\\"
gdbPath_tests = "Database Connections\\" + gdbName_tests + ".sde\\"
featuresRoot = gdbName + "." + gdbUser + "."
gdbFeaturesRoot = gdbPath  + featuresRoot
gdbFeaturesRoot_tests = gdbPath_tests  + gdbName_tests + ".sde."
tempEditingGdbPath = "C:\\Temp\\trailsdb_editing.gdb"
archivesFeaturePath = gdbFeaturesRoot + "fc_projects_archives"

# User inputs variables
project_code_value = arcpy.GetParameter(0)
reg_date_value = arcpy.GetParameterAsText(1)


def trailsdb_or_tests(gdb_name):
    if gdb_name == "trailsdb":
        return(gdbName,gdbPath,gdbFeaturesRoot)
    if gdb_name == "trailsdb_tests":
        return(gdbName_tests,gdbPath_tests,gdbFeaturesRoot_tests)

def buildWhereClause(table, field, value):
	"""Constructs a SQL WHERE clause to select rows having the specified value within a given field and table."""

	# Add DBMS-specific field delimiters
	fieldDelimited = arcpy.AddFieldDelimiters(table, field)

	# Determine field type
	fieldType = arcpy.ListFields(table, field)[0].type

	# Add single-quotes for string field values
	if str(fieldType) == 'String':
		value = "'%s'" % value

	# Format WHERE clause
	whereClause = "%s = %s" % (fieldDelimited, value)
	return whereClause

def salesforceObjects_inMemory(listToBeUsed):

    #List of objects to import from Salesforce for current case
    if listToBeUsed == "All":
        objectList = [
        "Account",
        "Contact",
        "Opportunity",
        "OpportunityDeliverable__c",
        "OpportunityRequirement__c",
        "ProjectDeliverableSign__c",
        "OpportunityContactRole",
        "Trail__c",
        "TrailAccount__c",
        "SignInfrastructure__c",
        "SignInfraDeliverable__c",
        "Task",
        "TrailCounter__c",
        "TrailCounterContact__c",
        "TrailWorkPlan__c",
        "TrailWorkPlanDeliverable__c",
        "TrailWorkPlanKPI__c",
        "User"
        ]
    if listToBeUsed == "Opportunity":
        objectList = ["Opportunity"]

    # Connect to Salesforce
    try:
        service = beatbox.PythonClient()  # instantiate the object
        service.login(userSF, passwordTOKEN)  # login using your sf credentials

        print("   Connected to Salesforce")
    except:
        print("   WARNING: Can't connect to Salesforce")

    for obj in objectList:
        print(obj)
        objLower = obj.lower()
        desc = service.describeSObjects(obj)[0]

        fieldSF = []
        # the syntax is for key, value in dict.items()
        for fieldname, fieldspec in desc.fields.items():
            # Those type of fields are not supported in the import
            if fieldspec.type == 'address': # cause an error if you don't exclude
                continue
            if fieldspec.type == 'location': # cause an error if you don't exclude
                continue
            # Skip field with too long names
            if len(fieldname) >= 31:
                continue

            elm = {}
            elm['fieldname'] = fieldname # Field is Normal Case as SF provides them
            elm['fieldlabel'] = fieldspec.label

            if fieldspec.type == 'currency' or fieldspec.type == 'double' or fieldspec.type == 'percent':
                if fieldspec.scale == 0:
                    intScale = fieldspec.scale + 1
                    intPrecision = fieldspec.precision + 1
                else:
                    intScale = fieldspec.scale
                    intPrecision = fieldspec.precision

                if (intScale > intPrecision) or (intPrecision > 38):
                    elm['fieldtype'] = "DOUBLE"
                    elm['fieldscale'] = 8
                    elm['fieldprecision'] = 38
                    elm['fieldlength'] = 8
                elif intPrecision >= 7:
                    elm['fieldtype'] = "DOUBLE"
                    elm['fieldscale'] = intScale
                    elm['fieldprecision'] = intPrecision
                    elm['fieldlength'] = 8
                else:
                    elm['fieldtype'] = "FLOAT"
                    elm['fieldscale'] = intScale
                    elm['fieldprecision'] = intPrecision
                    elm['fieldlength'] = 4
            elif fieldspec.type == 'date' or fieldspec.type == 'datetime':
                elm['fieldtype'] = "DATE"
                elm['fieldscale'] = 0
                elm['fieldprecision'] = 0
                elm['fieldlength'] = 8
            elif fieldspec.type == 'int':
                elm['fieldtype'] = "LONG"
                elm['fieldscale'] = 0
                elm['fieldprecision'] = 10
                elm['fieldlength'] = 4
            elif fieldspec.type == 'boolean':
                elm['fieldtype'] = "TEXT"
                elm['fieldscale'] = 0
                elm['fieldprecision'] = 0
                elm['fieldlength'] = 10
            elif fieldname == "ProjectCode__c": # exception to convert ProjectCode__c from String to Long
                elm['fieldtype'] = "LONG"
                elm['fieldscale'] = 0
                elm['fieldprecision'] = 10
                elm['fieldlength'] = 4
            else:
                elm['fieldtype'] = "TEXT"
                elm['fieldscale'] = 0
                elm['fieldprecision'] = 0
                elm['fieldlength'] = fieldspec.length

            fieldSF.append(elm)

        # Create temporary tables
        # Table Path
        if objLower == 'user':  # Creating table with user as the name failed
            objLower = 'usersf'
        tblPath = "in_memory\\" + objLower
        # Delete table if exists
        if arcpy.Exists(tblPath):
            arcpy.Delete_management(tblPath)
        # Create empty temp table
        arcpy.CreateTable_management("in_memory\\",objLower)

        # Adjust schema
        # To contain list of fields that will be added or updated
        fieldUpdated = ["objectid"]

        for field in fieldSF:
            fieldName = field['fieldname'].lower()
            fieldLabel = field['fieldlabel']
            fieldType = field['fieldtype']
            fieldScale = field['fieldscale']
            fieldPrecision = field['fieldprecision']
            fieldLength = field['fieldlength']
            arcpy.AddField_management(tblPath, fieldName, fieldType, fieldPrecision, fieldScale, fieldLength,
                                      fieldLabel, "NULLABLE", "NON_REQUIRED", "")

        # Add Salesforce data to temporary table
        # Query records from Salesforce
        queryFields = ', '.join(item['fieldname'] for item in fieldSF)
        query_result = service.query("SELECT " + queryFields + " FROM " + obj)
        records = query_result['records']  # dictionary of results!
        total_records = query_result['size']  # full size of results
        query_locator = query_result['queryLocator']  # get the mystical queryLocator

        # loop through, pulling the next 500 and appending it to your records dict
        while query_result['done'] is False and len(records) < total_records:
            query_result = service.queryMore(query_locator)
            query_locator = query_result['queryLocator']  # get the updated queryLocator
            records = records + query_result['records']  # append to records dictionary

        # print records[0]
        # print("Number of records: " + str(total_records))

        # SF object does contain records
        if len(records) > 0:
            # Print 1st record
            # print res[0]
            cursor = arcpy.InsertCursor(tblPath)

            # for field in fieldSF:
            #     print(field['fieldname'].lower())

            print("\n")
            for record in records:
                #print(record)

                row = cursor.newRow()
                for field in fieldSF:
                    fieldNameLower = field['fieldname'].lower()
                    fieldValue = record[field['fieldname']]
                    # print(fieldNameLower)
                    # print(record[field['fieldname']])
                    # print("\n")

                    if field['fieldtype'] == 'DATE' and fieldValue is not None:
                        fieldValue = fieldValue.strftime('%Y-%m-%d %H:%M:%S')

                    if isinstance(fieldValue, (list,)):
                        fieldValue = ', '.join(item for item in fieldValue)

                    if fieldValue == '':
                        fieldValue = None

                    row.setValue(fieldNameLower, fieldValue)
                cursor.insertRow(row)

def projectStageAndClassification_inMemory_v1(project_code):

	# Variables
	arcpy.AddMessage("  Getting project information from Salesforce")
	salesforceOpportunity = "in_memory\\opportunity"
	salesforceFields = ["projectcode__c", "projecttype__c", "projectsubtype__c", "projectstate__c", "stagename"]

	# Create temporary table
	salesforceObjects_inMemory("Opportunity")

	#if arcpy.Exists(salesforceOpportunity):
	#	for field in arcpy.ListFields(salesforceOpportunity):
	#		if field.name in salesforceFields:
	#			arcpy.AddMessage(field.name)

	# Get project type
	# Empty variables to avoid return errors on server
	projectTypeInSF = ""
	projectSubtypesInSF = []
	projectStateInSF = ""
	projectStageInSF = ""

	projectTypeCursor = arcpy.da.SearchCursor(salesforceOpportunity, salesforceFields)
	for row in projectTypeCursor:
		if row[0] == project_code:
			projectTypeInSF = row[1]
			tempProjectSubtypesInSF = row[2]
			if not tempProjectSubtypesInSF is None:
				projectSubtypesInSF = row[2].split(', ')
			projectStateInSF = row[3]
			projectStageInSF = row[4]
			arcpy.AddMessage(projectSubtypesInSF)

	return projectTypeInSF, projectSubtypesInSF, projectStateInSF, projectStageInSF

def projectFeatures_v1(project_code, database_version):
	# List of essential features for types + subtypes + state in Salesforce
	salesforceTypesSubtypesStatesEssentials = {
		"Study_Trail_New": ["None"],
		"Study_Trail_Existing": ["None"],
		"Study_Infrastructure_New": ["None"],
		"Study_Infrastructure_Existing": ["None"],
		"Study_Re-routing_New": ["not used yet"],
		"Study_Re-routing_Existing": ["not used yet"],
		"Study_Other_New": ["not used yet"],
		"Study_Other_Existing": ["None"],
		"Construction_Trail_New": [
			"fc_act_cross_country_skiing_pro",
			"fc_act_dog_sledding_pro",
			"fc_act_fat_biking_pro",
			"fc_act_horseback_riding_pro",
			"fc_act_mountain_biking_pro",
			"fc_act_paddling_pro",
			"fc_act_road_cycling_pro",
			"fc_act_rollerblading_pro",
			"fc_act_snowmobiling_pro",
			"fc_act_snowshoeing_pro",
			"fc_act_walking_pro",
			"fc_atv_pro",
			"fc_category_pro",
			"fc_environment_pro",
			"fc_gis_data_pro",
			"fc_local_trail_pro",
			"fc_manager_pro",
			"fc_network_pro",
			"fc_owner_pro",
			"fc_project_trail_pro",
			"fc_trail_code_pro",
			"fc_trail_type_pro"
		],
		"Construction_Trail_Existing": ["fc_project_trail_pro"],
		"Construction_Infrastructure_New": ["fc_project_infrastructure_pro"],
		"Construction_Infrastructure_Existing": ["None"],
		"Construction_Re-routing_New": ["not used yet"],
		"Construction_Re-routing_Existing": ["not used yet"],
		"Construction_Wayfinding Signage_New": ["fc_signage_trail_pro", "fc_signage_post_pro"],
		"Construction_Wayfinding Signage_Existing": ["fc_signage_trail_pro", "fc_signage_post_pro"],
		"Construction_Interpretive Signage Project_New": ["not used yet"],
		"Construction_Interpretive Signage Project_Existing": ["not used yet"],
		"Construction_Trailhead Project_New": ["not used yet"],
		"Construction_Trailhead Project_Existing": ["fc_signage_post_pro"],
		"Construction_Other_New": ["not used yet"],
		"Construction_Other_Existing": ["not used yet"],
		"Signage_Wayfinding Signage_New": ["fc_signage_trail_pro", "fc_signage_post_pro"],
		"Signage_Wayfinding Signage_Existing": ["fc_signage_trail_pro", "fc_signage_post_pro"],
		"Signage_Additional Cautionary Signage_New": ["fc_signage_post_pro"],
		"Signage_Additional Cautionary Signage_Existing": ["fc_signage_post_pro"],
		"Signage_Interpretive Signage Project_New": ["fc_signage_post_pro"],
		"Signage_Interpretive Signage Project_Existing": ["fc_signage_post_pro"],
		"Signage_Trailhead Project_New": ["fc_signage_post_pro"],
		"Signage_Trailhead Project_Existing": ["fc_signage_post_pro"],
		"Signage_Comprehensive Signage Project_New": ["fc_signage_post_pro"],
		"Signage_Comprehensive Signage Project_Existing": ["fc_signage_post_pro"],
		"Signage_Funding Only Request_New": ["not used yet"],
		"Signage_Funding Only Request_Existing": ["not used yet"],
		"Signage_Other_New": ["not used yet"],
		"Signage_Other_Existing": ["not used yet"],
		"Registration_Trail_New": ["not used yet"],
		"Registration_Trail_Existing": ["not used yet"],
		"Registration_Infrastructure_New": ["not used yet"],
		"Registration_Infrastructure_Existing": ["not used yet"],
		"Registration_Re-routing_New": ["not used yet"],
		"Registration_Re-routing_Existing": ["not used yet"],
		"Registration_Wayfinding Signage_New": ["not used yet"],
		"Registration_Wayfinding Signage_Existing": ["not used yet"],
		"Registration_Additional Cautionary Signage_New": ["not used yet"],
		"Registration_Additional Cautionary Signage_Existing": ["not used yet"],
		"Registration_Interpretive Signage Project_New": ["not used yet"],
		"Registration_Interpretive Signage Project_Existing": ["not used yet"],
		"Registration_Trailhead Project_New": ["not used yet"],
		"Registration_Trailhead Project_Existing": ["not used yet"],
		"Registration_Comprehensive Signage Project_New": ["not used yet"],
		"Registration_Comprehensive Signage Project_Existing": ["not used yet"],
		"Registration_Funding Only Request_New": ["not used yet"],
		"Registration_Funding Only Request_Existing": ["not used yet"],
		"Registration_Other_New": ["not used yet"],
		"Registration_Other_Existing": ["not used yet"],
		"Special_Funding Only Request_New": ["not used yet"],
		"Special_Funding Only Request_Existing": ["not used yet"],
		"Special_Trail Counters_New": ["not used yet"],
		"Special_Trail Counters_Existing": ["not used yet"],
		"Special_Other_New": ["not used yet"],
		"Special_Other_Existing": ["not used yet"]
	}

	# Operational date required or not
	salesforceTypesSubtypesStatesOperationalDate = {
		"Study_Trail_New": "False",
		"Study_Trail_Existing": "False",
		"Study_Infrastructure_New": "False",
		"Study_Infrastructure_Existing": "False",
		"Study_Re-routing_New": "not used yet",
		"Study_Re-routing_Existing": "not used yet",
		"Study_Other_New": "not used yet",
		"Study_Other_Existing": "False",
		"Construction_Trail_New": "True",
		"Construction_Trail_Existing": "False",
		"Construction_Infrastructure_New": "False",
		"Construction_Infrastructure_Existing": "False",
		"Construction_Re-routing_New": "not used yet",
		"Construction_Re-routing_Existing": "not used yet",
		"Construction_Wayfinding Signage_New": "False",
		"Construction_Wayfinding Signage_Existing": "False",
		"Construction_Interpretive Signage Project_New": "not used yet",
		"Construction_Interpretive Signage Project_Existing": "not used yet",
		"Construction_Trailhead Project_New": "not used yet",
		"Construction_Trailhead Project_Existing": "False",
		"Construction_Other_New": "not used yet",
		"Construction_Other_Existing": "not used yet",
		"Signage_Wayfinding Signage_New": "False",
		"Signage_Wayfinding Signage_Existing": "False",
		"Signage_Additional Cautionary Signage_New": "False",
		"Signage_Additional Cautionary Signage_Existing": "False",
		"Signage_Interpretive Signage Project_New": "False",
		"Signage_Interpretive Signage Project_Existing": "False",
		"Signage_Trailhead Project_New": "False",
		"Signage_Trailhead Project_Existing": "False",
		"Signage_Comprehensive Signage Project_New": "False",
		"Signage_Comprehensive Signage Project_Existing": "False",
		"Signage_Funding Only Request_New": "not used yet",
		"Signage_Funding Only Request_Existing": "not used yet",
		"Signage_Other_New": "not used yet",
		"Signage_Other_Existing": "not used yet",
		"Registration_Trail_New": "not used yet",
		"Registration_Trail_Existing": "not used yet",
		"Registration_Infrastructure_New": "not used yet",
		"Registration_Infrastructure_Existing": "not used yet",
		"Registration_Re-routing_New": "not used yet",
		"Registration_Re-routing_Existing": "not used yet",
		"Registration_Wayfinding Signage_New": "not used yet",
		"Registration_Wayfinding Signage_Existing": "not used yet",
		"Registration_Additional Cautionary Signage_New": "not used yet",
		"Registration_Additional Cautionary Signage_Existing": "not used yet",
		"Registration_Interpretive Signage Project_New": "not used yet",
		"Registration_Interpretive Signage Project_Existing": "not used yet",
		"Registration_Trailhead Project_New": "not used yet",
		"Registration_Trailhead Project_Existing": "not used yet",
		"Registration_Comprehensive Signage Project_New": "not used yet",
		"Registration_Comprehensive Signage Project_Existing": "not used yet",
		"Registration_Funding Only Request_New": "not used yet",
		"Registration_Funding Only Request_Existing": "not used yet",
		"Registration_Other_New": "not used yet",
		"Registration_Other_Existing": "not used yet",
		"Special_Funding Only Request_New": "not used yet",
		"Special_Funding Only Request_Existing": "not used yet",
		"Special_Trail Counters_New": "not used yet",
		"Special_Trail Counters_Existing": "not used yet",
		"Special_Other_New": "not used yet",
		"Special_Other_Existing": "not used yet"
	}

	# Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbPath = gdbVariables[1]
	gdbFeaturesRoot = gdbVariables[2]

	projectVariables = projectStageAndClassification_v1(project_code)
	projectTypeStr = projectVariables[0]
	projectSubtypesList = projectVariables[1]
	projectStateStr = projectVariables[2]

	project_Lines_Features_Names = []
	project_Lines_Features_Paths = []
	project_Lines_Features_Names_and_Paths = {}
	project_Lines_Features_Path_and_Names = {}
	project_Points_Features_Names = []
	project_Points_Features_Paths = []
	project_Points_Features_Names_and_Paths = {}
	project_Points_Features_Paths_and_Names = {}
	essential_Lines_Features_Names = []
	essential_Points_Features_Names = []
	project_Corresponding_Registered_Path = {}
	essential_Lines_Features_Names_CONSTRUCTION = []
	essential_Points_Features_Names_CONSTRUCTION = []

	# 1 - List of features names and paths that DO contain data for the project
	# list project features in proposed_info other than fc_project_pro
	arcpy.env.workspace = gdbPath + "proposed_info\\"
	for featureWithRoot in arcpy.ListFeatureClasses():
		pathLength = len(gdbFeaturesRoot)
		featurePath = gdbPath + featureWithRoot
		featureName = featurePath[pathLength:]
		if not "fc_project_pro" in featureWithRoot:
			cursor = arcpy.da.SearchCursor(featureWithRoot, "project_code")
			for row in cursor:
				if row[0] == project_code:
					if arcpy.Describe(featureWithRoot).shapeType == "Polyline":
						if not featureName in project_Lines_Features_Names:
							project_Lines_Features_Names.append(featureName)
						if not featurePath in project_Lines_Features_Paths:
							project_Lines_Features_Paths.append(featurePath)
						project_Lines_Features_Names_and_Paths.update({featureName: featurePath})
						project_Lines_Features_Path_and_Names.update({featurePath: featureName})
						project_Corresponding_Registered_Path.update({featurePath: featurePath[:-3] + "reg"})
					if arcpy.Describe(featureWithRoot).shapeType == "Point":
						if not featureName in project_Points_Features_Names:
							project_Points_Features_Names.append(featureName)
						if not featurePath in project_Points_Features_Paths:
							project_Points_Features_Paths.append(featurePath)
						project_Points_Features_Names_and_Paths.update({featureName: featurePath})
						project_Points_Features_Paths_and_Names.update({featurePath: featureName})
	# list project features in proposed_signage_info other than fc_project_signage_pro
	arcpy.env.workspace = gdbPath + "proposed_signage_info\\"
	for featureWithRoot in arcpy.ListFeatureClasses():
		pathLength = len(gdbFeaturesRoot)
		featurePath = gdbPath + featureWithRoot
		featureName = featurePath[pathLength:]
		if not "fc_project_signage_pro" in featureWithRoot:
			cursor = arcpy.da.SearchCursor(featureWithRoot, "project_code")
			for row in cursor:
				if row[0] == project_code:
					if arcpy.Describe(featureWithRoot).shapeType == "Polyline":
						if not featureName in project_Lines_Features_Names:
							project_Lines_Features_Names.append(featureName)
						if not featurePath in project_Lines_Features_Paths:
							project_Lines_Features_Paths.append(featurePath)
						project_Lines_Features_Names_and_Paths.update({featureName: featurePath})
						project_Lines_Features_Path_and_Names.update({featurePath: featureName})
						project_Corresponding_Registered_Path.update({featurePath: featurePath[:-3] + "reg"})
					if arcpy.Describe(featureWithRoot).shapeType == "Point":
						if not featureName in project_Points_Features_Names:
							project_Points_Features_Names.append(featureName)
						if not featurePath in project_Points_Features_Paths:
							project_Points_Features_Paths.append(featurePath)
						project_Points_Features_Names_and_Paths.update({featureName: featurePath})
						project_Points_Features_Paths_and_Names.update({featurePath: featureName})
	# 2 - List of features that SHOULD contain data for the project
	no_Missing_List_Validation = "True"
	operational_Date_Required = "False"
	missing_Combination_Message_List = []
	# create list from subtypes in salesforce_objects table
	for current_project_subtype in projectSubtypesList:
		# Filter projects without subtypes (Special)
		if not current_project_subtype is None:
			currentTypesSubtypesStates = projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr
			currentEssentialsList = salesforceTypesSubtypesStatesEssentials.get(currentTypesSubtypesStates)
			currentOperationalDateRequirement = salesforceTypesSubtypesStatesOperationalDate.get(
				currentTypesSubtypesStates)
			# Return error message for list not created yet
			if currentEssentialsList is None:
				no_Missing_List_Validation = "False"
				missing_Combination_Message_List.append(
					projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr + " is a new combination in Salesforce. Modify trailsdb_project_features_by_type")
			if not currentEssentialsList is None:
				for currentFeature in currentEssentialsList:
					# Return error message for new combination in salesforce not in dictionnary
					if currentFeature == "not used yet":
						no_Missing_List_Validation = "False"
						missing_Combination_Message_List.append(
							"First time a project " + currentTypesSubtypesStates + " is registered. Decide essential features needed and modify trailsdb_project_features_by_type")
					if not currentFeature == "not used yet":
						# Ignore projects with no essential features:
						if not currentFeature == "None":
							currentFeaturePath = gdbFeaturesRoot + currentFeature
							if arcpy.Describe(currentFeaturePath).shapeType == "Polyline":
								if not currentFeature in essential_Lines_Features_Names:
									essential_Lines_Features_Names.append(currentFeature)
									if not "signage" in currentFeature:
										essential_Lines_Features_Names_CONSTRUCTION.append(currentFeature)
							if arcpy.Describe(currentFeaturePath).shapeType == "Point":
								if not currentFeature in essential_Points_Features_Names:
									essential_Points_Features_Names.append(currentFeature)
									if not "signage" in currentFeature:
										essential_Points_Features_Names_CONSTRUCTION.append(currentFeature)
		# Check if an operational date has to be added
		if currentOperationalDateRequirement is None:
			no_Missing_List_Validation = "False"
			if not projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr + " is a new combination in Salesforce, modify trailsdb_project_features_by_type" in missing_Combination_Message_List:
				missing_Combination_Message_List.append(
					projectTypeStr + "_" + current_project_subtype + "_" + projectStateStr + " is a new combination in Salesforce, modify trailsdb_project_features_by_type")
		if currentOperationalDateRequirement == "not used yet":
			no_Missing_List_Validation = "False"
			missing_Combination_Message_List.append(
				"First time a project " + currentTypesSubtypesStates + " is registered, established if an operational date is required and modify trailsdb_project_features_by_type")
		# Change operational_Date_Required to true if any of the combinations returns True
		if currentOperationalDateRequirement == "True":
			operational_Date_Required = "True"

		# 3 - identify main project feature (fc_project_trail_pro or fc_signage_trail_pro)
		# project_Main_Feature_Path = "None"
		if projectTypeStr == "Signage":
			if "Wayfinding Signage" in projectSubtypesList:
				project_Main_Feature_Path = gdbFeaturesRoot + "fc_signage_trail_pro"
		if projectTypeStr == "Signage":
			if not "Wayfinding Signage" in projectSubtypesList:
				project_Main_Feature_Path = "None"
		if not projectTypeStr == "Signage":
			project_Main_Feature_Path = gdbFeaturesRoot + "fc_project_trail_pro"

	return project_Lines_Features_Names, project_Lines_Features_Paths, project_Lines_Features_Names_and_Paths, project_Lines_Features_Path_and_Names, project_Points_Features_Names, project_Points_Features_Paths, project_Points_Features_Names_and_Paths, project_Points_Features_Paths_and_Names, essential_Lines_Features_Names, essential_Points_Features_Names, no_Missing_List_Validation, missing_Combination_Message_List, project_Corresponding_Registered_Path, operational_Date_Required, project_Main_Feature_Path, essential_Lines_Features_Names_CONSTRUCTION, essential_Points_Features_Names_CONSTRUCTION

def projectDataValidation_v1(project_code, database_version):
	# Get project features variables from trailsdb
	projectFeaturesVariable = projectFeatures_v1(project_code, database_version)
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

def projectProposedOrRegistered_inMemory_v1(project_code):

	# salesforce_objects data
	projectVariables = projectStageAndClassification_inMemory_v1(project_code)
	projectStageStr = projectVariables[3]

	dataset = ""
	if projectStageStr in RegisteredProjectsStages:
		dataset = "Registered"
	if not projectStageStr in RegisteredProjectsStages:
		dataset = "Proposed"

	return dataset, projectStageStr

def projectProposedIntersect_v1(project_code,reg_date,database_version):
	# Editing gdb variables
	intersectionFeaturePath = tempEditingGdbPath + "\\intersect"

	# Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbName = gdbVariables[0]
	gdbPath = gdbVariables[1]
	gdbFeaturesRoot = gdbVariables[2]

	# Remove temp feature that might have been left before in editing gdb
	if arcpy.Exists(intersectionFeaturePath):
		arcpy.Delete_management(intersectionFeaturePath)

	# Get project features variables from trailsdb
	projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
	projectLinesFeaturesNamesList = projectFeaturesVariable[0]
	projectLinesFeaturesNamesandPathsDict = projectFeaturesVariable[2]
	projectPointsFeaturesNamesList = projectFeaturesVariable[4]
	projectPointsFeaturesNamesandPathsDict = projectFeaturesVariable[6]

	# Intersect polylines features and add a registration date
	linesIntersectList = []
	arcpy.AddMessage("  Copying project data")
	for currentFeature in projectLinesFeaturesNamesList:
		# Create temp feature with info from project
		# Trailsdb feature path
		currentFeaturePath = projectLinesFeaturesNamesandPathsDict.get(currentFeature)
		# temp feature in memory
		currentTempFeatureName = "temp_" + currentFeature
		if arcpy.Exists(currentTempFeatureName):
			arcpy.Delete_management(currentTempFeatureName)
		# temp feature path in c:\temp\trailsdb_editing
		currentTempFeaturePath = tempEditingGdbPath + "\\" + currentTempFeatureName
		if arcpy.Exists(currentTempFeaturePath):
			arcpy.Delete_management(currentTempFeaturePath)
		# Copying project to trailsdb_editing
		arcpy.MakeFeatureLayer_management(currentFeaturePath,currentTempFeatureName)
		whereClause = buildWhereClause(currentTempFeatureName, "project_code", project_code)
		arcpy.SelectLayerByAttribute_management(currentTempFeatureName,"NEW_SELECTION",whereClause)
		arcpy.CopyFeatures_management(currentTempFeatureName,currentTempFeaturePath)
		if not currentTempFeaturePath in linesIntersectList:
			linesIntersectList.append(currentTempFeaturePath)
	# Intersect all temp features and add and populate a date field
	# Exception for signage projects other than wayfinding (no line features)
	if not len(linesIntersectList) == 0:
		# Exception if there is main project feature is the only line feature (Signage only or trail project like a repair without new info), main trail
		if len(linesIntersectList) == 1:
			currentFeaturePath = linesIntersectList[0]
			currentTempFeatureName = "temp_main_feature"
			if arcpy.Exists(currentTempFeatureName):
				arcpy.Delete_management(currentTempFeatureName)
			arcpy.MakeFeatureLayer_management(currentFeaturePath,currentTempFeatureName)
			whereClause = buildWhereClause(currentTempFeatureName, "project_code", project_code)
			arcpy.SelectLayerByAttribute_management(currentTempFeatureName,"NEW_SELECTION",whereClause)
			arcpy.CopyFeatures_management(currentTempFeatureName,intersectionFeaturePath)
		# Intersect
		if not len(linesIntersectList) == 1:
			arcpy.Intersect_analysis(linesIntersectList, intersectionFeaturePath)
			arcpy.AddField_management(intersectionFeaturePath,"reg_date","DATE")
			dateCursor = arcpy.da.UpdateCursor(intersectionFeaturePath,"reg_date")
			for row in dateCursor:
				row[0] = reg_date
				dateCursor.updateRow(row)

	# Make temp point features
	pointsTempFeaturesList = []
	pointsTempFeaturesCorrespondingRegisteredFeaturesDict = {}
	for currentPointFeature in projectPointsFeaturesNamesList:
		currentPointFeaturePath = projectPointsFeaturesNamesandPathsDict.get(currentPointFeature)
		currentTempPointFeatureName = "temp_" + currentPointFeature
		registeredFeaturePath = gdbFeaturesRoot + currentPointFeature[:-3] + "reg"
		currentTempPointFeaturePath = tempEditingGdbPath + "\\" + currentTempPointFeatureName
		if arcpy.Exists(currentTempPointFeaturePath):
			arcpy.Delete_management(currentTempPointFeaturePath)
		arcpy.MakeFeatureLayer_management(currentPointFeaturePath,currentTempPointFeatureName)
		whereClause = buildWhereClause(currentTempPointFeatureName, "project_code", project_code)
		arcpy.SelectLayerByAttribute_management(currentTempPointFeatureName,"NEW_SELECTION",whereClause)
		arcpy.CopyFeatures_management(currentTempPointFeatureName,currentTempPointFeaturePath)
		pointsTempFeaturesList.append(currentTempPointFeaturePath)
		pointsTempFeaturesCorrespondingRegisteredFeaturesDict.update({currentTempPointFeaturePath:registeredFeaturePath})
	return intersectionFeaturePath,pointsTempFeaturesList,pointsTempFeaturesCorrespondingRegisteredFeaturesDict

def registerValidatedProject_v1(project_code,reg_date,database_version):

	# Variables
	gdbVariables = trailsdb_or_tests(database_version)
	gdbFeaturesRoot = gdbVariables[2]
	archivesFeaturePath = gdbFeaturesRoot + "fc_projects_archives"

	# Get project features variables from trailsdb
	projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
	projectLinesFeaturesPathsList = projectFeaturesVariable[1]
	projectFeatureNameCorrespondingRegisteredPath = projectFeaturesVariable[12]
	operationalDateRequiredStr = projectFeaturesVariable[13]

	# Get temporary intersection of project's line features and temporary copies of project's point features
	tempProjectFeatures = projectProposedIntersect_v1(project_code,reg_date,database_version)
	tempIntersectionPathStr = tempProjectFeatures[0]
	pointsTempFeaturesList = tempProjectFeatures[1]
	pointsTempFeaturesCorrespondingRegisteredFeaturesDict = tempProjectFeatures[2]

	# Append Archive
	arcpy.AddMessage("      Archive")
	try:
		arcpy.Append_management(tempIntersectionPathStr,archivesFeaturePath,"NO_TEST")
	# Exception for signage projects other than wayfinding (no line features)
	except:
		arcpy.AddMessage("          Study or Signage project other than wayfinding. Does not need to be archived")
	# Append line features of project (list of REGISTERED features)
	arcpy.AddMessage("      Line Features")
	for currentLineFeature in projectLinesFeaturesPathsList:
		registeredLineFeature = projectFeatureNameCorrespondingRegisteredPath.get(currentLineFeature)
		arcpy.AddMessage("          " + registeredLineFeature)
		arcpy.Append_management(tempIntersectionPathStr,registeredLineFeature,"NO_TEST")
	if operationalDateRequiredStr == "True":
		arcpy.AddMessage("          " + gdbFeaturesRoot + "fc_operational_date_reg")
		arcpy.Append_management(tempIntersectionPathStr,gdbFeaturesRoot + "fc_operational_date_reg","NO_TEST")
	# Append point features of project (list of TEMP features)
	arcpy.AddMessage("      Point Features")
	for currentTempPointFeature in pointsTempFeaturesList:
		# Feature to append to
		registeredPointFeature = pointsTempFeaturesCorrespondingRegisteredFeaturesDict.get(currentTempPointFeature)
		arcpy.AddMessage("          " + registeredPointFeature)
		arcpy.Append_management(currentTempPointFeature,registeredPointFeature,"NO_TEST")

def removeProjectFromProposedDatasets_v1(project_code,database_version):

	# Get project features variables from trailsdb
	projectFeaturesVariable = projectFeatures_v1(project_code,database_version)
	projectLinesFeaturesPathsList = projectFeaturesVariable[1]
	projectPointsFeaturesPathsList = projectFeaturesVariable[5]
	# Uses delete features to remove all geometries from this project
	for lineFeature in projectLinesFeaturesPathsList:
		if arcpy.Exists("currentTemp"):
			arcpy.Delete_management("currentTemp")
		arcpy.MakeFeatureLayer_management(lineFeature,"currentTemp")
		whereClause = buildWhereClause("currentTemp", "project_code", project_code)
		arcpy.SelectLayerByAttribute_management("currentTemp","NEW_SELECTION",whereClause)
		arcpy.DeleteFeatures_management("currentTemp")
	for pointFeature in projectPointsFeaturesPathsList:
		if arcpy.Exists("currentTemp"):
			arcpy.Delete_management("currentTemp")
		arcpy.MakeFeatureLayer_management(pointFeature,"currentTemp")
		whereClause = buildWhereClause("currentTemp", "project_code", project_code)
		arcpy.SelectLayerByAttribute_management("currentTemp","NEW_SELECTION",whereClause)
		arcpy.DeleteFeatures_management("currentTemp")