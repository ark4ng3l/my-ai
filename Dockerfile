# استفاده از تصویر پایه Python
FROM python:3.10-slim

# تنظیمات محیطی برای جلوگیری از نمایش اضافی اطلاعات
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# نصب ابزارهای مورد نیاز
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ارتقاء pip و نصب ابزارهای مرتبط
RUN pip install --upgrade pip setuptools wheel

# تنظیم دایرکتوری کاری داخل کانتینر
WORKDIR /app

# کپی کردن فایل‌های پروژه از سیستم محلی به داخل کانتینر
COPY . /app

# نصب پیش‌نیازهای پروژه از فایل requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# دانلود مدل‌ها در زمان ساخت
RUN python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; tokenizer = AutoTokenizer.from_pretrained('EleutherAI/gpt-neo-1.3B'); model = AutoModelForCausalLM.from_pretrained('EleutherAI/gpt-neo-1.3B')"

# اجرای اسکریپت به‌روزرسانی خودکار از مخزن Git
RUN python update_repo.py

# تعیین پورت مورد نظر
EXPOSE 8000

# اجرای برنامه اصلی (Flask)
CMD ["python", "myai.py"]
