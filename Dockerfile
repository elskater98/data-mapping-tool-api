FROM python:3.8.10

WORKDIR flask_app/

COPY ./ ./
RUN pip install -r requirements.txt
CMD ["python","app.py"]