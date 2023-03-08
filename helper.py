#!/usr/bin/env python
import logging
import sys
from blackduck.HubRestApi import HubInstance

logging.basicConfig(format='%(threadName)s:%(asctime)s:%(levelname)s:%(message)s', stream=sys.stderr,
                    level=logging.INFO)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("blackduck").setLevel(logging.DEBUG)


# Extend the hub class and override the constructor to take hub url, api token and insecure flag from the command line.
class MyHub(HubInstance):

    def __init__(self, *args, **kwargs):
        kwargs.update({"api_token": args[1]})
        kwargs.update({"insecure": args[2]})
        super().__init__(*args, **kwargs)