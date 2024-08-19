FROM --platform=linux/amd64 python:3.9-alpine AS build
ADD helloweb.py /helloweb.py
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["/helloweb.py"]
