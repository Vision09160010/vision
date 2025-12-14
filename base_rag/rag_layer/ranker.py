import requests

def rank(text_1, text_2, model="bge-reranker-v2-m3"):
    url = f"http://127.0.0.1:8000/score"
    data = {
        "model": model,
        "encoding_format": "float",
        "text_1": text_1,
        "text_2": text_2
    }

    response = requests.post(url, json=data)
    score = response.json()['data'][0]['score']
    return score