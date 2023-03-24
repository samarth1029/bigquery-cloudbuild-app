FROM python:3.9-slim as bigquery-cloudbuild-app
EXPOSE 8080
ENV APP_HOME /app
ENV PORT 8080
WORKDIR $APP_HOME
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]