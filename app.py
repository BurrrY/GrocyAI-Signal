import json
import os

import requests
import time

SIGNAL_NUMBER = os.environ.get("SIGNAL_NUMBER")
API_URL = os.environ.get("SIGNAL_API_URL")
CHAT_BACKEND = os.environ.get("GROCYAI_API_URL") + "/chat"


def handle_message(data):
    if not "envelope" in data:
        print("envelope not found")
        return

    envelope = data.get("envelope", {})
    sentMessage = envelope.get("syncMessage", {}).get("sentMessage")

    if sentMessage is None:
        print("sentMessage not found")
        return

    message = sentMessage.get("message", {})
    groupInfo = sentMessage.get("groupInfo", {}).get("groupName")

    if groupInfo != "Haushalt":
        print("not interested in message from ", groupInfo)
        return

    if message:
        print("sending message:", message)
        reply = requests.post(CHAT_BACKEND, json={"text": message}).json()["reply"]

        print("got reply:", reply)
        requests.post(f"{API_URL}/v2/send", json={
            "message": reply,
            "number": SIGNAL_NUMBER,
            "recipients": [os.environ.get("SIGNAL_GROUP_ID")]
        })


def poll_and_respond():
    while True:
        res = requests.get(f"{API_URL}/v1/receive/{SIGNAL_NUMBER}")
        if res.status_code != 200:
            time.sleep(5)
            continue

        print("got data", res)
        print("content len", len(res.content))

        if len(res.content) <2:
            continue


        data = res.json()

        print("got content", json.dumps(data))

        if not isinstance(data, list):
            print("not a list")
            continue


        for message in data:
            handle_message(message)


        time.sleep(2)

if __name__ == "__main__":
    poll_and_respond()
