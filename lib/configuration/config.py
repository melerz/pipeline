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
