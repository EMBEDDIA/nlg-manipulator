from collections import OrderedDict
import json
import pandas as pd
from pyjstat import pyjstat
from tabulate import tabulate
from urllib.request import Request
from urllib import request


class StatfiReaderService(object):

    def __init__(self):
        self._reader = Importer()

    def fetch(self, *args, **kwargs):
        return self._reader.load_pretty(*args, **kwargs)


class Importer(object):

    def _get_based_url(self, language, agency):
        base_urls = {
            "tilastokeskus": {
                "en": "http://pxnet2.stat.fi/PXWeb/api/v1/en/StatFin/",
                "fi": "http://pxnet2.stat.fi/PXWeb/api/v1/fi/StatFin/"
            },
            "scb": {
                "en": "http://api.scb.se/OV0104/v1/doris/en/ssd/"
            }
        }

        if not agency in base_urls:
            raise Exception("Invalid agency")
        if not language in base_urls[agency]:
            raise Exception("Invalid language")
        return base_urls[agency][language]


    def describe(self, *path, language="en", agency="tilastokeskus"):
        url = self._get_based_url(language, agency) + "/".join(path)
        req = Request(url, method="GET")
        with request.urlopen(req) as response:
            return response.read().decode('utf-8')


    def load(self, *path, query=None, language="en", agency="tilastokeskus"):
        if query is None:
            query = []
        url = self._get_based_url(language, agency) + "/".join(path)
        payload = '{"query": ' + json.dumps(query) + ',"response":{"format":"json-stat"}}'
        payload = payload.encode('utf-8')
        req = Request(url, payload, method="POST")
        with request.urlopen(req) as response:
            response_as_str = response.read().decode('utf-8')
            response_as_json = json.loads(response_as_str, object_pairs_hook=OrderedDict)
            dataframe = pyjstat.from_json_stat(response_as_json)
            return dataframe


    def describe_pretty(self, *path, language="en", agency="tilastokeskus", as_json=False):
        url = ""
        for path_element in path:
            options = self.describe(url, language=language)
            options = json.loads(options)
            options = [o for o in options if o['text'] == path_element]
            if len(options) == 1:
                if url:
                    url += "/"
                url += options[0]['id']
        description = self.describe(url, language=language, agency=agency)
        description = json.loads(description)

        if as_json:
            return description

        if isinstance(description, dict):
            output = description["title"] + ":\n"
            variables = description["variables"]
        elif isinstance(description, list):
            output = "UNTITLED RESPONSE:\n"
            variables = description
        else:
            raise Exception("Unable to parse response from server:", type(description))
        for variable in variables:
            output += "\t{}\n".format(variable["text"])
            if "valueTexts" in variable:
                output += "\t\tValues:\n"
                for value in variable["valueTexts"]:
                    output += "\t\t\t{}\n".format(value)
            for feature in variable:
                if feature not in ["id", "text", "values", "valueTexts", "code"]:
                    output += "\t\t{}: {}\n".format(feature, variable[feature])
        return output


    def load_pretty(self, *path, filters=None, language="en", agency="tilastokeskus"):
        if filters is None:
            filters = {}
        url = ""
        for path_element in path:
            options = self.describe(url, language=language, agency=agency)
            options = json.loads(options)
            options = [o for o in options if o['text'] == path_element]
            if len(options) == 1:
                if url:
                    url += "/"
                url += options[0]['id']

        description = self.describe(url, language=language, agency=agency)
        description = json.loads(description)

        query = []
        for variable in description["variables"]:
            if variable["text"] in filters:
                this_filter = filters[variable["text"]]
                this_filter = [str(item) for item in this_filter]
                values = []
                for idx, value in enumerate(variable["valueTexts"]):
                    if value in this_filter:
                        code = variable["values"][idx]
                        values.append(str(code))
                query.append(
                    {
                        "code": variable["code"],
                        "selection": {
                            "filter": "item",
                            "values": values
                        }
                    })

        return self.load(url, query=query, language=language, agency=agency)[0]


if __name__ == "__main__":
    reader = Importer()
    data = reader.load_pretty(
        "Elections",
        "Municipal elections",
        "5. Municipal elections 2012 - election results, voting",
        "5.2. Municipal elections 2012, support for parties",
        filters={
            "District": ["091 Helsinki"],
        }
    )
    print(tabulate(data, tablefmt='fancy_grid'))
