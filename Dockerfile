FROM fnproject/python:3.8

ADD . /function/
WORKDIR /function/

RUN pip3 install --target /function/ oci

CMD ["func.py"]
ERRO: PUBLISH_PLUGIN
x Os seguintes erros de validação foram retornados pela API: