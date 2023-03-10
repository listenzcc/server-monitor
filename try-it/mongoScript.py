# %%
import json
import pymongo

# %%
queries = json.load(open('latest_results.json'))
queries

# %%
# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Create or open the database
db = client["server-monitor-db"]

# Create or open the collection
collection = db['server-monitor-col']

res = collection.insert_many(queries)
res

# %%

# %%
[e for e in collection.find(dict(machineIP='172.18.116.146'))]
# %%

latest = [e for e in collection.aggregate([
    {
        '$group': {
            '_id': '$machineIP',
            'count': {'$sum': 1},
            'last': {'$last': "$_id"}
        }
    }
])]

latest
# %%

[e for e in collection.find({'_id': latest[0]['last']})]

# %%
