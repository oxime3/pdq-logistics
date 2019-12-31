FROM ubuntu:18.04
LABEL Author="Scott Allen" \
Description="This dockerfile creates an image that runs \
delivery zone generating module for PDQ" version="1.0"

RUN apt update
RUN apt install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

RUN apt update
RUN apt install -y python3-minimal python3-pip python3-distutils curl
RUN pip3 install pipenv

WORKDIR /usr/src/app
COPY . .

RUN pipenv install --deploy --ignore-pipfile 
ENTRYPOINT ["pipenv","run","python","__init__.py"]

#COPY startup_script.sh /scripts/startup_script.sh
#RUN ["chmod", "+x", "/scripts/startup_script.sh"]
#ENTRYPOINT ["/scripts/startup_script.sh"]