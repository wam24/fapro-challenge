FROM python:3.10.0-alpine



RUN apk add --no-cache --virtual .build-deps \
                      curl \
                      gcc \
                      build-base \
                      freetype-dev \
                      libpng-dev \
                      openblas-dev



RUN curl https://bootstrap.pypa.io/pip/get-pip.py  -o /get-pip.py  \
    && python /get-pip.py \
    && pip install virtualenv \
    && virtualenv /env \
    && chmod u+x /env/bin/activate

COPY ./requirements.txt /app/requirements.txt

COPY ./app ./app

ENV VIRTUAL_ENV=/env \
    PATH=/env/bin:$PATH

RUN . /env/bin/activate && pip install -r app/requirements.txt 

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
