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

# Insert the queries defined in above
# res = collection.insert_many(queries)
# res

# %%

# %%
[e for e in collection.find(dict(machineIP='172.18.116.146'))]


# %%

aggregate = [e for e in collection.aggregate([
    {
        '$group': {
            '_id': '$machineIP',
            'count': {'$sum': 1},
            'last': {'$last': "$_id"},
            'first': {'$first': '$_id'}
        }
    }
])]

aggregate

# %%
for group in aggregate:
    print(group)
    cursor = collection.find({'_id': group['first']})
    print([e for e in cursor])

    # !!! Delete the first record
    # collection.delete_one({'_id': group['first']})


# %%
[e for e in collection.find({'_id': aggregate[0]['first']})]

# %%
[e for e in collection.find({'_id': aggregate[0]['last']})]

# %%
aggregate[0]['first']

# %%
