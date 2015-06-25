from lib import *
from os.path import expanduser
#from lib.server import api
#TODO:

# -f switch implementation
# - beutify output
# - slum permissions
# - multiprocessing pooling
# -improve logging -> log for each experiment + time
# -
# support files in functions, in addition to folders

# create_trackdb format parameter

#Coverage:
#fastq->->sam(bwt file)->bam->sorted bam->bedGraph->->bedClip->sorted BedGraph (we don't need) -> bigWig
#bedtools genomecov -bg -ibam /cs/wetlab/melerz/nisoy/bam_files/8-NoIAA-6Alpha_S3_sorted.bam -g sacCer3.genome > genome_coverage_bigbed.bigbed
#sort -k1,1 -k2,2n genome_coverage_bigbed.bigbed > sorted.bedGraph
#./bedGraphToBigWig bedClip_output.bed genome_reference_sorted.sacC nisoy.bw
menue={
		"name":"get_name",
		"csv":"get_csv_list",
		"illumina":"get_illumina",
		"workflow":"get_workflow"
}
def run(name,csv,illumina_name,workflow,configuration=None,log=None,force=False):
	'''
		Args:
			name - The name of the experiment
			csv  - The name of the csv file
			illumina_name - The full path / name of the Illumina RAW data folder
			workflow - The name of the workflow you want to use (*All* workflows start with bcl_to_fastq step)
			configuration - The customized configuration you want for the RunInfo.xml file
			log - logger
			force - Override existing folders all along the pipeline process

		Returns:
			In case the workflow contains genome browser, the function returns the URL for the hub directory,
			otherwise, void.
	'''


	try:
		if not log:
			log = logging.getLogger(__name__)
		workflow = config['workflows'][workflow]

		step_module=importlib.import_module("lib.utils.bcl_to_fastq")

		step_module.run(name,csv,illumina_name,configuration,workflow)
		# for step in workflow:
		# 	print "Running step:%s"%step
		# 	log.info("Currently step:{0}".format(step))
		# 	step_module=importlib.import_module("lib.utils.%s"%step)
		# 	if step == "bcl_to_fastq":
		# 		step_module.run(name,csv,illumina_name,configuration)
		# 	else:
		# 		step_module.run(name)
		log.info("Finished executing pipeline!")

	except Exception as e:
		print e
		if log:
			log.exception("an error has been occured: %s"%e)
		else:
			print "Error while running pipeline!. %s"%e



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
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-n","--name",help="The experiment name")	
	parser.add_argument("-csv","--csv",help="The name of the SampleSheet.csv file you want to use")
	parser.add_argument("-i","--illumina",
						help="The name of the illumina data dir.This is the folder where the RAW data is")	
	parser.add_argument("-w","--workflow",help="The name of the workflow you want to execute",default="all")
	parser.add_argument("-ip","--ipaddress",help="The IP Address of the API server",default="127.0.0.1")
	parser.add_argument("-c","--configuration",help="Read configuration .\
													 (read,cycles,isIndexed) - One or more ':' separated tuples",type=get_read)
	parser.add_argument("-f","--force",help="Deleting existing folders while executing the pipeline",action="store_true")		

	args=parser.parse_args()

	data_force			= args.force
	data_name 			= validate_param("name", args.name)
	data_csv 			= validate_param("csv", args.csv)
	data_illumina 		= validate_param("illumina", args.illumina)
	data_workflow 		= validate_param("workflow", args.workflow)
	data_configuration  = args.configuration
	logger = configure_logging(log_level="DEBUG",log_file="./pipeline.log")
	run(name=data_name,csv=data_csv,illumina_name=data_illumina,
				configuration=data_configuration,workflow=data_workflow,log=logger,force=data_force)


