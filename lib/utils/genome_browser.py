# import json
# import subprocess
# import os
# import glob
# import sys
# import logging
# import re
# import datetime
# import shutil
# import stat
from .. import *
logger = logging.getLogger("__main__")
'''
	This module creates an hub folder for UCSC Genome Browser.
	The module is currently working only on bigWig files for now
'''

def run(experiment_name,**kwargs):
	try:
		currentLocation=os.getcwd()
		logger.info("Running genome_browser")
		print "Genome Browser: Creating hub directory"
		if experiment_name:
			#Export params from JSON:
			working_dir 		= get_working_directory(experiment_name)
			bw_dir 				= config['BIG_WIG_OUTPUT_DIR']
			hub_dir				= config['HUB_OUTPUT_DIR']
			trackdb_format		= config['trackdb']
			base_url 			= config['PUBLIC_WEBSITE']
			#End export params from JSON:

			bw_full_path        = os.path.join(working_dir,bw_dir)
			hub_full_path       = os.path.join(working_dir,hub_dir)

			create_hub_dir(experiment_name=experiment_name,trackdb_format=trackdb_format,
							hub_dir=hub_full_path,bigwig_dir = bw_full_path)

			url = base_url+experiment_name+"/"+hub_dir
			print url
		else:
			#check parameters....##future...
			raise Exception("Please provide experiment's name")
	except Exception, e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		os.chdir(currentLocation)
		raise Exception("Error in %s: %s,%s,%s,%s"%(fname,e,exc_type,exc_obj,exc_tb.tb_lineno))


def create_hub_dir(experiment_name,trackdb_format,hub_dir="./hub",bigwig_dir="./bw_files"):
	try:
		currentLocation = os.getcwd()
		#Create hub directory if doesnt exist
		logger.debug("create_hub_dir:START")
		if not (os.path.isdir(hub_dir)):
			os.mkdir(hub_dir)
			current_perm=os.stat(hub_dir)
			os.chmod(hub_dir,current_perm.st_mode|stat.S_IXOTH)
		else:
			raise Exception("There is alreay hub folder in this directory")
		if not os.path.isdir(bigwig_dir):
			raise Exception("%s doesn't exist"%(bigwig_dir))

		logger.debug("create_hub_dir: changing dir: %s"%hub_dir)
		os.chdir(hub_dir)

		date_str=datetime.date.today().strftime("%d/%m")
		#Create hub.txt file
		logger.debug("Creating hub file")
		with open("hub.txt","w+") as hub_file:	
			hub_file.write("hub %s\n"%(experiment_name))
			hub_file.write("shortLabel %s %s experiment\n"%(experiment_name,date_str))
			hub_file.write("longLabel %s %s experiment\n"%(experiment_name,date_str))
			hub_file.write("genomesFile genomes.txt\n")
			hub_file.write("email nflab@mail.huji.ac.il\n")

		#Create genomes.txt file
		logger.debug("Creating genomes.txt file")
		with open("genomes.txt","w+") as genomes_file:
			genomes_file.write("genome sacCer3\n") 
			genomes_file.write("trackDb sacCer3/trackDb.txt\n")

		#Create sacCer3 directory, with the bigWig files from the original bigWig folder
		#One may think we could link the new sacCer3 directory to the relevant files, however,
		#we need to allow FollowSymLink in the .htaccess file - but we can't (error 500), probably
		#because this setting can't be overidden (by httpd.conf file)
		logger.debug("Creating sacCer3 folder")
		shutil.copytree(bigwig_dir,"sacCer3")
		current_perm=os.stat("sacCer3")
		os.chmod("sacCer3",current_perm.st_mode|stat.S_IXOTH)

		#Create trackDb.txt file in the bigWig folder
		logger.debug("Creating tackDb.txt file")	
		create_trackdb(format=trackdb_format,path="sacCer3",name="trackDb.txt")

		#Go back to parent directory
		logger.debug("create_hub_dir: changing dir: %s"%currentLocation)
		os.chdir(currentLocation)

		logger.debug("create_hub_dir:END")
	except Exception,e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		raise Exception("Exception in create_hub_dir: type: %s : line : %s"%(exc_type,exc_tb.tb_lineno))

def create_trackdb(format,path="./",name="trackDb.txt"):
	#full_path=os.path.join(path,name)
	try:
		currentLocation = os.getcwd()
		os.chdir(path)
		bigwig_files = glob.glob("*")
		with open(name,"w+") as trackdb_file:
			for bigwig_file in bigwig_files:
				format['track']=bigwig_file
				format['shortLabel']=bigwig_file
				format['longLabel']=bigwig_file
				format['bigDataUrl']=bigwig_file
				for key,value in format.iteritems():
					trackdb_file.write("%s %s\n"%(key,value))
				trackdb_file.write("\n")
	except Exception,e:
		exc_type,exc_obj,exc_tb = sys.exc_info()
		raise Exception("Exception in create_trackdb: type: %s : line : %s"%(exc_type,exc_tb.tb_lineno))
