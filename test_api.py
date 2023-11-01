from flask import Flask, jsonify, request
import hashlib
import math
import requests
import redis

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@app.route('/md5/<string>', methods=['GET'])
def md5_string(string):
    md5_hash = hashlib.md5(string.encode()).hexdigest()
    return jsonify(input=string, output=md5_hash), 200

@app.route('/factorial/<int:n>', methods=['GET'])
def factorial_int(n):
    if n < 0:
        return jsonify(input=n, output="Error: Input must be a positive integer."), 400
    else:
        return jsonify(input=n, output=math.factorial(n)), 200

@app.route('/fibonacci/<int:n>', methods=['GET'])
def fibonacci_int(n):
    if n < 0:
        return jsonify(input=n, output="Error: Input must be a positive integer."), 400
    fib_seq = [0, 1]
    while fib_seq[-1] + fib_seq[-2] <= n:
        fib_seq.append(fib_seq[-1] + fib_seq[-2])
    return jsonify(input=n, output=fib_seq), 200

@app.route('/is-prime/<int:n>', methods=['GET'])
def is_prime_int(n):
    if n < 2:
        return jsonify(input=n, output="Error: Input must be a positive integer greater than 1."), 400
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return jsonify(input=n, output=False), 200
    return jsonify(input=n, output=True), 200

@app.route('/slack-alert/<string>', methods=['GET'])
def slack_alert_string(string):
    webhook_url = 'https://hooks.slack.com/services/your-webhook-url'
    payload = {'text': string}
    response = requests.post(webhook_url, json=payload)
    return jsonify(input=string, output=response.ok), 200

@app.route('/keyval', methods=['POST', 'PUT'])
@app.route('/keyval/<string:key>', methods=['GET', 'DELETE'])
def keyval(key=None):
    if request.method == 'POST':
        payload = request.get_json()
        if not payload or 'storage-key' not in payload or 'storage-val' not in payload:
            return jsonify(error="Invalid request", result=False), 400
        if redis_client.exists(payload['storage-key']):
            return jsonify(error="Key already exists", result=False), 409
        redis_client.set(payload['storage-key'], payload['storage-val'])
        return jsonify(command=f"CREATE {payload['storage-key']}/{payload['storage-val']}", result=True), 200

    elif request.method == 'GET':
        if not key or not redis_client.exists(key):
            return jsonify(error="Key does not exist", result=False), 404
        value = redis_client.get(key).decode('utf-8')
        return jsonify(key=key, value=value, command=f"READ {key}", result=True), 200

    elif request.method == 'PUT':
        payload = request.get_json()
        if not payload or 'storage-key' not in payload or 'storage-val' not in payload:
            return jsonify(error="Invalid request", result=False), 400
        if not redis_client.exists(payload['storage-key']):
            return jsonify(error="Key does not exist", result=False), 404
        redis_client.set(payload['storage-key'], payload['storage-val'])
        return jsonify(command=f"UPDATE {payload['storage-key']}/{payload['storage-val']}", result=True), 200

    elif request.method == 'DELETE':
        if not key or not redis_client.exists(key):
            return jsonify(error="Key does not exist", result=False), 404
        redis_client.delete(key)
        return jsonify(command=f"DELETE {key}", result=True), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
