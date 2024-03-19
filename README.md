# International Space Station Tracker: Midterm

## Overview
This folder contains 2 main scripts, `iss_tracker.py` and `test_iss_tracker.py`. The primary script `iss_tracker.py` fetches real-time International Space Station (ISS)
4 data from a provided URL, parses the XML content, and analyzes the data to provide insights such as the data range, closest epoch to the current time, average speed of 
the ISS, and instantaneous speed at the closest epoch to the current time. The test script `tester_iss_tracker.py` is designed to test the functionality of the 
iss_tracker module, which contains functions for fetching, parsing, and analyzing International Space Station (ISS) data. The script utilizes the pytest framework for
writing and executing test cases.

## Accessing the ISS Dataset.
The ISS data set can be accessed from the following link: https://spotthestation.nasa.gov/trajectory_data.cfm The XML data link at the bottom of this page, is used
in the scripts in order to perform data analysis. In order to view the data you can download the text and XML files. Doing this is recommended as it informs you about
what you are working with.

## Cloning the repostiory.
1. In order to clone this repository, open the command promp, and navigate to the directory to which you want to clone to.
2. Next, run the following command: `git@github.com:akalra501/ISS-info-tracker.git`
3. Once you have cloned the repo, make sure that you `cd` into the main directory directory by doing `cd ISS-info-tracker`.
4. Make sure the necessary scripts exist by typing in the `ls` command.

## Building a container
1. To build a container from the Dockerfile use the follwing command, and replace `<user_name>` with your docker username.:
   `docker build -t <user_name>/iss_tracker:1.0 .`
2. The above command has built the image.
3. To see the image run the following command:
    `docker images -a`
4. You will notice an image has been built.

## Running the docker-compose.yml file.
1. There is a docker-compose.yml file in this repo that will help you launch the application. The file has all the necessary information.
2. In order to run the application, use the following command `docker-compose up -d` this will start the flask app.
3. Now that the flask app is running, you can run the curl commands in the command line in order to get the output. The curl commands are explained in detail below.
4. In order to run the unit tests, run the following command: `docker exec -it iss_tracker /bin/bash`. This will take you inside the container where you can simply type in `pytest` in order to run the unit tests. If all the steps are performed correctly you should get 12 passed tests.

## Curl Commands to see output.
1. In order to see the list of all epochs you can run the following command. `curl localhost:5000/epochs`. This will print the list of all epochs to the screen
2. In order to see the list of epochs given query parameters you can run the following command. ` curl localhost:5000/epochs?limit=int&offset=int` in this command replace the 'int' with your desired numbers. The output for this command will be the list of epochs based on your query parameters.
3. In order to see the state vectors for a specific epoch, you can run the following command. `curl localhost:5000/epochs/<epoch>` instead of <epoch> you will have to write the value of an actual epoch. A sample epoch you can try is: 2024-059T12:28:00.000Z. so the modified command would be `curl localhost:5000/epochs/2024-059T12:28:00.000Z`. This will output the state vectors of this particular specified epoch.
4. In order to see the speed of a specific satellite at an epoch you can run the following command: `curl localhost:5000/epochs/<epoch>/speed` . In order to find the speed of a satellite a specific epoch you can use the above example. So the modified command would be `curl localhost:5000/epochs/2024-059T12:28:00.000Z/speed`. This will show you the speed of a satellite at the specific epoch.
5. In order to see the state vectors and the instantaneous speed of the epoch nearest in time, you can run the following command. `curl localhost:5000/now`. This will print out the state vectors and the instantaneous speed for the epoch nearest in time.
   

