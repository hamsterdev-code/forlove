FROM python:3.11
# set work directory
WORKDIR /
# copy project
COPY . .
# install dependencies
RUN pip install pytelegrambotapi sqlalchemy pymysql uvicorn yookassa fastapi

EXPOSE 8000
# run app
CMD ["python", "checker.py"]