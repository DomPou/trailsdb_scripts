import smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append("C:\\Trailsdb_Scripts\\Variables")
from GIS_email_variables import *

sys.path.append(errorsDetectionFolder)
from Salesforce_vs_trailsdb_managers_owners_v1 import managersOwnersErrors
#from Salesforce_vs_trailsdb_project_codes_points import missingProjectsPoints
#from Salesforce_vs_trailsdb_project_codes_lines import missingProjectsLines
#from Null_values_in_trailsdb import nullValues
#from Unknown_values_in_trailsdb import unknownValue

#sys.path.append("C:\\Trailsdb_Scripts\\\\Functions")
#from Send_email_with_Microsoft_Exchange import trailsdbScriptSuccess

def trailsdbScriptSuccess(scriptName):

	msg = MIMEMultipart()
	subject = "Trailsdb script completed - " + scriptName
	body = """
""" + scriptName + """ completed without errors
	"""

	msg['From'] = gisAddress
	msg['To'] = trailsdbErrorsAddress
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain', "utf-8"))
	text=msg.as_string()
	# Send the message via our SMTP server
	server = smtplib.SMTP('smtp.office365.com', 587)
	server.ehlo()
	server.starttls()
	server.login(gisAddress, gisPassword)
	server.sendmail(gisAddress, trailsdbErrorsAddress, text)
	server.quit()


#nullValues()
#unknownValue()
#missingProjectsPoints()
#missingProjectsLines()
managersOwnersErrors()

#Send an email once it is done saying everything worked
trailsdbScriptSuccess("task_scheduler_errors_emails.bat")
