import base64
import requests


class OllamaModel:
    def __init__(self, 
        model_name: str, 
        max_tokens: int = 300) -> None:
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.url = "http://localhost:11434/api/chat"
        self.headers = {"Content-Type": "application/json"}
        

    def __call__(self,question:str,image_file:str=None):
        payload= {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": question}
            ],
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        if image_file is not None:
            payload["messages"][0]["images"] = [
                base64.b64encode(open(image_file, "rb").read()).decode("utf-8")
            ]
        response = requests.post(
            url=self.url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        return response.json()["message"]["content"]

if __name__ == "__main__":
    model = OllamaModel("qwen2.5vl:32b")
    print(model("你好"))
