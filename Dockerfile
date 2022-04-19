FROM python:3.8.10

WORKDIR app/

COPY ./ ./
RUN pip install -r requirements.txt

RUN mkdir "output"
EXPOSE 5000

CMD ["gunicorn","app:app"]