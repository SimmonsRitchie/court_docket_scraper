import logging
import logging.config
import os
import pathlib
import yaml
from locations import dirs, paths

def logs_config(
    default_path=paths['logs_config'],
    default_level=logging.INFO,
    env_key='LOG_CFG'
):

    # set log output directory
    log_output = dirs["logs"]

    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)  # if file path is set using LOG_CFG env, use this
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())  # convert yaml to dict
            # we get the path in config file then append it to our log directory
            for handler in config['handlers']:
                if 'FileHandler' in config['handlers'][handler]['class']:
                    config['handlers'][handler]['filename'] = log_output / config['handlers'][handler]['filename']
                    config['handlers'][handler]['filename'].parent.mkdir(exist_ok=True, parents=True) # create parent
                    # directories of path if they don't exist
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)