""" ... """
import logging
from sensor import SensorX
import json
import os
import time
from requests import Timeout, HTTPError, ConnectionError
import requests


# logging.basicConfig(
#     level=logging.INFO,
#     filename=os.path.join(os.path.sep, os.getcwd(), 'logs', 'meetup.log'),
#     filemode='a',
#     format='%(asctime)s - %(lineno)d - %(message)s')

class Meetup(SensorX):
    __CONFIG_FILE = 'Meetup.json'

    def __init__(self):
        """ read sensor settings from config file """
        super().__init__(os.path.join(os.path.dirname(__file__), self.__class__.__name__))


    def has_updates(self, k):
        """ finding out if there are noew updates """
        n = 0
        content = self.get_all()
        for i in range(len(content)):
            if content[i]['k'] == k:
                n = i +1
                break
        return len(content) if n == 0 else len(content)-n

    def get_content(self, k):
        """ return new events since k """
        content = self.get_all()  # newest last
        n = 0
        for i in range(len(content)):
            if content[i]['k'] == k:
                n = i + 1
                break
        return content if n == 0 else content[n:]

    def get_all(self):
        if self._request_allowed():
            return self._fetch_data()[::-1]
        else:
            return self._read_buffer()[::-1]

    def _fetch_data(self):
        """ json encoded response from webservice .. or none"""
        try:
            response = requests.get(self.props['service_url'] % (self.props['topic_category'], self.props['radius'], self.props['key']),
                                    timeout=self.props['request_timeout'])
            self.props['last_used'] = int(time.time())
            self._save_settings()  # remember time of the last service request
            if response.status_code == 200:
                content = Meetup._create_content(response.json())
                self._write_buffer(content)  # remember last service request(s) results.
            else:
                logging.warning("response: {} {} {}".format(response.status_code, response, response.json()))
                content = []
        except (HTTPError, Timeout, ConnectionError, KeyError, ValueError, TypeError) as e:
            logging.error("except: " + str(e))
            content = []
        return content

    @staticmethod
    def _create_content(text):
        """ convert the json response from the web-service into a list of dictionaries that meets our needs.
        Parse the json content, which can be found in the javascript of the web page."""
        record = []

        for event in text['events']:
            data = {'event name': event['name'], 'date': event['local_date'], 'time': event['local_time'], 'group name': event['group'].get('name'), 'target audience': event['group'].get('who'), 'event link': event['link']}
            record.append(data)
        return record # newest 1st



if __name__ == "__main__":

    json_doc = Meetup().get_all()
    print(json_doc)

