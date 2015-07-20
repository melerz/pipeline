from lib import *
from os.path import expanduser
import multiprocessing

#Coverage:
#fastq->->sam(bwt file)->bam->sorted bam->bedGraph->->bedClip->sorted BedGraph (we don't need) -> bigWig
#bedtools genomecov -bg -ibam /cs/wetlab/melerz/nisoy/bam_files/8-NoIAA-6Alpha_S3_sorted.bam -g sacCer3.genome > genome_coverage_bigbed.bigbed
#sort -k1,1 -k2,2n genome_coverage_bigbed.bigbed > sorted.bedGraph
#./bedGraphToBigWig bedClip_output.bed genome_reference_sorted.sacC nisoy.bw

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
	return set([os.path.basename(fastq).split("_")[0] for 
						fastq in glob.glob(os.path.join(path,"*.fastq.gz") )
										if not re.match(".*Undetermined.*",fastq)])

def pool_init(lock_obj):
	global lock
	lock = lock_obj

def run_workflow_on_sample(params):
	'''
		The target function for the Pool.map function
		Args:
			- params: tuple of the form: (experiment_name,sample_name,workflow,working_directory,kwargs)
	'''
	experiment_name,sample_name,workflow,working_directory,kwargs = params
	for step in workflow:
		print "{sample}: Running step:{step}".format(sample=sample_name,step=step)
		#log.info("{sample}: Currently step:{step}".format(sample=sample_name,step=step))
		step_module=importlib.import_module("lib.utils.%s"%step)

		step_module.run(experiment_name,sample_name,working_directory,**kwargs)

def run_samples(experiment_name,samples_list,workflow,working_directory,**kwargs):
	lock_obj = multiprocessing.Lock()
	throttle_limit = len(samples_list)
	pool = multiprocessing.Pool(processes=throttle_limit,initializer=pool_init,initargs=(1,))

	#Build tuple list for passing more than one argument to the Pool.map() function - 
	#[(experiment_name,sample_name1,workflow),(experiment_name,sample_name2,workflow)]

	tuple_params = [(experiment_name,sample,workflow,working_directory,kwargs) for sample in samples_list]

	pool.map(run_workflow_on_sample, tuple_params)

def configure_logging(log_level="INFO",log_file="./pipeline.log"):
	loglevel = getattr(logging,log_level.upper(),None)
	if not isinstance(loglevel, int):
		raise Exception("Invalid log level: %s" %loglevel)
	logger=logging.getLogger(__name__)
	logger.setLevel(loglevel)
	file_handler = logging.FileHandler(log_file)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger

def get_read(configuration):
	'''
		Argument type helper function for argparse
	'''
	try:
		read_data_list=configuration.split(":")
		read_list=[]
		for read in read_data_list:
			read_number,cycles,is_indexed = read[1:-1].split(",")
			is_indexed = is_indexed.upper()
			read_list.append((read_number,cycles,is_indexed))
		return read_list
	except Exception, e:
		raise argparse.ArgumentTypeError(e.message)

def validate_param(name,value):
	if not value:
		#menu enters here
		raise Exception("You've forgot to specify %s"%name)
	return value

def cleanup(name):
	'''
		Cleans the experiment folders when the pipeline exists unexpectedly (Ctl+C)
	'''
	if not name:
		raise Exception("No experiment to clean")

	#Back to the main dir
	os.chdir(main_dir)

	#CS Directory
	cs_dir = funcs.build_cs_dir_path(name)

	#Working directory dir
	wd_dir = funcs.get_working_directory(name)

	#Initial directory
	init_dir = os.path.join(os.getcwd(),name)

	#Delete CS directory
	try:
		shutil.rmtree(cs_dir,ignore_errors=True)
		print "%s:Cleaned %s"%(name,cs_dir)
	except Exception,e:
		print "Cleanup: Couldn't delete %s: %s"%(cs_dir,str(e))

	#Unlink working directory (~/www/)
	try:
		os.unlink(wd_dir)
		print "%s:Cleaned %s"%(name,wd_dir)
	except Exception,e:
		print "Cleanup: Couldn't delete %s: %s"%(wd_dir,str(e))

	#Delete initial directory (local directory linked to the Illumina data)
	try:
		shutil.rmtree(init_dir)
		print "%s:Cleaned %s"%(name,init_dir)
	except Exception,e:
		print "Cleanup: Couldn't delete %s: %s"%(init_dir,str(e))

	#Delete log file
	#log_file is declared in main
	try:
		os.remove(log_file)
		print "%s:Cleaned %s"%(name,log_file)
	except Exception,e:
		print "Cleanup: Couldn't delete %s: %s"%(log_file,str(e))

def signal_handler(signal,frame):
	if not data_name:
		raise Exception("No experiment to clean")
	cleanup(name = data_name )
	sys.exit(0)

def init_sigint_handler(event):
		signal.signal(event, signal_handler)

#def run(name,csv,illumina_name,workflow,configuration=None,log=None,force=False,disable_hub=False):
def run(name,csv,illumina_name,workflow,**kwargs):
	'''
		Args:
			name - The name of the experiment
			csv  - The name of the csv file
			illumina_name - The full path / name of the Illumina RAW data folder
			workflow - The name of the workflow you want to use (*All* workflows start with bcl_to_fastq step)

			Keywords arguments:
				configuration - The customized configuration you want for the RunInfo.xml file
				log - logger
				force - Override existing folders all along the pipeline process
				fastq - Path to a folder contains fastq files. If specified, pipeline skips bcl_to_fastq
				disable_hub - True/False - To create hub or not.

		Returns:
			In case the workflow contains genome browser, the function returns the URL for the hub directory,
			otherwise, void.
	'''


	try:
		#Extract kwargs
		log = kwargs.get('log',None)
		#force = kwargs.get('force',None)
		workingdir = kwargs.get('workingdir',None)
		configuration = kwargs.get('configuration',None)
		disable_hub = kwargs.get('disable_hub',None)


		if not log:
			log = logging.getLogger(__name__)

		workflow = config['workflows'][workflow]


		experiment_working_directory = workingdir or funcs.get_working_directory(name)#Function in configuration.config
		#if os.path.isdir(experiment_working_directory) and glob.glob(os.path.join(working_dir_from_user,"*.fastq.gz")):

		#Run bcl_to_fastq only when working dir path is not specified
		if not workingdir:
			step_module=importlib.import_module("lib.utils.bcl_to_fastq")

			step_module.run(name,experiment_working_directory,csv,illumina_name,configuration)

		if workflow:
			#Get samples list from the experiment folder
			samples_list = get_samples_from_fastq_dir(experiment_working_directory)
			#For each of every sample, we will run the workflow process
			run_samples(name,samples_list,workflow,experiment_working_directory)

		#
		#If we have genome_browser in the workflow, create the hub directory first
		if not disable_hub:
			print("Creating unified hub directory")
			hub_module = importlib.import_module("lib.utils.genome_browser")
			#Create the hub directory
			hub_module.run(name,experiment_working_directory)				

		log.info("Finished executing pipeline!")

	except Exception as e:
		print e
		if log:
			log.exception("an error has been occured: %s"%e)
		else:
			print "Error while running pipeline!. %s"%e

if __name__ == "__main__":

	#Init Arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("name",help="The experiment name")

	run_group = parser.add_argument_group('Run','Create an experiment')

	run_group.add_argument("-csv","--csv",help="The name of the SampleSheet.csv file you want to use")
	run_group.add_argument("-i","--illumina",
						help="The name of the illumina data dir.This is the folder where the RAW data is")	
	run_group.add_argument("-w","--workflow",help="The name of the workflow you want to execute",default="all")
	run_group.add_argument("-skip","--skipfastq",help="The path to a folder contains fastq files.\
																	 All files will be created in this folder. If specified without value, \
																	 										defaults to ~/www/<experiment_name>",const=funcs.build_profile_dir_path,nargs='?')		
	run_group.add_argument("-ip","--ipaddress",help="The IP Address of the API server",default="127.0.0.1")
	run_group.add_argument("-c","--configuration",help="Read configuration .\
													 (read,cycles,isIndexed) - One or more ':' separated tuples",type=get_read)
	run_group.add_argument("-f","--force",help="Overiding existing folders while executing the pipeline",action="store_true")		
	run_group.add_argument("--nohub",help="If set, it won't create a hub directory for all bigwig files.",action="store_true")		

	clean_group = parser.add_argument_group('Clean','Clean an experiment')
	clean_group.add_argument("-cl","--clean",help="Deletes all experiment directories and data",action="store_true")
	
	args=parser.parse_args()

	data_name = validate_param("name", args.name)
	data_clean = args.clean

	if(data_clean):
		answer = raw_input("Are you sure you want to delete experiment %s?"%data_name)
		if answer.lower() == "yes": 
			cleanup(name)
		sys.exit(0)

	#Required Parameters
	data_csv 			= validate_param("csv", args.csv)
	data_illumina 		= validate_param("illumina", args.illumina)
	data_workflow 		= validate_param("workflow", args.workflow)

	#Logging
	log_file = os.path.join(os.getcwd(),data_name+".log")
	logger = configure_logging(log_level="DEBUG",log_file=log_file)

	#Non-Required Parameters
	kwrags = {
		"disable_hub":args.nohub,
		"force":args.force,
		"configuration":args.configuration,
		"workingdir":args.skipfastq,
		"log":logger
	}


	#Save current location (Mainly for SIGINT [CTL+C] handler)
	main_dir = os.getcwd()
	#Init SIGINT signal handler
	#init_sigint_handler(signal.SIGINT)

	#Run main functin
	run(name=data_name,csv=data_csv,illumina_name=data_illumina,workflow=data_workflow,**kwrags)


