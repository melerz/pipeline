'''
	This module provides the following:
		1) Loads the configuration file - config.json
		2) Initialize global functions for the pipeline scripts
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

#www_path = expanduser("~/www")

SAMPLE_DIR_FORMAT="sample-"

def create_dir(path,force=False):
	#Check if dir is already exist
	if os.path.isdir(path):
		print "create dir currently deletes the folder: %s"%path
		#Check if force was specified
		if not force:
			raise Exception("Directory %s in %s is already exist! exiting now..."%(path,os.getcwd()))
		#force was specified. Delete the dir
		else:
			shutil.rmtree(path,ignore_errors=True)		
	os.mkdir(path)
	current_perm=os.stat(path)
	os.chmod(path,current_perm.st_mode|stat.S_IXOTH|stat.S_IXGRP)

def build_profile_dir_path(name):
	'''
		Builds the experiment folder *path* inside the ~/www folder of the current user.
		This function is an helper function to get_working_directory function

		Args:
			- name: The experiment name
		Returns:
			The path for the main experiment dir
	'''

	www_path = expanduser("~/www")
	experiment_dir = os.path.join(www_path,name)
	return experiment_dir	

def build_cs_dir_path(name):
	'''
		Builds the experiment folder *path* inside the WORKING_DIR config setting.
		The folder from (build_profile_dir_path) is linked to this folder.
		In this way, we avoid quota issues.
		This function is an helper function to get_working_directory function

		Args:
			- name: The experiment name
		Returns:
			The path for the experiment dir inside the WORKING_DIR config setting
	'''
	username = getpass.getuser()
	working_directory = config['WORKING_DIR']
	experiment_wd_dir = os.path.join(working_directory,username+"-"+name)
	return experiment_wd_dir

def build_sample_dir_path(sample_name):
	'''
		Builds the sample dir inside the experiment dir.
		This function is an helper function to get_working_directory function.

		Args:
			- sample_name: The current sample name of the pipeline
		Returns:
			The path for the current sample name
	'''
	path=SAMPLE_DIR_FORMAT+sample_name
	return path


def get_sample_dir(sample_name,force=False):
	'''
		Creates/Gets a sub-folder inside the working dir by the name of the
		current sample name that is processed by the pipeline
		Args:
			- sample_name (str): The sample name
			- working_dir (str): A path to a fastq folder
		Returns:
			The full path of the sample dir
	'''
	sample_dir_name = build_sample_dir_path(sample_name)
	sample_dir=os.path.join(os.getcwd(),sample_dir_name)
	create_dir(sample_dir,force)
	return sample_dir

def get_working_directory(name,**kwrags):
	'''
		Creates/Gets the experiment directory in a sub-directory within the www folder in the user profile.
		If sample_name is specified, than it creates/gets a sub-folder inside the experiment directory by the name of the
		current sample name that is processed by the pipeline
		Args:
			- name (str): The experiment name
			- sample_name (str) : The sample name

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
		if not os.path.isdir(os.path.dirname(experiment_dir)):
			os.mkdir(os.path.dirname(experiment_dir))

		#Create the experiment folder inside the www folder
		os.symlink(experiment_wd_dir,experiment_dir)

	#If sample_name is not specified, return the experiment dir path only	
	return experiment_dir

def get_samples(name):
	'''
		Args:
			- name - The experiment name
		Returns:
			Returns a list of all the sample dirs inside the experiment folder
	'''
	working_directory = get_working_directory(name)
	sample_dirs = glob.glob(working_directory+"/"+SAMPLE_DIR_FORMAT+"*")
	return sample_dirs