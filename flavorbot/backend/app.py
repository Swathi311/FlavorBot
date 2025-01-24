from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_text():
    try:
        # Get the JSON payload from the POST request
        data = request.get_json()

        # Extract the 'text' field from the payload
        user_input = data.get('text', '')

        # Echo back the query as the bot's response
        response = {
            "text": f"You said: {user_input}"  # Example response
        }

        # Return the response as JSON
        return jsonify(response)

    except Exception as e:
        # Handle errors
        return jsonify({"error": "An error occurred: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
