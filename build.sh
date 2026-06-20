#!/usr/bin/env bash
# exit on error
set -o errexit

# Download model if not present
if [ ! -f best_model.pkl ]; then
    echo "Downloading best_model.pkl..."
    curl -o best_model.pkl https://storage.googleapis.com/big3personality_model/best_model.pkl
fi

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
