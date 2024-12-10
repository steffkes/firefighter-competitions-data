FROM python:3.12.2-slim-bookworm

WORKDIR /app

ADD . ./

RUN pip install -r /app/requirements.txt

CMD ["streamlit", "run", "app"]
