FROM ubuntu:18.04

LABEL Author="Scott Allen" \
Description="This dockerfile creates an image that runs \
the PDQ API"  version="1.0"

RUN apt update &&\
	apt install -y python3-minimal python3-pip python3-distutils curl

RUN pip3 install pipenv

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list | tee /etc/apt/sources.list.d/msprod.list

RUN apt update && \
ACCEPT_EULA=Y apt install -y mssql-tools unixodbc-dev

RUN apt update
RUN apt install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
    
ENV LANG en_US.utf8

WORKDIR /usr/src/app
COPY . .

RUN pipenv install --deploy --ignore-pipfile 
EXPOSE 5000
ENTRYPOINT ["pipenv","run","python","pdq_api.py"]

