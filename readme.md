# Xccelerated-Assessments

## Table of Contents
- [Overview](#overview)
- [Business Problem](#business-problem)
- [Solution Explanation](#solution-explanation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Setup](#setup)
- [Additional Information](#additional-information)
- [References](#references)

## Overview
This application extracts data from an API, processes the data, and stores it in a PostgreSQL database. It then exposes the processed data through a Flask API endpoint. This README provides an overview of the application, its components, and the workflow involved.

## Business Problem
The goal of this application is to analyze and present data from events captured by an API. The data includes event details such as event ID, event type, customer ID, timestamp, and session information. The business problem revolves around understanding customer behavior and session patterns to make informed decisions and optimize user experience.

## Solution Explanation
To address the business problem, the application follows these steps:

1. **Data Extraction and Ingestion**: The `app.py` script extracts data from the API and ingests it into a PostgreSQL database table. The extracted data is processed and transformed into a dataframe, which is then stored in the database.

2. **Data Preprocessing**: The data is preprocessed to derive additional features necessary for analysis. This includes calculating the time duration of each event, determining the previous event's timestamp, identifying new sessions, and assigning session IDs.

3. **Database Setup**: The `model.py` script provides the necessary code to create the database and table structure required for storing the processed data. It uses the credentials specified in `config.py` to establish a connection with the PostgreSQL database.

4. **Flask API**: The `app.py` script utilizes the Flask framework to create an API that exposes the processed data. The API endpoint is hosted on `0.0.0.0` with port `8000`.

5. **SQL Query**: The API endpoint handles incoming requests by executing a SQL query on the database. The query calculates two metrics: `median_visits_before_order` and `median_session_duration_minutes_before_order`. The results are then returned in JSON format.

## Project Structure

The project directory consists of the following files:

- `app.py`: The main script responsible for data extraction, preprocessing, database ingestion, and API creation using Flask.
- `config.py`: Contains all the necessary credentials for the database connection and API URL.
- `docker-compose.yml`: Configuration file for running the application with Docker Compose.
- `Dockerfile`: File used to build the Docker image for the application.
- `model.py`: Script to set up the PostgreSQL database and create the necessary table.
- `requirements.txt`: Lists all the Python dependencies required for the project.
- `query_1.sql`: SQL query for analysis (not directly related to the scripts).
- `query_2.sql`: SQL query for analysis (not directly related to the scripts).


## Setup
Before running the application, ensure that you have Docker and Docker Compose installed on your machine. If not, follow the official Docker documentation to install the necessary components.

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Open the `config.py` file and provide the required credentials for the database connection and API URL.
4. Run the command `docker-compose up` to start the application. Docker Compose will build the necessary images and containers based on the provided configurations.
5. Once the application is up and running, you can access the API endpoint at `http://localhost:8000` to retrieve the processed data.

## Data Table
The `tb_events` table in the PostgreSQL database contains the following columns:

- `event_id`: The ID of the event.
- `event_type`: The description of the event type.
- `customer_id`: The ID of the customer.
- `timestamp`: The datetime when the event was executed.
- `prev_timestamp`: The datetime when the previous event of the same customer was executed.
- `new_session`: A flag indicating if it is the start of a new session (0 for not a new session, 1 for the beginning of a new session).
- `time`: The duration of the event (timestamp - prev_timestamp).
- `increment`: The order of new sessions.
- `session_id`: The ID of the session, obtained by concatenating the customer ID with the increment.


## References
- The session definition used in this application follows the guidelines outlined in the following link: [Google Analytics - Sessions and Campaigns](https://support.google.com/analytics/answer/2731565?hl=en#zippy=%2Cin-this-article)

## Additional Information
For additional information or support, please contact Leonardo Melo at melojleo@hotmail.com .You can also visit my [LinkedIn profile](https://www.linkedin.com/in/melojleo) for more details.
