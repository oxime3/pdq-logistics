# pdq-logistics
Repository for pdq-logistics sub-system 

## Prerequisites
- Docker & Docker-compose

## Installation
Clone the repository:
```
$ git clone https://github.com/oxime3/pdq-logistics.git
```
## Usage
1. From the directory containing the `docker-compose.yml` file, run the API and van-module using:
```
$ docker-compose up
```
2. Since this is a prototype, you will need to to edit the IP address in the configuration file, or the app will load the map but not be able to load van locations by connecting to the API. The file is called `APIService.java`. The example below uses nano to edit the file:
```
$ nano ~/modules/MapboxLocationTracking-master/app/src/main/java/com/khadejaclarke/mapboxlocationtracking/utils/APIService.java
```

Edit the line below, replacing the indicated section with the IP address of the computer you are running the API on:
  
`String BASE_URL = "http://*<YOUR-IP-ADDRESS>*:5000/pdq/";`

2. Compile the app and install the apk on an android mobile device.

3. Run the app.

![app_image](images/van_placements.png)
