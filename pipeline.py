import logging
import os
import sys
import json
import importlib
def run(log_level="INFO",log_file="./fastq-log.log",config_file="./config.json"):

	try:
		logger = configure_logging(log_level,log_file)
		logger.info("loading config file...")
		config = json.load(open(config_file))
		workflow = config['workflows']['fastq_only']
		for step in workflow['pipeline']:
			logger.info("Currently step:{0}".format(step))
			step_module=importlib.import_module(step)
			step_module.run(config['data'],logger)
		logger.info("Finished executing pipeline!")

	except Exception as e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

		print(exc_type,fname,exc_tb.tb_lineno)
		if logger:
			logger.exception("an error has been occured: %s"%e)
		else:
			print "main exception. See log file for further details:%s"%e



def configure_logging(log_level="INFO",log_file="./fastq-log.log"):
	loglevel = getattr(logging,log_level.upper(),None)
	if not isinstance(loglevel, int):
		raise Exception("Invalid log level: %s" %loglevel)
	#logging.basicConfig(filename=log_file,level=loglevel,foremat="%(name)s:%(levelname)s:%(message)s")
	logger=logging.getLogger(__name__) #need to change that to __name__
	logger.setLevel(loglevel)
	file_handler = logging.FileHandler(log_file)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger


if __name__ == "__main__":
	run(log_level="INFO",log_file="./fastq-log.log",config_file="./config.json")
