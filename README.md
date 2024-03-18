# COE 332 Homework04: The ISS Aquatic data analysis.

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
2. Next, run the following command: `git clone git@github.com:akalra501/coe332-Homeworks.git`
3. Once you have cloned the repo, make sure that you `cd` into the homework04 directory by doing `cd homework04`.
4. Make sure the necessary scripts exist by typing in the `ls` command.

## Building a container
1. To build a container from the Dockerfile use the follwing command, and replace `<user_name>` with your docker username.:
   `docker build -t <user_name>/flask-homework05:1.0 .`
2. The above command has built the image.
3. To see the image run the following command:
    `docker images -a`
4. You will notice an image has been built.

## Running the containerized code
1. Since the image has been built you can use the following command to create a docker container from the image:
  ` docker run --rm -it <user_name>/flask-homework05:1.0 `, again replacing the username with your docker username.
2. This will show that your app has started running on a server.
3. The next step is to copy the http path shown on the screen.
4. Once, the path has been copied, navigate to a new terminal window.
5. Navigate to the jetstream VM in the new window.
6. Now you can begin executing the curl commands.

##Curl Commands to see output.
1. In order to see the list of all epochs you can run the following command. `curl localhost:5000/epochs`. This will print the list of all epochs to the screen
2. In order to see the list of epochs given query parameters you can run the following command. ` curl localhost:5000/epochs?limit=int&offset=int` in this command replace the 'int' with your desired numbers. The output for this command will be the list of epochs based on your query parameters.
3. In order to see the state vectors for a specific epoch, you can run the following command. `curl localhost:5000/epochs/<epoch>` instead of <epoch> you will have to write the value of an actual epoch. A sample epoch you can try is: 2024-059T12:28:00.000Z. so the modified command would be `curl localhost:5000/epochs/2024-059T12:28:00.000Z`. This will output the state vectors of this particular specified epoch.
4. In order to see the speed of a specific satellite at an epoch you can run the following command: `curl localhost:5000/epochs/<epoch>/speed` . In order to find the speed of a satellite a specific epoch you can use the above example. So the modified command would be `curl localhost:5000/epochs/2024-059T12:28:00.000Z/speed`. This will show you the speed of a satellite at the specific epoch.
5. In order to see the state vectors and the instantaneous speed of the epoch nearest in time, you can run the following command. `curl localhost:5000/now`. This will print out the state vectors and the instantaneous speed for the epoch nearest in time.
   

