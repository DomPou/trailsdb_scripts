import sys

sys.path.append("C:\\Trailsdb_Scripts\\Merge_pro_reg")
from Salesforce_objects_joins_trailsdb import joinsSfTrailsdb
from Merge_signage_posts_and_trails import mergeSignage


sys.path.append("C:\\Trailsdb_Scripts\\\\Functions")
from Send_email_with_Microsoft_Exchange import trailsdbScriptSuccess

joinsSfTrailsdb()
mergeSignage()

#Send an email once it is done saying everything worked
trailsdbScriptSuccess("task_scheduler_joins.bat")
