'''
This module loads the configuration file
'''

from .. import *
import inspect, os

CONFIG_NAME="config.json"

current_file_path=inspect.getfile(inspect.currentframe())
current_dir_path = os.path.dirname(current_file_path)
configuration_path = os.path.join(current_dir_path,CONFIG_NAME)
config=json.load(open(configuration_path))

def get_working_directory(name):
	'''
		Creates the experiment directory in a sub-directory within the www folder in the user profile
	'''
	www_path = expanduser("~/www")
	experiment_dir = os.path.join(www_path,name)
	
	if not os.path.isdir(experiment_dir):
		print "Creating the experiment directory in: %s"%(experiment_dir)
		#Creating relevant experiment dir in working directory
		working_directory = config['WORKING_DIR']
		experiment_wd_dir = os.path.join(working_directory,name)
		os.path.mkdir(experiment_wd_dir)

		#Creating a linked directory inside the ~/www, to the working directory

		#Create www folder if doesn't exist
		if not os.path.isdir(www_path):
			os.path.mkdir(www_path)

		#Create the experiment folder inside the www folder
		os.symlink(experiment_wd_dir,experiment_dir)
	return experiment_dir