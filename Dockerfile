FROM public.ecr.aws/lambda/python:3.9

# Hack to install chromium dependencies
RUN yum install -y -q sudo unzip
RUN yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

# Find the version of latest stable build of chromium from below
# https://omahaproxy.appspot.com/
# Then follow the instructions here in below URL 
# to download old builds of Chrome/Chromium that are stable
# Current stable version of Chromium
ENV CHROMIUM_VERSION=1002910


# Install Chromium
COPY install-browser.sh ./
RUN /usr/bin/bash ./install-browser.sh
ENV PATH="${PATH}:/opt"

COPY chrome-deps.txt ./
RUN yum install -y $(cat ./chrome-deps.txt)

# Install Python dependencies for function
COPY requirements.txt ./
RUN python3 -m pip install --upgrade pip -q
RUN python3 -m pip install -r ./requirements.txt -q 


COPY . ${LAMBDA_TASK_ROOT}
CMD [ "lambda_function.lambda_handler" ]