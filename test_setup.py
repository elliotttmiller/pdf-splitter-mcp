import httpx

# 1. Create a dummy PDF
with open("test.pdf", "wb") as f:
    f.write(b"%PDF-1.4\n%Dummy Content")

# 2. Upload
url = "http://127.0.0.1:8000"
files = {'file': open('test.pdf', 'rb')}
resp = httpx.post(f"{url}/upload", files=files)

print("Upload Status:", resp.status_code)
print("Response:", resp.json())
