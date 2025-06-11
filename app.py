import json
import os
import sys

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
    sentMessage2 = envelope.get("dataMessage", {})

    if sentMessage is None and sentMessage2 is None :
        print("sentMessage and 2 not found")
        return

    message = None
    if sentMessage is not None:
        message = sentMessage.get("message", {})
    elif sentMessage2 is not None:
        message = sentMessage2.get("message", {})

    if message is None :
        print("message and not found")
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


        if len(res.content) <=2:
            continue



        data = res.json()

        print("got data", res)
        print("content len", len(res.content))
        print("got content", json.dumps(data))

        if not isinstance(data, list):
            print("not a list")
            continue


        for message in data:
            try:
                handle_message(message)
            except:
                e = sys.exc_info()[0]
                print("error handling message: %s", e)


        time.sleep(1)

if __name__ == "__main__":
    print("GROCYAI_API_URL: %s", os.environ.get("GROCYAI_API_URL") + "/chat")
    poll_and_respond()
