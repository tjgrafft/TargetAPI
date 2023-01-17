from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import pandas as pd
import requests

app = Flask(__name__)

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017/")
db = client["target_products"]

# Create the API endpoints

@app.route("/")
def products():
    # Make an HTTP GET request to the /products endpoint
    response = requests.get("http://localhost:5000/products")
    
    # Parse the JSON response
    data = response.json()
    
    # Render the products template with the product data
    return render_template("products.html", products=data)

@app.route("/products", methods=["GET"])
def get_products():
    # Retrieve a list of all products in the database
    products = list(db.products.find())

    # Convert the list of products to a Pandas dataframe
    df = pd.DataFrame(products)

    # Filter the df by only grabbing the rows where the category is Clothing. Also sort the data by price
    df = df[df["category"] == "Clothing"]
    df = df.sort_values("price", ascending=False)
    
    # Return the dataframe as a JSON response
    return jsonify(df.to_dict("records"))

@app.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    # Retrieve a single product from the database using its ID
    product = db.products.find_one({"id": product_id})
    
    # Return the product as a JSON response
    return jsonify(product)

@app.route("/products", methods=["POST"])
def add_product():
    # Retrieve the product data from the request body
    data = request.get_json()
    
    # Insert the new product into the database
    result = db.products.insert_one(data)
    
    # Return the ID of the new product as a JSON response
    return jsonify({"id": result.inserted_id})

@app.route("/products/<product_id>", methods=["PUT"])
def update_product(product_id):
    # Retrieve the updated product data from the request body
    data = request.get_json()
    
    # Update the product in the database using its ID
    result = db.products.update_one({"id": product_id}, {"$set": data})
    
    # Return the number of documents modified as a JSON response
    return jsonify({"modified_count": result.modified_count})

@app.route("/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    # Delete the product from the database using its ID
    result = db.products.delete_one({"id": product_id})
    
    # Return the number of documents deleted as a JSON response
    return jsonify({"deleted_count": result.deleted_count})

if __name__ == "__main__":
    app.run()
