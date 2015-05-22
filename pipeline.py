import lib
#TODO:
# parameters in addition to json configuration 
# generic function for running commands
# library/class design
# support files in functions, in addition to folders


# store bowtie output
# create_trackdb format parameter

#Coverage:
#fastq->->sam(bwt file)->bam->sorted bam->bedGraph->->bedClip->sorted BedGraph (we don't need) -> bigWig
#bedtools genomecov -bg -ibam /cs/wetlab/melerz/nisoy/bam_files/8-NoIAA-6Alpha_S3_sorted.bam -g sacCer3.genome > genome_coverage_bigbed.bigbed
#sort -k1,1 -k2,2n genome_coverage_bigbed.bigbed > sorted.bedGraph
#./bedGraphToBigWig bedClip_output.bed genome_reference_sorted.sacC nisoy.bw
def run(name,csv,illumina_name,configuration,workflow,log=None):
	try:
		if not log:
			log = logging.getLogger(__name__)

		workflow = lib.config['workflows'][workflow]
		for step in workflow:
			print "Running step:%s"%step
			log.info("Currently step:{0}".format(step))
			step_module=importlib.import_module(lib.step)
			if step == "bcl_to_fastq":
				step_module.run(name,csv,illumina_name,configuration)
			else:
				step_module.run(name)
				
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


if __name__ == "__main__":
	# parser = argparse.ArgumentParser()
	# parser.add_argument("--config","-c",help="The path to configuration file in JSON format")	
	# parser.add_argument("--data","-d",help="The path to data file in JSON format")
	# parser.add_argument("log=DEBUG")	
	# parser.add_argument("level=DEBUG")	
	# parser.parse_args()
	data_file="./data.json"
	if data_file:

		data= json.load(open(data))
		data_name=data['name']
		data_csv=data['csv']
		data_illumina=data['illumina_name']
		data_configuration=data['configuration']
		data_workflow=data['workflow']

	logger = configure_logging(log_level="DEBUG",log_file="./pipeline.log")
	run(name=data_name,csv=data_csv,illumina_name=data_illumina,
				configuration=data_configuration,workflow=data_workflow,log=logger)
