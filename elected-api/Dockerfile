


FROM python:bookworm

ADD . /install
WORKDIR /install
RUN pip install -r requirements.txt

# app execution
CMD ["python", "app.py"]


