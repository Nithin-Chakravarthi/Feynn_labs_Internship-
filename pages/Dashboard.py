import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import datetime
from bson.objectid import ObjectId
import random
from db_utils import get_amazon_price, users_coll, retailers_coll, products_coll

st.set_page_config(page_title="Dashboard")
st.title("Dashboard")

# Redirect if not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in first.")
    switch_page("Login")

role = st.session_state["role"]
user_id = st.session_state["user_id"]

# --------------------------
# Retailer Dashboard
# --------------------------
if role == "Retailer":
    st.subheader("Retailer Dashboard: Add Product")
    
    name = st.text_input("Product Name")
    description = st.text_area("Description")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    store_location = st.text_input("Store Location")
    uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])
    
    if st.button("Add Product"):
        image_data = None
        if uploaded_file is not None:
            image_data = uploaded_file.read()  # read image bytes
        products_coll.insert_one({
            "retailer_id": user_id,
            "name": name,
            "description": description,
            "price": price,
            "store_location": store_location,
            "image": image_data,  # storing binary image data; in production, consider saving file paths
            "created_at": datetime.datetime.utcnow()
        })
        st.success("Product added successfully!")
    
    st.subheader("Your Products")
    my_products = list(products_coll.find({"retailer_id": user_id}))
    for prod in my_products:
        st.write(f"**{prod['name']}** - ${prod['price']} | {prod['store_location']}")
        st.write(prod["description"])
        if prod.get("image"):
            st.image(prod["image"], use_column_width=False, width=150)

# --------------------------
# Customer Dashboard
# --------------------------
elif role == "Customer":
    st.subheader("Search for Products")
    query = st.text_input("Enter product name")
    
    if st.button("Search"):
        results = list(products_coll.find({"name": {"$regex": query, "$options": "i"}}))
        if results:
            for prod in results:
                st.markdown("---")
                st.write(f"**{prod['name']}**")
                st.write(prod["description"])
                st.write(f"Your Price: ${prod['price']}")
                amazon_price = get_amazon_price(prod["name"])
                st.write(f"Amazon Price: ${amazon_price}")
                if prod.get("image"):
                    st.image(prod["image"], width=150)
                # Book Demo button
                if st.button("Book Demo", key=str(prod["_id"])):
                    # In real implementation, send a message to the retailer.
                    st.success("Demo request sent to retailer!")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Buy", key="buy"+str(prod["_id"])):
                        st.info("Buy functionality not implemented.")
                with col2:
                    if st.button("Add to Cart", key="cart"+str(prod["_id"])):
                        st.info("Add to Cart functionality not implemented.")
        else:
            st.info("No products found.")
    
    st.subheader("Recommended Products")
    # Dummy recommendation: randomly sample up to 3 products.
    total_count = products_coll.count_documents({})
    if total_count:
        recommendations = random.sample(list(products_coll.find()), min(3, total_count))
        for rec in recommendations:
            st.markdown("---")
            st.write(f"**{rec['name']}**")
            st.write(f"Price: ${rec['price']} | Location: {rec['store_location']}")
            if rec.get("image"):
                st.image(rec["image"], width=150)
    
    st.subheader("Nearby Retailers")
    # Dummy implementation: Show retailers matching the customer's location.
    user = users_coll.find_one({"_id": ObjectId(user_id)})
    user_location = user.get("location", "")
    nearby = list(retailers_coll.find({"store_location": user_location}))
    if nearby:
        for ret in nearby:
            st.write(f"{ret['username']} - {ret['store_location']}")
    else:
        st.info("No nearby retailers found.")

# Logout Button
if st.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["user_id"] = None
    switch_page("Login")
