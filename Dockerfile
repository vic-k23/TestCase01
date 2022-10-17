FROM python:3.10
# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:/code/.venv/bin:$PATH"
# Some tune for poetry
RUN poetry config virtualenvs.in-project true
# Change workdir
WORKDIR /code
# Copy project file
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
# Install dependencies
RUN poetry install
# Copy project code
COPY ./app /code
# Expose 80 port
EXPOSE 80
# Run service
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
