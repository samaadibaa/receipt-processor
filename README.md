# Set up
# Build the docker image
Run the following command in the `receipt-processor` directory:
docker build -t processor .

# Start app by running
docker run -p 8080:8080 processor
# to process the receipt sent POST request to
http://localhost:8080/receipts/process

# To get points send a GET request to
http://localhost:8080/receipts/<id>/points
