import logging
import os

def configure_logging():
    log_file_path = os.path.abspath('logs/ame.log')
    print(f'Logging to {log_file_path}')
    logging.basicConfig(filename=log_file_path, level=logging.INFO)

configure_logging()