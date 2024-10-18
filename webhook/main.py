from flask import Flask, request
import json
from config import config
from http import HTTPStatus
import uvicorn

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    return 'OK', HTTPStatus.OK


@app.route('/liveness', methods=['GET'])
def liveness():
    return 'OK', HTTPStatus.OK


@app.route('/readiness', methods=['GET'])
def readiness():
    return 'OK', HTTPStatus.OK


@app.route('startup', methods=['GET'])
def startup():
    return 'OK', HTTPStatus.OK


@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)
    if data['action'] == 'opened':
        pr_url = data['pull_request']['html_url']
        # Trigger the bot to post the PR message on Discord
        # You can use a queue or shared state to communicate between Flask and Discord bot
        post_pr_to_discord(pr_url)
    return '', HTTPStatus.OK


def post_pr_to_discord(pr_url):
    # Use an internal mechanism to trigger the Discord bot to post the PR message
    pass


if __name__ == '__main__':
    uvicorn.run(app, host=config.WEBHOOK_HOST, port=config.WEBHOOK_PORT)
