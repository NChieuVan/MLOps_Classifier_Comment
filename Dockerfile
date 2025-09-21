FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# chuyển source sang archive.debian.org rồi mới update/install
RUN set -eux; \
    sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list; \
    sed -i 's|security.debian.org|archive.debian.org/debian-security|g' /etc/apt/sources.list; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get install -y --no-install-recommends libgomp1; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY app.py lgbm_model.pkl tfidf_vectorizer.pkl ./
COPY fontend_basic/ ./fontend_basic

EXPOSE 8080
CMD ["python", "app.py"]
