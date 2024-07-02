FROM python:3.9-alpine
WORKDIR /aiaos-kds

COPY . /aiaos-kds/


# Install dependencies
RUN pip install --upgrade pip
RUN pip install pandas
RUN pip install openpyxl
RUN pip install -r requirements.txt

# Set permission for entrypoint
RUN chmod u+x ./entrypoint.sh
CMD ["./entrypoint.sh"]