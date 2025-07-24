FROM python:3.11
# set work directory
WORKDIR /
# copy project
COPY . .
# install dependencies
RUN pip install pytelegrambotapi sqlalchemy pymysql yookassa uuid

EXPOSE 80
# run app
CMD ["python", "bot.py"]