# import json
# import subprocess
# import os
# import glob
# import sys
# import logging
# import re
from .. import *
logger = logging.getLogger("__main__")
def run(experiment_name,**kwargs):
	try:
		currentLocation=os.getcwd()
		logger.info("sam to bam process....")
		print "Running samtools..."

		#Export params from JSON:
		working_dir 	= config['WORKING_DIR']+experiment_name
		bowtie_dir 		= config['BOWTIE_OUTPUT_DIR']
		bam_dir 		= config['BAM_OUTPUT_DIR']
		samtools_exec 	= config['tools']['samtools']['exec']
		#End export params from JSON

		bowtie_full_path=os.path.join(working_dir,bowtie_dir)
		bam_full_path=os.path.join(working_dir,bam_dir)


		create_bam(bowtie_path=bowtie_full_path,output=bam_full_path,exec_path=samtools_exec)

	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		os.chdir(currentLocation)
		raise Exception("Error in %s: %s,%s,%s,%s"%(fname,e,exc_type,exc_obj,exc_tb.tb_lineno))


def create_bam(bowtie_path,output="./bam_files/",exec_path="/cs/wetlab/pipeline/samtools/bin/samtools"):
	try:
		logger.debug("create_bam:START")
		if not (os.path.isdir(output)):
			os.mkdir(output)
		logger.debug("create_bam: changing dir: %s"%bowtie_path)
		currentLocation = os.getcwd()
		os.chdir(bowtie_path)
		for bowtie_file in glob.glob("*"):

			#Init
			bam_file_without_prefix = os.path.join(output,bowtie_file)
			bam_file_path 			= bam_file_without_prefix +".bam"
			bam_sorted_file_path 	= bam_file_without_prefix+"_sorted"
			cmd 					= [exec_path,"view","-bS",bowtie_file]
			cmd_sort 				= [exec_path,"sort",bam_file_path,bam_sorted_file_path]
			#Init

			logger.debug("Currently processing bowtie file: %s"%(bowtie_file))
			#Create BAM file
			logger.debug("create_bam: bam file: %s",bam_file_path)
			with open(bam_file_path,"w+") as f:
				p = subprocess.Popen(cmd,stdout=f,stderr=subprocess.PIPE)
				output_cmd,err = p.communicate()
				if p.returncode != 0:
					raise Exception("Converting SAM to BAM: %s" %(err))

			#Create sorted BAM file
			logger.debug("create_bam: sort bam file: %s",bam_sorted_file_path)
			p = subprocess.Popen(cmd_sort,stderr=subprocess.PIPE)
			output_cmd,err = p.communicate()
			if p.returncode != 0:
				raise Exception("Sorting bam : %s" %(err))
			#Delete the original BAM file
			logger.debug("Succefully sort the BAM file. Remove original BAM file: %s"%(bam_file_path))
			os.remove(bam_file_path)

		logger.debug("create_bam: changing dir: %s"%currentLocation)
		os.chdir(currentLocation)
		logger.debug("create_bam:END")
	except Exception as e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		raise Exception("Error in create_bam function: Message: %s : Type: %s : Object: %s : Line: %s"%(e,
																			exc_type,exc_obj,exc_tb.tb_lineno))




