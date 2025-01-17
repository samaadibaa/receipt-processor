from flask import Flask, request, jsonify
import uuid
from datetime import datetime
from decimal import Decimal, ROUND_UP

app = Flask(__name__) # app is the central part of the web service it defines routes and run the server

# In-memory store for receipts and points
receipts_data = {} # Using a dictionary to store recept IDs as keys and calculated points as values


def calculate_points(receipt): # In the calculate_points function the input is the receipt data
    points = 0 # The output is the total points based on the receipt rules
               # Initialized points to 0 to store the total

    # Rule 1: One point per alphanumeric character in the retailer name
    retailer = receipt['retailer'] # Extract the retailer name from the receipt
    points += sum(c.isalnum() for c in retailer) # add 1 point for every alphanumeric character in the retailer name

    # Rule 2: 50 points if the total is a round dollar amount
    total = Decimal(receipt['total'])  # Convert total to Decimal for precise monetary operations
    if total % 1 == 0:  # Check if the total is a whole number (no cents)
        points += 50  # Add 50 points for a round dollar amount

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % Decimal('0.25') == 0:  # Check if the total is a multiple of 0.25
        points += 25  # Add 25 points if true

    # Rule 4: 5 points for every two items
    num_items = len(receipt['items']) # Count the total number of items in the receipt
    points += (num_items // 2) * 5    # Add 5 points for every pair of items

    # Rule 5: Special points for item descriptions
    for item in receipt['items']:  # Loop through all items in the receipt
        trimmed_desc = item['shortDescription'].strip()  # Remove any extra spaces from the item's description
        if len(trimmed_desc) % 3 == 0:  # Check if the length of the trimmed description is a multiple of 3
            item_price = Decimal(item['price'])  # Convert the item's price to Decimal for accurate calculations
            points += (item_price * Decimal('0.2')).quantize(Decimal('1'), rounding=ROUND_UP)  # Add rounded-up points

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt['purchaseDate'], "%Y-%m-%d") # Parse the purchaseDate string into a datetime object
    if purchase_date.day % 2 != 0: # If the day is odd, add 6 points
        points += 6

    # Rule 7: 10 points if the purchase time is between 2:00pm and 4:00pm
    purchase_time = datetime.strptime(receipt['purchaseTime'], "%H:%M").time()  # Parse purchase time into a time object
    if purchase_time.hour == 14:  # Check if the time is between 2:00pm and 3:59pm
        points += 10  # Add 10 points if true

    return int(points)  # Return the total points as an integer


@app.route("/receipts/process", methods=["POST"]) # This allows the client to submit receipt data
def process_receipt():
    receipt = request.json # Parse the JSON payload from the request into a python dictionary (receipt)
    receipt_id = str(uuid.uuid4()) # Generate a unique id (receipt_id) for this receipt
    points = calculate_points(receipt) # Calculate the total points for the submitted receipt
    receipts_data[receipt_id] = points # Store the calculated points in receipts_data dictionary using the receipt_id
    return jsonify({"id": receipt_id}) # respond with the generated receipt id in JSON format


@app.route("/receipts/<receipt_id>/points", methods=["GET"]) # This allows the client to request points for a specific receipt id
def get_points(receipt_id):
    points = receipts_data.get(receipt_id) # Look up the points associated with the receipt_id in the receipts_data dictionary
    if points is None: # if the id is not found, respond with the error message and 404 code
        return jsonify({"error": "Receipt not found"}), 404
    return jsonify({"points": points}) # If found, return the points in JSON format


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) # host is accesssible from any network, port 8080
