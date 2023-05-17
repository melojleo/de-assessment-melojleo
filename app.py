import pandas as pd
from model import eventsdb
from sqlalchemy.orm import declarative_base
from datetime import timedelta
from config import db_hostname, db_port, db_name, db_user, db_password, api_url, time_duration_session
from flask import Flask, jsonify
import psycopg2


app = Flask(__name__)
# Creation of the app that extract the data from data base and return in json file
@app.route('/', methods=['GET'])
def json_app():
    #Connect with the database
    conn = psycopg2.connect(
        host= db_hostname,  
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    
    cursor = conn.cursor()
    
    #Query the first metric from database: "median_visits_before_order"
    cursor.execute("WITH CTE AS (SELECT customer_id, session_id, CASE WHEN COALESCE(((increment) + 1) - LAG(increment + 1) OVER (PARTITION BY customer_id ORDER BY session_id), 0) = 0 THEN 1 ELSE ((increment) + 1) - LAG(increment + 1) OVER (PARTITION BY customer_id ORDER BY session_id) END AS total_sessions_before_order FROM tb_events WHERE event_type = 'placed_order')SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY total_sessions_before_order) AS mediana FROM CTE;")  

    # Return the response from the query
    resultados = cursor.fetchall()
    
    # Extract the metric
    median_session_count = resultados[0][0]
    
    # #Query the first metric from database: "median_session_duration_minutes_before_order"
    cursor.execute("WITH a AS (SELECT customer_id, MIN(timestamp) AS timestamp FROM tb_events WHERE event_type = 'placed_order' GROUP BY customer_id), b AS (SELECT customer_id, timestamp, time FROM tb_events WHERE new_session = 0), c AS (SELECT a.customer_id, SUM(time) AS time FROM a JOIN b ON a.customer_id = b.customer_id AND a.timestamp >= b.timestamp GROUP BY a.customer_id)SELECT (PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY time))/60 AS mediana FROM c;")

    # Return the response from the query
    resultados_duracao = cursor.fetchall()
    
    # Extract the metric
    median_session_duration_minutes = resultados_duracao[0][0]
    
    # Close the connection with the database
    cursor.close()
    conn.close()
    
    # create the dictionary
    response = {
        "median_visits_before_order": median_session_count,
        "median_session_duration_minutes_before_order": median_session_duration_minutes
    }

    # Return the json file
    return jsonify(response)

# Validation if the dataframe is valid to load in the database
def check_if_valid_data(df: pd.DataFrame) -> bool:
    
    # Check if dataframe is empty
    if df.empty:
        print("\nDataframe empty. Finishing execution")
        return False 
    
    # Check for nulls
    if df.event_id.empty:
        raise Exception("\nid is Null or the value is empty")
    
    # Check for nulls
    if df.customer_id.empty:
        raise Exception("\ncustomer_id is Null or the value is empty")
    return True

def load_data(table_name, events_df, session_db, engine_db):
    
    # validate
    if check_if_valid_data(events_df):
        print("\nData valid, proceed to Load stage")
    
    # load data on database
    try:
        events_df.to_sql(table_name, engine_db, index=False, if_exists='replace')
        print ('\nData Loaded on Database')

    except Exception as err:
        print(f"\nFail to load data on database: {err}")

    session_db.commit()
    session_db.close()
    print("\nClose database successfully")
    return session_db

def get_data( session_db, engine_db, url, session_time):
    
    # Declare the columns
    event_id = []
    event_type  = []
    customer_id = []
    timestamp = []
    
    # Define threshold value
    T = timedelta(seconds=session_time*60) 
    
    #Extract the data from api
    try:
        # Read the json file from api url
        df = pd.read_json(url, lines=True)      

        #Extract the data and load the list in the variables
        event_id = df.apply(lambda row: row['id'], axis=1).tolist()
        event_type = df.apply(lambda row: row[1], axis=1).tolist()
        customer_id = df.iloc[:,2].apply(lambda x: x.get('customer-id') if 'customer-id' in x else None)
        timestamp = df.iloc[:,2].apply(lambda x: x.get('timestamp') if 'timestamp' in x else None)
        
        # Create the dictionary with the content of the api data 
        data_dict = {
            "event_id" : event_id,
            "event_type" : event_type ,
            "customer_id" : customer_id,
            "timestamp" : timestamp        
        }
    except Exception as e:
        print (f'Error to get data from APi: {e}')
        exit(1)
            
    # create dataframe to structure data
    events_df = pd.DataFrame(data_dict, columns = ["event_id", "event_type","customer_id","timestamp"])

    # Transform the column "customer_id" into an integer and drop null values
    events_df = events_df.dropna(subset=['customer_id']).sort_values(by=['customer_id','timestamp',"event_id"]).reset_index(drop=True)
    events_df["customer_id"] = events_df["customer_id"].astype(int)
    
    # Turn the column "timestamp" into an datetime
    events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
    
    # add a column containing previous timestamp
    events_df['prev_timestamp'] = events_df.groupby(['customer_id'])['timestamp'].transform(lambda x:x.shift(1))

    #create the new session column
    events_df['new_session'] = ((events_df['timestamp'] - events_df['prev_timestamp'])>=T).astype(int)

    #create the new session column
    events_df['time'] = events_df.apply(lambda row: (row['timestamp'] - row['prev_timestamp']) / pd.Timedelta(seconds=1), axis=1).astype(float)


    # create the session_id
    events_df['increment'] = events_df.groupby("customer_id")['new_session'].cumsum()
    events_df['session_id'] = events_df['customer_id'].astype(str) + '_' + events_df['increment'].astype(str)

    # final result and sort the values
    events_df = events_df.sort_values(['customer_id','timestamp'])

    print ("Data on Pandas Dataframe:\n")
    print(events_df.shape)
    print(events_df.head())
    
    # call the function to load data on database
    load_data('tb_events',events_df, session_db, engine_db)

# Declaration base
Base = declarative_base()

# Make the tb_events table
get_session_db, get_engine = eventsdb.start()

# call the get_data function and load data on database
get_data(get_session_db,
         get_engine,
         api_url,
         time_duration_session)

# run the application and make the server publicly available
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)