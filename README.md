export MODEL_SERVER=localhost:8000
flask --app main.py --debug run --port 5001 --host 0.0.0.0
podman run -d --name simplevis-ui -p 5001:5001 -v simplevis-data:/opt/app-root/src/simplevis-data simplevis-ui