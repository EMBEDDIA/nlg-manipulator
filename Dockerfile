FROM python:3.6

ENV omorfi 20161115
ENV PYTHONPATH /usr/lib/python3/dist-packages

RUN echo "\nPREPARING\n" && \
    apt-get update && \
    apt-get install -y --no-install-recommends apt-utils lsb-release && \
    #
    #
    echo "\nINSTALLING HFST\n" && \
    wget http://apertium.projectjj.com/apt/apertium-packaging.public.asc -O - \
      | apt-key add - && \
    echo "deb http://apertium.projectjj.com/apt/nightly $(lsb_release -c | cut -f2) main" \
      | tee /etc/apt/sources.list.d/apertium-nightly.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends hfst libhfst52 python3-libhfst zip autoconf automake && \
    #
    #
    echo "\nFIXING HFST\n" && \
    ls /usr/lib/python3/dist-packages/ && \
    ln -s /usr/lib/python3/dist-packages/_libhfst.cpython-35m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/_libhfst.so

RUN echo "\nINSTALLING OMORFI\n" && \
    apt-get update && apt-get install -y zip autoconf automake && \
    wget https://github.com/flammie/omorfi/archive/${omorfi}.tar.gz && \
    tar -xvzf ${omorfi}.tar.gz && \
    cd omorfi-${omorfi} && \
    ls && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig 
  
RUN echo "\nINSTALLING OTHER REQUIREMENTS FROM APT\n" && \
    apt-get update && apt-get install -y gfortran libhdf5-100

RUN echo "\nINSTALLING REQUIREMENTS FROM PIP\n"
COPY ["requirements.txt", "requirements.txt"]
RUN pip3 install -r /requirements.txt

RUN echo "\nCOPYING FILES\n"
RUN mkdir app

RUN echo "\nREMOVING EXTRA OMORFI AUTOMATA\n" && \
    rm /usr/local/share/omorfi/omorfi.accept.hfst /usr/local/share/omorfi/omorfi-omor_recased.analyse.hfst

# Heroku ignores this, required for local testing
EXPOSE 8080

ADD . /app
WORKDIR /app

# Heroku runs as non-root
RUN chmod a+rxw -R /app

RUN adduser --disabled-password myuser
USER myuser

#CMD python3 /app/src/server.py $PORT
CMD python3 /app/src/server.py 8080
