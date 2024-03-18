FROM python:3.9


# Update package lists, upgrade existing packages, and install necessary packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 \
                       python3-pip && \
                       pip3 install pandas pytest==8.0.0 requests requests-mock 

# Set working directory inside the container
WORKDIR /code

# Copy Python scripts into the container
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
COPY iss_tracker.py .
COPY test_iss_tracker.py .

# Give execute permissions to the Python scripts
RUN chmod +x iss_tracker.py
RUN chmod +x test_iss_tracker.py

# Set the environment variable PATH to include the /code directory
ENV PATH="/code:${PATH}"

# Define the default command to run when the container starts
ENTRYPOINT ["python"]
CMD ["iss_tracker.py"]
