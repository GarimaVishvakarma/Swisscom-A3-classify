from flask import Flask, jsonify, request

app = Flask(__name__)



@app.route('/', methods=['GET'])
def home():

    return jsonify({"data": "response"})


if __name__ == '__main__':
    app.run(host="10.100.38.96", port=5000, debug=True)