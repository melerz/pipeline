import json
import subprocess
import os
import glob
import sys
import logging
logger = logging.getLogger("__main__")
def run(config_file="./config.json"):
	try:
		currentLocation=os.getcwd()
		logger.info("Alignmenet process....")
		config = json.load(open(config_file))
		logger.info("Loading Config files...")
		fastq_dir = config['settings']['WORKING_DIR']+config['data']['url']
		logger.info(fastq_dir)
		bowtie_dir = config['settings']['BOWTIE_OUTPUT_DIR']
		bowtie_exec = config['settings']['tools']['bowtie']['exec']
		genome = config['settings']['GENOME']
		#Enter working dir (fastq files)
		os.chdir(fastq_dir)
		#Create bowtie dir
		logger.info("current directory:%s"%(os.getcwd()))
		if not (os.path.isdir(bowtie_dir)):
			os.mkdir(bowtie_dir)

		#Get all *R1* fastq files in directory
		fastq_r1_files = glob.glob('*R1*.fastq.gz')
		#check if paired
		paired = is_paired(config['data']['configuration'])
		#Create bowtie file for each fastq file
		for fastq_r1_file in fastq_r1_files:
			#Create seperate sam file for each fastq file
			sam_file = bowtie_dir + (fastq_r1_file.split("_R1")[0]+".bwt")
			#Create unified (?) metrics file
			metrics_file = bowtie_dir + "metrics.met"
			if paired:
				#find his pair
				fastq_r2_file = fastq_r1_file.replace("R1","R2")
				cmd = [bowtie_exec,"-p","16","-x",
							genome,"-1",fastq_r1_file,"-2",fastq_r2_file,
								"-S",sam_file,"--met-file",metrics_file
						]
			else:
				cmd = [bowtie_exec,"-p","16","-x",
							genome,"-U",fastq_r1_file,"-S",sam_file,
							"--met-file",metrics_file
						]
			p = subprocess.Popen(cmd,stdout.subprocess.PIPE,stderr=subprocess.PIPE)
			output,err = subprocess.communicate() #Blocking...
			if err:
				logger.error("Error in creating bowtie file for fastq file:%s"%err)
		os.chdir(currentLocation)

	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		os.chdir(currentLocation)
		raise Exception("Error in fastq_to_sam: %s,%s,%s,%s"%(e,exc_type,exc_obj,fname))



def is_paired(experiment_configuration):
	'''
		This helper function determines if the current experiment is paired-read
		or not. It does so by examine the json configuration data
	'''
	try:
		count=0
		for val in experiment_configuration.values():
			if val['IsIndexedRead']=='Y':
				count+=1

		return count==2
	except Exception, e:
		raise Exception("Error in fastq_to_sam: %s",e)
