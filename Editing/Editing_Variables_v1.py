import arcpy

tempFolder = "C:\\Temp\\"
tempEditingGdb = "trailsdb_editing.gdb"
tempEditingGdbPath = tempFolder + tempEditingGdb + "\\"
tempProjectsFeatureName = "tempProjectsFeature"
tempProjectsFeaturePath = tempEditingGdbPath + tempProjectsFeatureName
tempRegisteredFeatureName = "tempRegisteredFeature"
tempRegisteredFeaturePath = tempEditingGdbPath + tempRegisteredFeatureName


if not arcpy.Exists(tempFolder + tempEditingGdb):
    arcpy.CreateFileGDB_management(tempFolder, tempEditingGdb)

# every features variables
gdbEssentialFields = ["objectid","globalid","created_user","created_date","last_edited_user","last_edited_date","shape","st_length(shape)"]
featuresToIgnore = ["fc_signage_pro","fc_project_pro","fc_phase_pro"]


# field name in tempProjectsFeature, feature class, name in feature, type, domain,essential to register, essential for studies
# proposed_info then proposed_signage_info
fieldsProjectsFeature = [
["project_code","fc_project_trail_pro","project_code","LONG","","essential","essential"],
["submissionid_trail","fc_project_trail_pro","submissionid_trail","TEXT","","non-essential","non-essential"],
["validated_trail","fc_project_trail_pro","validated_trail","SHORT","yes_no","non-essential","non-essential"],
["trail_code","fc_trail_code_pro","trail_code","TEXT","","essential","essential"],
["salesforceid_manager","fc_manager_pro","salesforceid_manager","TEXT","","essential","non-essential"],
["salesforceid_owner","fc_owner_pro","salesforceid_owner","TEXT","","essential","non-essential"],
["local_trail_id","fc_local_trail_pro","local_trail_id","SHORT","","essential","non-essential"],
["regional_trail_id","fc_regional_trail_pro","regional_trail_id","SHORT","","non-essential","non-essential"],
["category","fc_category_pro","category","SHORT","category","essential","non-essential"],
["network","fc_network_pro","network","SHORT","network","essential","non-essential"],
["trail_type","fc_trail_type_pro","trail_type","SHORT","trail_type","essential","non-essential"],
["environment","fc_environment_pro","environment","SHORT","environment","essential","non-essential"],
["paddling","fc_act_paddling_pro","paddling","SHORT","yes_no","essential","non-essential"],
["cross_country_skiing","fc_act_cross_country_skiing_pro","cross_country_skiing","SHORT","yes_no","essential","non-essential"],
["dog_sledding","fc_act_dog_sledding_pro","dog_sledding","SHORT","yes_no","essential","non-essential"],
["fat_biking","fc_act_fat_biking_pro","fat_biking","SHORT","yes_no","essential","non-essential"],
["horseback_riding","fc_act_horseback_riding_pro","horseback_riding","SHORT","yes_no","essential","non-essential"],
["mountain_biking","fc_act_mountain_biking_pro","mountain_biking","SHORT","yes_no","essential","non-essential"],
["road_cycling","fc_act_road_cycling_pro","road_cycling","SHORT","yes_no","essential","non-essential"],
["rollerblading","fc_act_rollerblading_pro","rollerblading","SHORT","yes_no","essential","non-essential"],
["snowmobiling","fc_act_snowmobiling_pro","snowmobiling","SHORT","yes_no","essential","non-essential"],
["snowshoeing","fc_act_snowshoeing_pro","snowshoeing","SHORT","yes_no","essential","non-essential"],
["walking","fc_act_walking_pro","walking","SHORT","yes_no","essential","non-essential"],
["atv","fc_atv_pro","atv","SHORT","yes_no","essential","non-essential"],
["gis_data_accuracy","fc_gis_data_pro","gis_data_accuracy","SHORT","gis_data_accuracy","essential","non-essential"],
["gis_data_type","fc_gis_data_pro","gis_data_type","SHORT","gis_data_type","essential","non-essential"],
["gis_data_date","fc_gis_data_pro","gis_data_date","DATE","","essential","non-essential"],
["gis_data_source","fc_gis_data_pro","gis_data_source","TEXT","","essential","non-essential"],
["gis_data_url","fc_gis_data_pro","gis_data_url","TEXT","","essential","non-essential"],
["gis_change_explanation","fc_gis_data_pro","gis_change_explanation","SHORT","gis_change_explanation","essential","non-essential"],
["project_code_signage","fc_signage_trail_pro","project_code","TEXT","","non-essential","non-essential"]
]

fieldsSignageProjectsFeature = [["project_code","fc_signage_trail_pro","project_code","LONG","","essential"]]

signageFeature = "fc_signage_trail_pro"

fieldsProjectsLinkedPointFeature = {
"fc_signage_trail_pro":"fc_signage_post_pro"
}

#field name in tempRegisteredFeature, feature class, name in feature, type, domain
fieldsRegisteredFeature = [
["project_code","fc_project_trail_reg","project_code","LONG",""],
["submissionid_trail","fc_project_trail_reg","submissionid_trail","TEXT",""],
["validated_trail","fc_cip_trail_reg","validated_trail","SHORT","yes_no"],
["trail_code","fc_trail_code_reg","trail_code","TEXT",""],
["salesforceid_manager","fc_manager_reg","salesforceid_manager","TEXT",""],
["salesforceid_owner","fc_owner_reg","salesforceid_owner","TEXT",""],
["local_trail_id","fc_local_trail_reg","local_trail_id","SHORT",""],
["regional_trail_id","fc_regional_trail_reg","regional_trail_id","SHORT",""],
["submissionid_scip","fc_cip_signage_trail_reg","submissionid_scip","TEXT",""],
["validated_scip","fc_cip_signage_trail_reg","validated_scip","SHORT","yes_no"],
["submissionid_wayfinding","fc_signage_wayfinding_trail_reg","submissionid_wayfinding","TEXT",""],
["validated_wayfinding","fc_signage_wayfinding_trail_reg","validated_wayfinding","SHORT","yes_no"],
["category","fc_category_reg","category","SHORT","category"],
["network","fc_network_reg","network","SHORT","network"],
["trail_type","fc_trail_type_reg","trail_type","SHORT","trail_type"],
["environment","fc_environment_reg","environment","SHORT","environment"],
["paddling","fc_act_paddling_reg","paddling","SHORT","yes_no"],
["cross_country_skiing","fc_act_cross_country_skiing_reg","cross_country_skiing","SHORT","yes_no"],
["dog_sledding","fc_act_dog_sledding_reg","dog_sledding","SHORT","yes_no"],
["fat_biking","fc_act_fat_biking_reg","fat_biking","SHORT","yes_no"],
["horseback_riding","fc_act_horseback_riding_reg","horseback_riding","SHORT","yes_no"],
["mountain_biking","fc_act_mountain_biking_reg","mountain_biking","SHORT","yes_no"],
["road_cycling","fc_act_road_cycling_reg","road_cycling","SHORT","yes_no"],
["rollerblading","fc_act_rollerblading_reg","rollerblading","SHORT","yes_no"],
["snowmobiling","fc_act_snowmobiling_reg","snowmobiling","SHORT","yes_no"],
["snowshoeing","fc_act_snowshoeing_reg","snowshoeing","SHORT","yes_no"],
["walking","fc_act_walking_reg","walking","SHORT","yes_no"],
["atv","fc_atv_reg","atv","SHORT","yes_no"],
["gis_data_accuracy","fc_gis_data_reg","gis_data_accuracy","SHORT","gis_data_accuracy"],
["gis_data_type","fc_gis_data_reg","gis_data_type","SHORT","gis_data_type"],
["gis_data_date","fc_gis_data_reg","gis_data_date","DATE",""],
["gis_data_source","fc_gis_data_reg","gis_data_source","TEXT",""],
["gis_data_url","fc_gis_data_reg","gis_data_url","TEXT",""],
["gis_change_explanation","fc_gis_data_reg","gis_change_explanation","SHORT","gis_change_explanation"]
]
