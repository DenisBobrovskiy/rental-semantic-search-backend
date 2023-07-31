from flask import (Flask, request)
import openai
import pymongo
import json
from bson import json_util

#Set OpenAI key
openai.api_key = "OPENAI API KEY"
MONGODB_CONNECTION_URI = "MONGODB CONNECTION STRING"

#Create Flask app
app = Flask(__name__)


#Set up our API route, using POST HTTP requests
@app.route('/api/getPlaces',methods=["POST"])
def getPlaces():
    print(request.form)
    input_string = request.form.get("input") #this is the input string to the POST request

    #If no input return "Invalid" with status 400
    if(input_string==None):
        return "Invalid",400

    #Generate an openai embedding from the user input
    input_embedding = get_embedding(input_string)
    print("embedding generated, length of embedding: {}".format(len(input_embedding)))


    #Connect to MongoDB. 
    # NOTE: Make sure the connection string, db_name and collection_name are correct)
    client = pymongo.MongoClient(MONGODB_CONNECTION_URI)

    db_name = "sample_airbnb"
    collection_name = "listingsAndReviews"
    collection = client[db_name][collection_name]

    #Perform Vector Search
    output_data = findSimilarDocuments(collection,input_embedding)
    print(type(output_data))

    #Print some fields of the result data
    for val in output_data:
        print("Name: {}, summary: {}, bedrooms {}.\n".format(val.get("name"),val.get("summary"),val.get("bedrooms")))
    
    return json.dumps({"data":json_util.dumps(output_data)}),200 #We return places data with status code 200. We also use json_util from BSON library to let us serialize the output from MongoDB



# this function calls OpenAI Embeddings API and returns the embedding generated for the input text
def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

#Find documents in the database's collection most similar to the inputEmbedding
def findSimilarDocuments(collection, input_embedding):
    print("Performing vector search...")
    #Generate a query that uses the Atlas search index to find documents with their "openai_embedding" field
    similar_docs_cursor = collection.aggregate([
        {
            "$search": {
                "index": "vector_search_openai", #name of the search index
                "knnBeta": {
                    "vector": input_embedding, #input embedding used for the search
                    "path": "openai_embedding", #the name of the field that contains the embedding
                    "k": 10 #How many data entries to retrieve
                }
            }
        }
    ])
    similar_docs = list(similar_docs_cursor)
    print(len(similar_docs))

    return similar_docs
    