# import logging
# import os
# from lib import createfastq_operations as operations
# import sys
# import json
# createRundir(name,fastq_output_dir,illumina_experiment_dir):
from .. import *
import createfastq_operations as operations
import multiprocessing
logger = logging.getLogger("__main__")
def run(experiment_name,samplesheet_name,illumina_name,xml_configuration,workflow,**kwargs):
	'''
		For each expierment in the data, create a folder with the expirement name, and init it by
		calling the createRundir function.

		data is a JSON forematted data, that describe the current run (run->expierments->(configuration,samples))

		This method first calls to createRundir (links, copy the RunInfo.xml),
		and then, for each experiment it calls for runExpirement method
	'''
	try:
		#This logger object is used in the library too
		global logger
		currentLocation=os.getcwd()
		if not logger:
			logger = logging.getLogger(__name__)
		
		print "Running bcl2fastq"

		#Export from config
		if not os.path.isabs(illumina_name):
			illumina_experiment_data    = config['BASE_ILLUMINA_PATH']+illumina_name
		else:
			illumina_experiment_data 	= illumina_name
		output_dir 						= funcs.get_working_directory(experiment_name)#Function in configuration.config
		csv_upload_dir					= config['MEDIA_ROOT']
		#End export params from config

		#Save the current location because this function change it

		logger.info(("Currently experiment:{0}".format(experiment_name)))
		

		#Check if experiment dir is already exist
#		if os.path.isdir(experiment_name):
#			raise Exception("Experiment dir is already exist! exiting now...")

#		os.mkdir(experiment_name)
#		os.chdir(experiment_name)

#		logger.info("{0}: Init Directory".format(experiment_name))
		#Init experiment folder (Link files, RunInfo.xml, create output directory)
#		operations.popluateDir(experiment_name,output_dir,illumina_experiment_data)

#		logger.info("{0}: Run bcl2fastq".format(experiment_name))
		#running bcl2fastq in the current experiment folder.
		#Output folder is fastq, created by popluateDir

		#Create samplesheet path
#		if not samplesheet_name.endswith(".csv"):
#			samplesheet = csv_upload_dir + samplesheet_name + ".csv"
#		else:
#			samplesheet = csv_upload_dir + samplesheet_name 
#		operations.runExpirement(xml_configuration,samplesheet)

		# update_data(settings.JOB_ENDPOINT+"%s/"%data['job_id'],
		# 		{'status':'Finished','description':'Succefully Finished to generate fastq'})
		# #Changing back to the main folder


		logger.info("{0}: Finished".format(experiment_name))

		#If we have genome_browser in the workflow, create the hub directory first
		# if 'genome_browser' in workflow:
		# 	#create folder

		#Get samples list from the experiment folder
		samples_list = get_samples_from_fastq_dir(output_dir)
		#For each of every sample, we will run the workflow process
		run_samples(experiment_name,samples_list,workflow)
		
		os.chdir(currentLocation)
	except Exception as e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		if currentLocation:
			os.chdir(currentLocation)
		raise Exception("Error in %s: %s,%s,%s,%s"%(fname,e,exc_type,exc_obj,exc_tb.tb_lineno))


def get_samples_from_fastq_dir(path):
	'''
		This function return a set (unique values) of sample names inside the fastq dir (only their names)
		Ex:
			If we have a fastq file named - 'GCY20-02_S3_R001_L001.fastq.gz', than the name will be: 'GCY20-02'
		Args: 
			path: path to the fastq files dir
		Returns: 
			A set of samples names
	'''
	return set([os.path.basename(fastq.split("_")[0]) for 
						fastq in glob.glob(os.path.join(path,"*.fastq.gz") )
										if not re.match(".*Undetermined.*",fastq)])

def pool_init(lock_obj):
	global lock
	lock = lock_obj

def run_workflow_on_sample(params):
	'''
		The target function for the Pool.map function
		Args:
			- params: tuple of the form: (experiment_name,sample_name,workflow)
	'''
	experiment_name,sample_name,workflow = params
	for step in workflow:
		print "{sample}: Running step:{step}".format(sample=sample_name,step=step)
		log.info("{sample}: Currently step:{step}".format(sample=sample_name,step=step))
		step_module=importlib.import_module("lib.utils.%s"%step)

		step_module.run(experiment_name,sample_name)

def run_samples(experiment_name,samples_list,workflow):
	lock_obj = multiprocessing.Lock()
	throttle_limit = len(samples_list)
	pool = multiprocessing.Pool(processes=throttle_limit,initializer=pool_init,initargs=(1,))

	#Build tuple list for passing more than one argument to the Pool.map() function - 
	#[(experiment_name,sample_name1,workflow),(experiment_name,sample_name2,workflow)]

	tuple_params = [(experiment_name,sample,workflow) for sample in samples_list]

	pool.map(run_workflow_on_sample, tuple_params)
