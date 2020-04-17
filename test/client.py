import requests

files = [
    ("file_md", open("commands.py", 'rb')),
    ("file_md", open("mylogger.py", 'rb')),
]
r = requests.post(
    url="http://localhost:10051/hexo",
    data={'type': 'help'},
    # files=files
)

print(r.status_code)
print(r.text)