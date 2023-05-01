FROM python:3.10-alpine

ENV DEVMAN_ACCESS_TOKEN=$DEVMAN_ACCESS_TOKEN
ENV TG_BOT_TOKEN=$TG_BOT_TOKEN
ENV TG_USER_CHAT_ID=$TG_USER_CHAT_ID

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

COPY main.py ./
CMD ["python", "main.py"]
