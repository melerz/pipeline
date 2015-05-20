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
		working_dir = config['settings']['WORKING_DIR']+config['data']['url']
		bowtie_dir = config['settings']['BOWTIE_OUTPUT_DIR']
		bam_dir = config['settings']['BAM_OUTPUT_DIR']
		samtools_exec = config['settings']['tools']['samtools']['exec']

		bowtie_full_path=os.path.join(working_dir,bowtie_dir)
		bam_full_path=os.path.join(working_dir,bam_dir)


		create_bam(bowtie_path=bowtie_full_path,output=bam_full_path,exec_path=samtools_exec)

	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		os.chdir(currentLocation)
		raise Exception("Error in sam_to_bam: %s,%s,%s,%s"%(e,exc_type,exc_obj,fname))


def create_bam(bowtie_path,output="./bam_files/",exec_path="/cs/wetlab/pipeline/samtools/bin/samtools"):
		logger.debug("create_bam:START")
		logger.debug("create_bam: changing dir: %s"%bowtie_path)
		currentLocation = os.getcwd()
		os.chdir(bowtie_path)
		if not (os.path.isdir(output)):
			os.mkdir(output)
		#for bowtie_file in glob.glob("*"):
		for bowtie_file in ['1-C09_S1.bwt','1-C46_S28.bwt']:
			cmd = [exec_path,"view","-bS",bowtie_file]
			bam_file_path = os.path.join(output,bowtie_file) +".bam"
			logger.debug("create_bam: bam file: %s",bam_file_path)
			p = subprocess.Popen(cmd,stdout=open(bam_file_path,"w+"),stderr=subprocess.PIPE)

		logger.debug("create_bam: changing dir: %s"%bowtie_path)
		logger.debug("create_bam:END")
		os.chdir(currentLocation)


