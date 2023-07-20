from flask import Flask
from redis import Redis
import os

app = Flask(__name__)

redisHost = os.environ.get('REDIS_HOST', default = "localhost")
redisPort = os.environ.get('REDIS_PORT', default = 6379)
r = Redis(host = redisHost, port = redisPort, decode_responses = True)

@app.route("/")
def hello_world():
    try:
        return r.lpop()
    except:
        return 'no cookie yet'
