from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
uri = os.getenv('db_uri')

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))


def send_message_to_mongodb(filename, comparision, left_model, right_model, status, ip):
    db = client.get_database("lime_eval")
    collection = db.get_collection(f"{comparision}_comparisons")
    
    message = {
        "filename": filename,
        "left_model": left_model,
        "right_model": right_model,
        "status": status,
        "ip": ip
    }
    
    try:
        collection.insert_one(message)
        print("Message sent to MongoDB successfully.")
    except Exception as e:
        print(f"An error occurred while sending the message to MongoDB: {e}")

def get_all_messages_from_collection(comparision):
    db = client.get_database("lime_eval")
    collection = db.get_collection(f"{comparision}_comparisons")
    
    try:
        messages = list(collection.find())
        if messages:
            print("Messages retrieved from MongoDB successfully.")
            return messages
        else:
            print("No messages found in the collection.")
            return []
    except Exception as e:
        print(f"An error occurred while retrieving messages from MongoDB: {e}")
        return []


if __name__ == "__main__":
    send_message_to_mongodb("test.png", 'noise', "IMGS_bread", "IMGS_ZeroDCE", "IMGS_bread")
    print(get_all_messages_from_collection('noise'))