import pymongo

# Connect to MongoDB
client = pymongo.MongoClient('MongoDB Connection string')
db = client['sample_airbnb']
collection = db['listingsAndReviews']

# Get the IDs of the documents to keep
documents_to_remove = collection.find().skip(300)

# Remove documents not in the list of IDs to keep
collection.delete_many({'_id': {'$in': [doc['_id'] for doc in documents_to_remove]}})

# Close the MongoDB connection
client.close()
