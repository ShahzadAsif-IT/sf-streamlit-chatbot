CREATE OR REPLACE TABLE CHAT_MEMORY (
    user_id STRING,
    session_id STRING,
    timestamp TIMESTAMP,
    role STRING,
    message STRING
);