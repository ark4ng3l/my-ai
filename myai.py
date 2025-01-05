import os
import requests
import sqlite3
import subprocess
import pyttsx3
import speech_recognition as sr
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer

# تنظیمات پایه
DB_NAME = "memory.db"
MODEL_NAME = "EleutherAI/gpt-neo-1.3B"
UPDATE_URL = "https://api.github.com/repos/your-username/your-repo/contents"

# مدل هوش مصنوعی
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# تشخیص و تبدیل گفتار
engine = pyttsx3.init()

# 1. پایگاه داده
def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_to_memory(user_input, ai_response):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memory (user_input, ai_response)
        VALUES (?, ?)
    """, (user_input, ai_response))
    conn.commit()
    conn.close()

# 2. تعامل متنی/صوتی
def chat_with_model(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"], max_length=150, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("لطفاً صحبت کنید...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio, language="fa-IR")
        except sr.UnknownValueError:
            return "متاسفم، نتوانستم صحبت شما را تشخیص دهم."

# 3. بروزرسانی خودکار
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
        with open(file_name, "wb") as f:
            f.write(response.content)
        print(f"فایل {file_name} با موفقیت دانلود شد.")
    else:
        print(f"خطا در دانلود فایل {file_name}: {response.status_code}")

def update_system():
    contents = fetch_repository_contents()
    for item in contents:
        if item["type"] == "file":
            download_file(item["download_url"], item["name"])
    print("بروزرسانی کامل شد. سیستم راه‌اندازی مجدد می‌شود...")
    subprocess.run(["python", "myai.py"])

# 4. مدیریت سیستم
def main():
    initialize_database()
    print("سیستم هوش مصنوعی آماده است.")

    while True:
        print("\n1. تعامل متنی")
        print("2. تعامل صوتی")
        print("3. بروزرسانی سیستم")
        print("4. خروج")
        choice = input("انتخاب شما: ")

        if choice == "1":
            user_input = input("پیام شما: ")
            response = chat_with_model(user_input)
            print(f"پاسخ: {response}")
            save_to_memory(user_input, response)
        elif choice == "2":
            user_input = listen()
            response = chat_with_model(user_input)
            print(f"پاسخ: {response}")
            speak(response)
            save_to_memory(user_input, response)
        elif choice == "3":
            update_system()
        elif choice == "4":
            print("خداحافظ!")
            break
        else:
            print("انتخاب نامعتبر. دوباره تلاش کنید.")

if __name__ == "__main__":
    main()
