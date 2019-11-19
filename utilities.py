import json
from pathlib  import Path
import selenium
from selenium import webdriver

################################################################################
#
# Part 0: Exception Handling
#
################################################################################

class FileNotFound(BaseException):
    pass

class CorruptConfiguration(BaseException):
    pass

# Return a thing pretending to be a browser
#  for purposes of failure to open a browser.
#  capable being returned into a with/as statement
class NotABrowser():
    def __bool__(self):
        return False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

################################################################################
#
# Part 1: Utilities to load the configuration file
#
################################################################################

def load_config(file_name = 'config.json', require_chrome = False):
    '''
    Load the configuration file

    The configuration file should be a json file.

    Parameters:
     - file_name (str): the path to the configuration file.
                        Default 'config.json'

     - require_chrome (bool): whether to check that there is a path to
                              chromedriver
                              Default False

    Returns:
     - a dictionary with configuration info

    Raises:
     - FileNotFound if no config file is found
     - CorruptConfiguration if there are missing fields or loading fails
    '''

    file_exists = Path(file_name).exists()
    if not file_exists:
        raise FileNotFound('Unable to find a configuration file')

    try:
        with open(file_name, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise FileNotFound('Corrupted configuration file') from e

    if 'api_key' not in config:
       raise CorruptConfiguration('Missing api_key')

    if 'spreadsheet_id' not in config and 'medium_urls' not in config:
        raise CorruptConfiguration('Missing URL list resource')

    if require_chrome and 'chromedriver_location' not in config:
        raise CorruptConfiguration('Missing path to chrome driver')

    return config

def write_config(data, file_name = 'config.json'):
    with open(file_name, 'w') as f:
        json.dump(data, f)


################################################################################
#
# Part 2: Get a selenium web browser
#
################################################################################

# Exported for use in setup
profile_path = Path.cwd()/Path('./chromedriver-profile/')

def get_browser(config = None):
    '''
    Get a selenium broswer instance

    Open a chromerdriver browser based on a config dictionary (defualts to
    loading config.json). Checks whether the user has profiles enabled and opens
    an (essentially) incognito instance if not. No return if the profile is
    already in use by another chromedriver instance.

    Paramters
     - config : dictionary with a path to the browser and preference on having
                a user profile. Default: None. On default, loads config.json

    Returns:
     - a selenium browser instance on success; otherwise print a harmless
     error message and return nothing
    '''
    if not config:
        config = load_config(require_chrome = True)

    if 'have_profile' not in config:
        print('No configuration for user profiles is set. '
              'Enabling by default. '
              'You can update this using the setup file.')
        use_profile = True

    else:
        use_profile = config['have_profile']

    options = webdriver.ChromeOptions()
    if use_profile:
        options.add_argument(f'user-data-dir={profile_path}')

    chromedriver_path = config['chromedriver_location']
    try:
        browser = webdriver.Chrome(executable_path=chromedriver_path,
                                   options = options)
    except selenium.common.exceptions.InvalidArgumentException:
        print('The user profile is already in use. '
              'Please quit any existing chromedriver instances. '
              'Please note that closing the windows is not sufficient')
        return NotABrowser()
    else:
        return browser
