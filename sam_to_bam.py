import json
import subprocess
import os
import glob
import sys
import logging
import re
logger = logging.getLogger("__main__")
def run(config_file="./config.json"):
	try:
		currentLocation=os.getcwd()
		logger.info("sam to bam process....")
		print "Running samtools..."
		config = json.load(open(config_file))
		logger.info("Loading Config files...")
		samtools_exec = config['settings']['tools']['samtools']['exec']
		bam_dir = config['settings']['BAM_OUTPUT_DIR']
		cmd="%s view -bS %s > %s.bam"
	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		os.chdir(currentLocation)
		raise Exception("Error in sam_to_bam: %s,%s,%s,%s"%(e,exc_type,exc_obj,fname))