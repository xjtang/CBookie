""" Module for logging
"""
import logging


log_format = '|%(asctime)s|%(levelname)s|%(module)s|%(lineno)s||%(message)s'
log_formatter = logging.Formatter(log_format,'%Y-%m-%d %H:%M:%S')
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

log = logging.getLogger('pyshell')
log.addHandler(log_handler)
log.setLevel(logging.INFO)
