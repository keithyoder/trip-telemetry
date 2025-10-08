from loggers.mongodb import MongoClient

def tail_log(limit=10):
    """
    Fetch and print the last `limit` documents from the MongoDB collection.
    """
    # Connect to MongoDB
    client, db, collection = MongoClient()

    # Find the last 10 documents by sorting in descending natural order and limiting
    for doc in collection.find().sort([('$natural', -1)]).limit(limit):
        print(doc)

    client.close()