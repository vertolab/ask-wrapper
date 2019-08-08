import json
import logging


def debug(msg, **kwargs):
    content = {'msg': msg}
    if kwargs:
        content['kwargs'] = kwargs
    jsoned = json.dumps(content, indent=None)

    logging.debug(jsoned)
