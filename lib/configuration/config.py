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

SAMPLE_DIR_FORMAT="sample-"

def build_profile_dir_path(name):
	www_path = expanduser("~/www")
	#experiment_dir = os.path.join(www_path,name)
	experiment_dir="/cs/wetlab/melerz/website/60-maayan/"
	return experiment_dir	

def build_cs_dir_path(name):
	username = getpass.getuser()
	current_datetime = time.strftime("%d-%m-%y-%H-%M")
	#Creating relevant experiment dir in working directory
	working_directory = config['WORKING_DIR']
	experiment_wd_dir = os.path.join(working_directory,username+"-"+current_datetime+"-"+name)
	return experiment_wd_dir

def build_sample_dir_path(sample_name):
	path=SAMPLE_DIR_FORMAT+sample_name
	return path

def get_working_directory(name,sample_name=None):
	'''
		Creates/Gets the experiment directory in a sub-directory within the www folder in the user profile.
		If sample_name is specified, than it creates/gets a sub-folder inside the experiment directory by the name of the
		current sample name that is processed by the pipeline
		Args:
			- name: The experiment name
			- sample_name: The sample name

		Return:
			The full path to the experiment dir / sample dir inside the user profile
	'''
	experiment_dir=build_profile_dir_path(name)
	if not os.path.isdir(experiment_dir):
		experiment_wd_dir = build_cs_dir_path(name)

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

	if sample_name:
		sample_dir_name = build_sample_dir_path(sample_name)
		sample_dir=os.path.join(experiment_dir,sample_dir_name)
		if not os.path.isdir(sample_dir):
			print "Creating sample dir of sample: {sample} of the experiment: {experiment}".format(sample=sample_name,experiment=name)
			os.mkdir(sample_dir)
		return sample_dir

	#If sample_name is not specified, return the experiment dir path only	
	return experiment_dir


def get_samples(name):
	working_directory = get_working_directory(name)
	sample_dirs = glob.glob(working_directory+"/"+SAMPLE_DIR_FORMAT+"*")
	return sample_dirs