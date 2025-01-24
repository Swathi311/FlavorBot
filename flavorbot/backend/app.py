from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process_text():
    try:
        data = request.get_json()
        user_input = data.get('text', '')
        response = {"text": f"You said: {user_input}"}
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": "An error occurred: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
