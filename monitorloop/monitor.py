# %%
import time
import pymongo
import traceback
import threading
import subprocess

from tqdm.auto import tqdm
from pathlib import Path
from pprint import pprint

# %%
pwd = Path(__file__).parent

# %%
cmd = 'ssh 172.18.116.146 ~/bin/uptimes-everything.sh'


def ssh_query(cmd=cmd):
    '''
    Query the machines' status by ssh
    '''
    # Checkout the latest output from the cmd,
    # the plaintext is the output
    plaintext = subprocess.check_output(cmd, shell=True)
    plaintext = plaintext.decode()

    # The results will be appended in the results
    results = []

    # Parse the plaintext and separate into queries
    queries = [e.strip() for e in plaintext.split(
        '::---- New session for machine ----') if e.strip()]

    # Further parse the queries and append it into the results
    for query in queries:
        dct = dict()
        segments = [e.strip() for e in query.split('::----') if e.strip()]

        for seg in segments:
            head, body = seg.split('\n', 1)
            dct[head] = body

        results.append(dct)

    return results

# %%


def mongo_collection():
    '''
    Get the handler of a Mongo collection
    '''
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Create or open the database
    db = client["server-monitor-db"]

    # Create or open the collection
    collection = db['server-monitor-col']

    return collection

# %%


class Monitor(object):
    '''
    The monitor class
    '''

    def __init__(self):
        self.collection = None
        pass

    # ----------------------------------------
    # Get mongo collection in a Very save way,
    # ! The safe method is not developed yet,
    # ! since I don't know how.
    def safe_mongo_collection(self):
        '''
        Get the handler of a Mongo collection
        '''

        if self.collection is not None:
            print('Using existing collection: {}'.format(self.collection))
            return self.collection

        self.collection = mongo_collection()
        return self.collection

    # ----------------------------------------
    # Update the mongodb in the loop
    def loop_update(self):
        '''
        Iterate
        '''
        def loop():
            while True:
                try:
                    self.update_mongo()
                except Exception:
                    traceback.print_exc()

                # Sleep for 60 seconds
                time.sleep(60)

        t = threading.Thread(target=loop, daemon=True)
        t.start()
        pass

    def update_mongo(self):
        '''
        Checkout and append the results into the mongo collection
        '''
        print('Update mongo')
        documents = ssh_query()

        col = self.safe_mongo_collection()

        return col.insert_many(documents)

    # ------------------------------------------------------
    # Flexible api
    # It will call the collection's method to generate the
    # very flexible operations.
    def _find(self, filter=None, projection=None, sort=None, limit=0):
        col = self.safe_mongo_collection()

        kwargs = dict(
            filter=filter,
            projection=projection,
            sort=sort,
            limit=limit
        )

        try:
            return [e for e in tqdm(col.find(**kwargs), 'Find in mongodb')]
        except Exception:
            traceback.print_exc()

        # Error occurs
        return

    def _aggregate(self, pipeline):
        col = self.safe_mongo_collection()

        # Correct the single operation
        if isinstance(pipeline, dict):
            pipeline = [pipeline]

        try:
            return [e for e in tqdm(col.aggregate(pipeline), 'Aggregate the mongodb')]
        except Exception:
            traceback.print_exc()

        # Error occurs
        return

    # -------------------------------------------------------
    # Useful api
    def fetchall_mongo(self):
        '''
        fetch all the documents from the mongo database
        '''
        return self._find()

    def summary_mongo(self):
        '''
        Get the summary of the mongo collection
        '''
        return self._aggregate({
            '$group': {
                '_id': '$machineIP',
                'count': {'$sum': 1},
                'last': {'$last': "$_id"}
            }
        })

    def checkout_mongo_by_id(self, _id):
        '''
        Checkout the document by the _id in the mongo collection
        '''
        return self._find(filter={'_id': _id})


# %%
if __name__ == '__main__':
    monitor = Monitor()
    monitor.loop_update()

    while True:
        inp = input('>> ')
        print('[---- Got cmd: {} ----]'.format(inp))

        if inp == 'q':
            break

        if 'fetchall' in inp:
            pprint(monitor.fetchall_mongo())
            continue

        if 'summary' in inp:
            pprint(monitor.summary_mongo())
            continue

        if 'last' in inp:
            for e in monitor.summary_mongo():
                pprint(monitor.checkout_mongo_by_id(e['last']))
            continue

        print('[---- Invalid cmd, doing nothing. ----]')

    print('Monitor stops')


# %%
