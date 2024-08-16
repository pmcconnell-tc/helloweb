FROM python:3.7-alpine
ADD helloweb.py /helloweb.py
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["/helloweb.py"]
