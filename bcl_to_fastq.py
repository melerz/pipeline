import logging
import os
from lib import createfastq_operations as operations
import sys
import requests

def run(data,logger=None):
	'''
		For each expierment in the data, create a folder with the expirement name, and init it by
		calling the createRundir function.

		data is a JSON forematted data, that describe the current run (run->expierments->(configuration,samples))

		This method first calls to createRundir (links, copy the RunInfo.xml),
		and then, for each experiment it calls for runExpirement method
	'''
	try:
		#This logger object is used in the library too
		if not logger:
			logger = logging.getLogger(__name__)
			
		logger.info(("Currently experiment:{0}".format(data['name'])))
		
		#Save the current location because createRunDir change it
		currentLocation=os.getcwd()

		logger.info("{0}: Init Directory".format(data['name']))
		#Init experiment folder (Link files, RunInfo.xml, create output directory)
		operations.createRundir(data)

		logger.info("{0}: Run bcl2fastq".format(data['name']))
		#running bcl2fastq in the current experiment folder.
		#Output folder is fastq, created by createRundir
		operations.runExpirement(data)

		# update_data(settings.JOB_ENDPOINT+"%s/"%data['job_id'],
		# 		{'status':'Finished','description':'Succefully Finished to generate fastq'})
		# #Changing back to the main folder

		os.chdir(currentLocation)

		logger.info("{0}: Finished".format(data['name']))

	except Exception as e:
		# update_data(settings.JOB_ENDPOINT+"%s/"%data['job_id'],
		# 	{'status':'Failed','description':'%s'%e})
		raise Exception("Error in bcl_to_fastq.py: %s",e)