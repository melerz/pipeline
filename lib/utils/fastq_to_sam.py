# import json
# import subprocess
# import os
# import glob
# import sys
# import logging
# import re

from .. import *

logger = logging.getLogger("__main__")

def run(experiment_name):
	try:
		currentLocation=os.getcwd()
		logger.info("Alignment process....")
		print "Running bowtie..."

		#Export params from JSON:
		fastq_dir = config['WORKING_DIR']+experiment_name
		bowtie_dir = config['BOWTIE_OUTPUT_DIR']
		bowtie_dir = config['BOWTIE_OUTPUT_DIR']
		bowtie_exec = config['tools']['bowtie']['exec']
		genome = config['GENOME']
		#End xport params from JSON

		#Check if the experiment is double read or not
		paired = is_paired(fastq_dir)

		#Create the bowtie files
		create_bowtie(path=fastq_dir,genome=genome,bowtie_exec=bowtie_exec,
						bowtie_dir=bowtie_dir,paired=paired)

		full_bowtie_dir=os.path.join(fastq_dir,bowtie_dir)

		#Unite L1/2/3/4 bowtie files into one file
		unite_bowtie(path=full_bowtie_dir)

	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		os.chdir(currentLocation)
		raise Exception("Error in %s: %s,%s,%s,%s"%(fname,e,exc_type,exc_obj,exc_tb.tb_lineno))



def is_paired(fastq_dir):
	'''
		This helper function determines if the current experiment is paired-read
		or not. It does so by examine the json configuration data
	'''
	try:
		logger.debug("is_paired: START")
		if glob.glob("*_R2_*"):
			return True
		else:
			return False
	except Exception, e:
		raise Exception("Error in is_paired: %s",e)

def create_bowtie(paired,genome,path=".",bowtie_exec="/cs/wetlab/pipeline/bwt2/bowtie2",bowtie_dir="bowtie_files/"):
	'''
		This helper function create bowtie files
	'''
	try:
		logger.debug("create_bowtie: START")
		currentLocation = os.getcwd()
		logger.debug("create_bowtie: changing dir: %s"%path)
		os.chdir(path)
		#Create bowtie dir
		logger.info("current directory:%s"%(os.getcwd()))
		if not (os.path.isdir(bowtie_dir)):
			os.mkdir(bowtie_dir)

		#Get all *R1* fastq files in directory, exclude 'Undetermined' files
		fastq_r1_files = [fastq_file for fastq_file in 
							glob.glob('*R1*.fastq.gz') if not re.match("Undetermined",fastq_file)]
		for fastq_r1_file in fastq_r1_files:
			#Create seperate sam file for each fastq file
			sam_file = bowtie_dir + (fastq_r1_file.split("_R1")[0]+".bwt")

			if paired:
				#find his pair
				fastq_r2_file = fastq_r1_file.replace("R1","R2")
				cmd = [bowtie_exec,"-p","16","-x",
							genome,"-1",fastq_r1_file,"-2",fastq_r2_file,
								"-S",sam_file
						]
				logger.debug("Processing paired files:%s,%s"%(fastq_r1_file,fastq_r2_file))
			else:
				cmd = [bowtie_exec,"-p","16","-x",
							genome,"-U",fastq_r1_file,"-S",sam_file
						]
				logger.debug("Processing unpaired file:%s"%(fastq_r1_file))

			p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			output_cmd,err = p.communicate() #Blocking...
			if p.returncode != 0:
				raise Exception("Error in running bowtie tool for: %s : %s"%(fastq_r1_file,output_cmd))

			#Handling output.
			#1) Output relevant lines to the user
			#2) Save the output in a unified files
			print "Alignment rate: %s : %s"%(sam_file,output_cmd)
			with open("bowtie_stats.txt","a+") as f:
				f.write("---------")
				f.write(sam_file)
				f.write(output_cmd)

		logger.debug("create_bowtie: changing dir: %s"%currentLocation)
		os.chdir(currentLocation)
		logger.debug("create_bowtie: END")
	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		raise Exception("Error in create_bowtie function: Message: %s : Type: %s : Object: %s : Line: %s"%(e,
																				exc_type,exc_obj,exc_tb.tb_lineno))


def unite_bowtie(path="."):
	'''
		This helper function merge the lanes bowtie files for each sample
	'''
	try:
		logger.debug("unite_bowtie: START")
		currentLocation = os.getcwd()
		logger.debug("unite_bowtie: changing dir: %s"%path)
		os.chdir(path)
		#Trim trailing slash in path
		if path[-1:] == "/":
			path = path[:-1]
		#Get all unique samples with the format aaa_bbb_L00X.bwt.
		#We will create a unique bowtie file with only aaa_bbb prefix.
		unique_samples = set(['_'.join(bwt_file.split("_")[:2]) for bwt_file in glob.glob("*_*_*")])
		for unique_sample in unique_samples:
			logger.debug("Found unique sample: %s"%unique_sample)
			lanes_samples_files = glob.glob("%s*"%unique_sample)
			with open(unique_sample+".bwt","a+") as sam_united_file:
				#Get content of each bowtie file and append it to the unified file
				#We want to put the content in order, first lane first
				#Also, we want to avoid multipile headers when we are processing
				#from the 2nd lane. For samtools to read the sam file, only the first header
				#is important
				for lane in ['L001','L002','L003','L004']:
					for lane_sample_file in lanes_samples_files:
						if re.search("%s"%lane,lane_sample_file):
							logger.debug("Processing lane file: %s"%lane_sample_file)
							with open(lane_sample_file,"r") as f:
								if lane != 'L001':
									for line in f:
										if "@" not in line: #like grep -v '@'
											sam_united_file.write(line)
								else:
									sam_united_file.write(f.read())
							#Remove the single bowtie file
							os.remove(lane_sample_file)
		logger.debug("unite_bowtie: changing dir: %s"%currentLocation)
		os.chdir(currentLocation)
		logger.debug("unite_bowtie: END")
	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		raise Exception("Error in unite_bowtie function: Message: %s : Type: %s : Object: %s : Line: %s"%(e,
																				exc_type,exc_obj,exc_tb.tb_lineno))





