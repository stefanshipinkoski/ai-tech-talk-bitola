from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_model import generate_response, extract_json_yaml_code

app = Flask(__name__)
CORS(app)
app.config["ENV"] = "production"


@app.route("/generate", methods=["GET", "POST"])
def handle_response():
    try:
        if request.method == "GET" or request.method == "POST":
            data = request.get_json()

            # check if the prompt exists in the request data
            if "prompt" in data:
                print("Received prompt:", data["prompt"])
                response = generate_response(data["prompt"])

                # extract schema if existing
                schema = extract_json_yaml_code(response)
                return schema
            else:
                return jsonify({"error": "Missing prompt in the request data."}), 400
        else:
            return jsonify({"error": "Invalid request method. Use POST or GET"}), 405
    except Exception as err:
        return jsonify({"error": str(err)}), 500


if __name__ == "__main__":
    app.run(debug=True)
