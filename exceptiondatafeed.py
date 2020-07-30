from collections import defaultdict

import datetime
from mygeotab import API, dates
from mygeotab.ext import feed
import pandas
import csv


class ExceptionDataFeedListener(feed.DataFeedListener):
    def __init__(self, api):
        self.api = api
        self._cache = defaultdict(dict)
        super(feed.DataFeedListener, self).__init__()

    def _populate_sub_entity(self, entity, type_name):
        key = type_name.lower()
        if isinstance(entity[key], str):
            # If the expected sub-entity is a string, it's a unknown ID
            entity[key] = dict(id=entity[key])
            return
        cache = self._cache[key]
        subentity = cache.get(entity[key]["id"])
        
        
        if not subentity:
            subentities = self.api.get(type_name, id=entity[key]["id"], results_limit=1)
            if len(subentities) > 0:
                subentity = subentities[0]
                entity[key] = subentity
        else:
            entity[key] = subentity

    def on_data(self, data):
        for d in data:
            self._populate_sub_entity(d, "Device")
            self._populate_sub_entity(d, "Rule")
            date = datetime.datetime.now()
            result = "{date},{device},{rule}".format(
                    date=date,
                    device=d["device"].get("name", "**Unknown Vehicle"),
                    rule=d["rule"].get("name", "**Unknown Rule")
                    )
            mylist = result.split(",")
            print(mylist)
            df = pandas.DataFrame([mylist])
            df.to_csv('exceptiondatafeed.csv', index=False, header=None, mode='a')

    def on_error(self, error):
        print(error)
        return True

   
def main(database='', user='', password='', server=None, interval=60):
    api = API(database=database, username=user, password=password, server=server)
    api.authenticate()
    feed.DataFeed(api, ExceptionDataFeedListener(api), "ExceptionEvent", interval=interval).start()


if __name__ == "__main__":
    main()

