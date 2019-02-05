import arcpy, sys, beatbox

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from Connection_to_trailsdb import *

sys.path.append(salesforceFolder)
from Salesforce_connection_variables import *


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