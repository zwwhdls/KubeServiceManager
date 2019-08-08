FROM daocloud.io/library/python:3.6.2rc1-alpine

WORKDIR /KubeServiceManager
COPY . /KubeServiceManager
COPY ./requirements.txt /KubeServiceManager
RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple

CMD ["python", "app_runner.py"]

EXPOSE 5000