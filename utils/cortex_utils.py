import json

def call_cortex(session, messages):
    prompt = json.dumps(messages)
    response = "No response"

    try:
        df = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'snowflake-arctic',
                CONCAT('messages:', '{prompt}')
            ) AS response
        """)
        if df.collect() and df.collect()[0]:
            response = df.collect()[0]["RESPONSE"]
    except BaseException as ex:
        response = str(ex)
        
    return response
