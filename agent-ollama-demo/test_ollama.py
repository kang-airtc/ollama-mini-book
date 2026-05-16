import requests

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.2:latest",
        "messages": [{"role": "user", "content": "请介绍一下Ollama并用中文回答."}],
    },
    stream=True,
)

for line in response.iter_lines():
    if line:
        data = line.decode("utf-8")
        print(data)
