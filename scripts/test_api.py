import requests

response1 = requests.post("http://127.0.0.1:8000/session/test1234/turn", json={"utterance": "mai jharkhand se hu"})
print(response1.json())
response2 = requests.post("http://127.0.0.1:8000/session/test1234/turn", json={"utterance": "21"})
print(response2.json())
