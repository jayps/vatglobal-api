FROM python:3.9.11-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
COPY requirements.dev.txt /code/
RUN pip install -r requirements.dev.txt
COPY . /code/
EXPOSE 8000
RUN ["chmod", "+x", "/code/entrypoint.sh"]
ENTRYPOINT /code/entrypoint.sh