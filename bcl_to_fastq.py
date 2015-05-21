import logging
import os
from lib import createfastq_operations as operations
import sys
import json
# createRundir(name,fastq_output_dir,illumina_experiment_dir):
logger = logging.getLogger("__main__")
def run(config_file="./config.json",data_file="./data.json"):
	'''
		For each expierment in the data, create a folder with the expirement name, and init it by
		calling the createRundir function.

		data is a JSON forematted data, that describe the current run (run->expierments->(configuration,samples))

		This method first calls to createRundir (links, copy the RunInfo.xml),
		and then, for each experiment it calls for runExpirement method
	'''
	try:
		global logger
		#This logger object is used in the library too
		if not logger:
			logger = logging.getLogger(__name__)

		#Load Configuration and data files
		config 	= json.load(open(config_file))
		data 	= json.load(open(data_file))

		
		print "Running bcl2fastq"

		#Export params from JSON
		experiment_name 	   		= data['name']
		samplesheet					= data['csv']
		xml_configuration			= data['coniguration']
		illumina_experiment_data    = config['BASE_ILLUMINA_PATH']+data['illumina_name']
		output_dir 					= config['WORKING_DIR']
		#End export params from JSON

		#Save the current location because this function change it
		currentLocation=os.getcwd()
		
		logger.info(("Currently experiment:{0}".format(experiment_name)))
		

		#Check if experiment dir is already exist
		if os.path.isdir(experiment_name):
			raise Exception("Experiment dir is already exist! exiting now...")

		os.mkdir(experiment_name)
		os.chdir(experiment_name)

		logger.info("{0}: Init Directory".format(experiment_name))
		#Init experiment folder (Link files, RunInfo.xml, create output directory)
		operations.popluateDir(experiment_name,output_dir,illumina_experiment_data)

		logger.info("{0}: Run bcl2fastq".format(experiment_name))
		#running bcl2fastq in the current experiment folder.
		#Output folder is fastq, created by popluateDir
		operations.runExpirement(xml_configuration,samplesheet)

		# update_data(settings.JOB_ENDPOINT+"%s/"%data['job_id'],
		# 		{'status':'Finished','description':'Succefully Finished to generate fastq'})
		# #Changing back to the main folder

		os.chdir(currentLocation)

		logger.info("{0}: Finished".format(data['name']))

	except Exception as e:
		# update_data(settings.JOB_ENDPOINT+"%s/"%data['job_id'],
		# 	{'status':'Failed','description':'%s'%e})
		os.chdir(currentLocation)
		raise Exception("Error in bcl_to_fastq.py: %s",e)