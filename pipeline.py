import logging
import os
import sys
import json
import importlib


#TODO:
# generic function for running commands
# library/class design
# parameters instead of json configuration 
# support files in functions, in addition to folders

#Coverage:
#fastq->->sam(bwt file)->bam->sorted bam->bedGraph->->bedClip->sorted BedGraph (we don't need) -> bigWig
#bedtools genomecov -bg -ibam /cs/wetlab/melerz/nisoy/bam_files/8-NoIAA-6Alpha_S3_sorted.bam -g sacCer3.genome > genome_coverage_bigbed.bigbed
#sort -k1,1 -k2,2n genome_coverage_bigbed.bigbed > sorted.bedGraph
#./bedGraphToBigWig bedClip_output.bed genome_reference_sorted.sacC nisoy.bw
def run(config_file="./config.json",log=None):
	try:
		if not log:
			log = logging.getLogger(__name__)
		log.info("loading config file...")
		config = json.load(open(config_file))
		workflow = config['workflows']['fastq_only']
		for step in workflow['pipeline']:
			log.info("Currently step:{0}".format(step))
			print "Running step:%s"%step
			step_module=importlib.import_module(step)
			#step_module.run(config['data'],logger=log)
			step_module.run()
		log.info("Finished executing pipeline!")

	except Exception as e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type,fname,exc_tb.tb_lineno)
		if log:
			log.exception("an error has been occured: %s"%e)
		else:
			print "Error while running pipeline!. See log file for further details:%s"%e



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
	logger = configure_logging(log_level="DEBUG",log_file="./pipeline.log")
	run(config_file="./config.json",log=logger)
