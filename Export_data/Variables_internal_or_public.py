import sys, arcpy
sys.path.append("C:\Trailsdb_Scripts\Variables")
from Connection_to_trailsdb import *

fieldsToIgnoreOrDelete = ["objectid", "shape", "globalid", "created_user", "created_date", "last_edited_user", "last_edited_date"]

#Feature class, field name, public value
fieldsPublicInfo = [
	["province_en",""],
	["province_fr",""],
	["trail_status","Operational Trail"],
	["local_trail_name_en",""],
	["local_trail_name_fr",""],
	["local_trail_km",""],
	["activities_en",""],
	["activities_fr",""],
	["environment_agg_en",""],
	["environment_agg_fr",""],
	["trail_type_agg_en",""],
	["trail_type_agg_fr",""],
	["regional_trail_name_en",""],
	["regional_trail_name_fr",""]
]

#Field join, field
tablesFieldsInternalPublicInfo =[
	["local_trail_id","local_trail_name_en"],
	["local_trail_id","local_trail_name_fr"],
	["project_code","project_name"],
	["phase_code","phase_name"],
	["regional_trail_id","regional_trail_name_en"],
	["regional_trail_id","regional_trail_name_fr"],
	["trail_code","trail_code_name_en"],
	["trail_code","trail_code_name_fr"],
	["trail_code","trail_code_description_en"],
	["trail_code","trail_code_description_fr"],
	["trail_code","trail_code_notes_en"],
	["trail_code","trail_code_notes_fr"],
	["trail_code","trail_code_road_en"],
	["trail_code","trail_code_road_fr"],
	["trail_code","trail_code_atv_en"],
	["trail_code","trail_code_atv_fr"],
	["trail_code","trail_code_tctmapsurl"],
	["trail_code","trail_code_groupname1"],
	["trail_code","trail_code_websiteurl1"],
	["trail_code","trail_code_groupname2"],
	["trail_code","trail_code_websiteurl2"],
	["trail_code","trail_code_groupname3"],
	["trail_code","trail_code_websiteurl3"],
	["trail_code","trail_code_groupname4"],
	["trail_code","trail_code_websiteurl4"]
]
