# Python imports
import sys
import logging

def log(msg, severity=logging.DEBUG, detail='', error=None):
    if isinstance(msg, unicode):
        msg = msg.encode(sys.getdefaultencoding(), 'replace')
    if isinstance(detail, unicode):
        detail = detail.encode(sys.getdefaultencoding(), 'replace')
    logger.log(severity, '%s \n%s', msg, detail)
