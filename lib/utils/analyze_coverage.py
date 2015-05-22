# import json
# import subprocess
# import os
# import glob
# import sys
# import logging
# import re
from . import config
logger = logging.getLogger("__main__")
'''
	This module receives BAM files, and output bedGraph file format along with
	bigWig file format.
'''
def run(experiment_name):
	try:
		currentLocation=os.getcwd()
		logger.info("analyze:coverage")
		print "Running coverage analyze"
		if experiment_name:
			#Export params from JSON:
			working_dir 		= config['WORKING_DIR']+experiment_name
			genome_chrome_size 	= config['GENOME_CHROME_SIZE']
			bedtools_exec 		= config['tools']['bedtools']['exec']
			bw_exec 			= config['tools']['bedGraphToBigWig']['exec']
			bed_dir 			= config['BED_OUTPUT_DIR']
			bam_dir 			= config['BAM_OUTPUT_DIR']
			bw_dir 				= config['BIG_WIG_OUTPUT_DIR']
			#End export params from JSON:

			bed_full_path       = os.path.join(working_dir,bed_dir)
			bam_full_path       = os.path.join(working_dir,bam_dir)
			bw_full_path        = os.path.join(working_dir,bw_dir)
			
			create_bed(bam_path=bam_full_path,output=bed_full_path,
							exec_path=bedtools_exec)

			create_bigwig_from_bed(bed_path=bed_full_path,output=bw_full_path,
							exec_path=bw_exec,chrome_size=genome_chrome_size)
		else:
			#check parameters....##future...
			raise Exception("Please provide experiment's name")
	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		os.chdir(currentLocation)
		raise Exception("Error in %s: %s,%s,%s,%s"%(fname,e,exc_type,exc_obj,exc_tb.tb_lineno))


def create_bed(bam_path,output="./bed_files/",exec_path="/usr/bin/bedtools"):
	try:
		#Create if not exist bed directory
		logger.debug("create_bed:START")
		if not (os.path.isdir(output)):
			os.mkdir(output)
		logger.debug("create_bed: changing dir: %s"%bam_path)
		currentLocation = os.getcwd()
		os.chdir(bam_path)

		for sorted_bam in glob.glob("*"):
			logger.debug("Currently processing BAM file: %s"%(sorted_bam))
			cmd=[exec_path,"genomecov","-bg","-ibam",sorted_bam]
			bed_file=os.path.join(output,(sorted_bam+".bed"))
			
			#Create bedGraph file
			with open(bed_file,"w+") as f:
				p = subprocess.Popen(cmd,stdout=f,stderr=subprocess.PIPE)
				output_cmd,err = p.communicate()
				if p.returncode != 0 :
					raise Exception("creating bedGraph file: %s : Error: %s"%(bed_file,err))

		#Go back to parent directory
		logger.debug("create_bed: changing dir: %s"%currentLocation)
		os.chdir(currentLocation)

		logger.debug("create_bed:END")
	except:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		raise Exception("Exception in create_bed: line : %s"%(exc_tb.tb_lineno))

def create_bigwig_from_bed(bed_path,output="./bigwig_files/",
								exec_path="/cs/wetlab/pipeline/bedGraphToBigWig",
										chrome_size="/cs/wetlab/pipeline/SC_GENOME/sacCer3_indexed/genome_chrome_size.txt"):
	try:
		#Create if not exist bed directory
		logger.debug("create_bigwig_from_bed:START")
		if not (os.path.isdir(output)):
			os.mkdir(output)
		logger.debug("create_bigwig_from_bed: changing dir: %s"%bed_path)
		currentLocation = os.getcwd()
		os.chdir(bed_path)

		for bed_file in glob.glob("*"):
			logger.debug("Currently processing bed file: %s"%(bed_file))
			bw_file=os.path.join(output,(bed_file+".bw"))
			cmd=[exec_path,bed_file,chrome_size,bw_file]
			
			#Create bigWig file
			p = subprocess.Popen(cmd,stderr=subprocess.PIPE)
			output_cmd,err = p.communicate()
			if p.returncode != 0 :
				raise Exception("creating bigWig file: %s : Error: %s"%(bw_file,err))

		#Go back to parent directory
		logger.debug("create_bigwig_from_bed: changing dir: %s"%currentLocation)
		os.chdir(currentLocation)

		logger.debug("create_bigwig_from_bed:END")
	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		raise Exception("Exception in create_bigwig_from_bed: line : %s"%(exc_tb.tb_lineno))