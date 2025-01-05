import requests
import os

UPDATE_URL = "https://api.github.com/repos/your-username/your-repo/contents"
LOCAL_REPO_DIR = "/app"

def fetch_repository_contents():
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(UPDATE_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"خطا در دسترسی به مخزن: {response.status_code}")
        return []

def download_file(file_url, file_name):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(os.path.join(LOCAL_REPO_DIR, file_name), "wb") as f:
            f.write(response.content)
        print(f"فایل {file_name} با موفقیت دانلود شد.")
    else:
        print(f"خطا در دانلود فایل {file_name}: {response.status_code}")

def update_system():
    contents = fetch_repository_contents()
    for item in contents:
        if item["type"] == "file":
            download_file(item["download_url"], item["name"])
    print("بروزرسانی کامل شد.")

if __name__ == "__main__":
    update_system()
