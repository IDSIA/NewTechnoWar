"""
Adapted from: https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19
"""
import os
import yaml
import logging.config
import logging


def setup_logging(default_path='logger.config.yaml', default_level=logging.INFO, env_key='LOG_CONFIG'):
    os.makedirs("logs", exist_ok=True)
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print('Failed to load configuration file. Using default configs')
