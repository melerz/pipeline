import json
import subprocess
import os
import glob
import logging
logger = logging.getLogger(__name__)
def run(config_file="./config.json"):
	try:
		currentLocation=os.getcwd()
		logger.info("Alignmenet process....")
		config = json.load(open(config_file))
		logger.info("Loading Config files...")
		fastq_dir = config['settings']['WORKING_DIR']+config['data']['url']
		bowtie_dir = config['settings']['BOWTIE_OUTPUT_DIR']
		bowtie_exec = config['settings']['tools']['bowtie']['exec']
		genome = config['settings']['GENOME']
		#Enter working dir (fastq files)
		os.chdir(fastq_dir)
		#Create bowtie dir
		if not (os.path.isdir(bowtie_dir)):
			os.mkdir(dir_name)

		#Get all *R1* fastq files in directory
		fastq_r1_files = glob.glob('*R1*.fastq.gz')
		#check if paired
		if is_paired(config['data']['configuration']):
			logger.info("Paired reads")
			for fastq_r1_file in fastq_r1_files:
				#find his pair
				fastq_r2_file = fastq_r1_file.replace("R1","R2")
				sam_file = bowtie_dir + fastq_r1_file
				metrics_file = bowtie_dir + "metrics.met"
				p = subprocess.Popen(
							["bowtie_exec","-p","16","-x",
								genome,"-1",fastq_r1_file,"-2",fastq_r2_file,
									"-S",sam_file,"--met-file",metrics_file
							])
		else:
			logger.info("Unpaired reads")
			for fastq_r1_file in fastq_r1_files:
				sam_file = bowtie_dir + fastq_r1_file
				metrics_file = bowtie_dir + "metrics.met"
				p = subprocess.Popen(
							["bowtie_exec","-p","16","-x",
								genome,"-U",fastq_r1_file,"-S",sam_file,
								"--met-file",metrics_file
							])				
		os.chdir(currentLocation)

	except Exception, e:
		raise Exception("Error in fastq_to_sam: %s",e)



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
