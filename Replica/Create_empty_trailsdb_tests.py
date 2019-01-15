import sys, arcpy
sys.path.append("C:\Trailsdb_Scripts\Variables")
from Connection_to_trailsdb import *

#Create TrailsDB_tests Geodatabase
arcpy.CreateEnterpriseGeodatabase_management("POSTGRESQL", instance, gdbName_tests, "DATABASE_AUTH", dbAdmin, dbAdminPassword, "SDE_SCHEMA", gdbAdminAndPassword, gdbAdminAndPassword, "", keycodes)