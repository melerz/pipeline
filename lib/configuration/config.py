'''
This module loads the configuration file
'''

from .. import *
from os.path import expanduser
import inspect, os
import getpass
import time

CONFIG_NAME="config.json"

current_file_path	=	inspect.getfile(inspect.currentframe())
current_dir_path 	= 	os.path.dirname(current_file_path)
configuration_path 	= 	os.path.join(current_dir_path,CONFIG_NAME)
config=json.load(open(configuration_path))

def get_working_directory(name):
	'''
		Creates the experiment directory in a sub-directory within the www folder in the user profile
	'''
	www_path = expanduser("~/www")
	experiment_dir = os.path.join(www_path,name)
	
	if not os.path.isdir(experiment_dir):
		print "Creating the experiment directory in: %s"%(experiment_dir)
		username = getpass.getuser()
		current_datetime = time.strftime("%d-%m-%y-%H-%M")
		#Creating relevant experiment dir in working directory
		working_directory = config['WORKING_DIR']
		experiment_wd_dir = os.path.join(working_directory,username+"-"+current_datetime+"-"+name)

		os.mkdir(experiment_wd_dir)

		#Set Mode
		current_perm=os.stat(experiment_wd_dir)
		os.chmod(experiment_wd_dir,current_perm.st_mode|stat.S_IXOTH|stat.S_IXGRP) #o+x
		htaccess_file = open(experiment_wd_dir+'/.htaccess',"w+")
		htaccess_file.write("Options +Indexes")

		#Creating a linked directory inside the ~/www, to the working directory

		#Create www folder if doesn't exist
		if not os.path.isdir(www_path):
			os.mkdir(www_path)

		#Create the experiment folder inside the www folder
		os.symlink(experiment_wd_dir,experiment_dir)

	return experiment_dir