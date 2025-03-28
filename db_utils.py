import pymongo
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

# MongoDB Setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["technest"]
users_coll = db["users"]
retailers_coll = db["retailers"]
products_coll = db["products"]
messages_coll = db["messages"]

# Dummy function to simulate Amazon price comparison.
def get_amazon_price(product_name):
    import random
    return round(random.uniform(0.9, 1.1) * 100, 2)

# Helper function for user authentication
def authenticate_user(email, password, role):
    collection = retailers_coll if role == "Retailer" else users_coll
    user = collection.find_one({"email": email})
    if user and check_password_hash(user["password"], password):
        return str(user["_id"])
    return None

# Register new users or retailers.
def register_user(username, email, password, role, location):
    hashed = generate_password_hash(password)
    collection = retailers_coll if role == "Retailer" else users_coll
    if collection.find_one({"email": email}):
        return False
    collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed,
        "location": location,
        "created_at": datetime.datetime.utcnow()
    })
    return True

# KNN-based content filtering recommendations.
# It uses the product's price and one-hot encoded store_location as features.
def get_knn_recommendations(user_location, price_preference, n_neighbors=3):
    products = list(products_coll.find())
    if not products:
        return []
    # Create DataFrame from products.
    df = pd.DataFrame(products)
    # Ensure price is float.
    df['price'] = df['price'].astype(float)
    # One-hot encode store_location.
    df_onehot = pd.get_dummies(df['store_location'], prefix='loc')
    features = pd.concat([df[['price']], df_onehot], axis=1)
    # Fit NearestNeighbors model.
    nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
    nn_model.fit(features)
    # Create user feature vector.
    # One-hot encode user_location based on df_onehot columns.
    user_onehot = [0] * len(df_onehot.columns)
    columns = list(df_onehot.columns)
    for i, col in enumerate(columns):
        if col == f"loc_{user_location}":
            user_onehot[i] = 1
    user_feature = np.array([price_preference] + user_onehot).reshape(1, -1)
    distances, indices = nn_model.kneighbors(user_feature)
    recommended = df.iloc[indices[0]].to_dict(orient='records')
    return recommended
