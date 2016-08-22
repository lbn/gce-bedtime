from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

import json
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
ZONE = os.getenv("GCP_ZONE")

def saver(instance):
    items = instance["metadata"]["items"]
    meta = {item["key"]: item["value"] for item in items}
    return "saver" in meta and meta["saver"] == "true"

def running(instance):
    return instance["status"] == "RUNNING"

def stopped(instance):
    return instance["status"] == "TERMINATED"

class Saver(object):
    def __init__(self):
        credentials = GoogleCredentials.get_application_default()
        self.compute = discovery.build("compute", "v1", credentials=credentials)

    def running_savers(self):
        result = self.compute.instances().list(project=PROJECT_ID, zone=ZONE).execute()
        return [inst for inst in result["items"]
                if saver(inst) and running(inst)]

    def stopped_savers(self):
        result = self.compute.instances().list(project=PROJECT_ID, zone=ZONE).execute()
        return [inst for inst in result["items"]
                if saver(inst) and stopped(inst)]

    def instance_off(self, instance):
        result = self.compute.instances().stop(project=PROJECT_ID, zone=ZONE,
                                        instance=instance["name"]).execute()
        print(json.dumps(result))

    def instance_on(self, instance):
        result = self.compute.instances().start(project=PROJECT_ID, zone=ZONE,
                                        instance=instance["name"]).execute()
        print(json.dumps(result))

    def turn_off_all(self):
        instances = self.running_savers()
        print("Turning off these instances:")
        print([inst["name"] for inst in instances])
        for inst in instances:
            self.instance_off(inst)

    def turn_on_all(self):
        instances = self.stopped_savers()
        print("Turning on these instances:")
        print([inst["name"] for inst in instances])
        for inst in instances:
            self.instance_on(inst)
