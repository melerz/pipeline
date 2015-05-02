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
		logger.info("Alignment process....")
		print "Running bowtie..."
		config = json.load(open(config_file))
		logger.info("Loading Config files...")
		fastq_dir = config['settings']['WORKING_DIR']+config['data']['url']
		logger.info(fastq_dir)
		bowtie_dir = config['settings']['BOWTIE_OUTPUT_DIR']
		bowtie_exec = config['settings']['tools']['bowtie']['exec']
		genome = config['settings']['GENOME']

		#Check if the experiment is double read or not
		paired = is_paired(config['data']['configuration'])

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
		raise Exception("Error in fastq_to_sam: %s,%s,%s,%s"%(e,exc_type,exc_obj,fname))



def is_paired(experiment_configuration):
	'''
		This helper function determines if the current experiment is paired-read
		or not. It does so by examine the json configuration data
	'''
	try:
		logger.debug("is_paired: START")
		count=0
		for val in experiment_configuration.values():
			if val['IsIndexedRead']=='Y':
				count+=1
		logger.debug("is_paired: END")
		return count==2
	except Exception, e:
		raise Exception("Error in fastq_to_sam: %s",e)

def create_bowtie(paired,genome,path=".",bowtie_exec="/cs/wetlab/pipeline/bwt2/bowtie2",bowtie_dir="bowtie_files/"):
	'''
		This helper function create bowtie files
	'''
	logger.debug("create_bowtie: START")
	currentLocation = os.getcwd()
	logger.debug("create_bowtie: changing dir: %s"%path)
	os.chdir(path)
	#Create bowtie dir
	logger.info("current directory:%s"%(os.getcwd()))
	if not (os.path.isdir(bowtie_dir)):
		os.mkdir(bowtie_dir)

	#Get all *R1* fastq files in directory
	fastq_r1_files = glob.glob('*R1*.fastq.gz')

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
			logger.debug("Processing paired files:%s,%s"%(fastq_r1_file,fastq_r2_file))
		else:
			cmd = [bowtie_exec,"-p","16","-x",
						genome,"-U",fastq_r1_file,"-S",sam_file,
						"--met-file",metrics_file
					]
			logger.debug("Processing unpaired file:%s"%(fastq_r1_file))

		p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		output,err = p.communicate() #Blocking...
		if err:
		# 	#logger.error("Error in creating bowtie file for fastq file:%s"%err)
			print output,err
	logger.debug("create_bowtie: changing dir: %s"%currentLocation)
	os.chdir(currentLocation)
	logger.debug("create_bowtie: END")

def unite_bowtie(path="."):
	'''
		This helper function merge the lanes bowtie files for each sample
	'''
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
			for lane in ['001','002','003','004']:
				for lane_sample_file in lanes_samples_files:
					if re.match("(\w+_%s)"%lane,lane_sample_file):
						logger.debug("Processing lane file: %s"%lane_sample_file)
						with open(lane_sample_file,"r") as f:
							if lane != '001':
								for line in f:
									if "@" not in line:
										sam_united_file.write(line)
							else:
								sam_united_file.write(f.read())
						#Remove the single bowtie file
						os.remove(lane_sample_file)
	logger.debug("unite_bowtie: changing dir: %s"%currentLocation)
	os.chdir(currentLocation)
	logger.debug("unite_bowtie: END")





