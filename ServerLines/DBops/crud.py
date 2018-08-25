import requests
import os

URL = os.environ.get("DB_URL")

query_template = """
mutation insert_logs {
  insert_logs(
    objects: [
      {
        UID: XXX,
        info: "YYY",
      }
    ]
  ) {
    returning {
      key
      time
    }
  }
}
""".strip()

def get_query(uid,info):
    return query_template.replace("XXX",uid).replace("YYY",info)

def insert(uid,log_type,content):
    query = get_query(uid,log_type+"::"+content)
    json_query = {
        "operationName":"insert_logs",
        "query":query,
    }
    r = requests.post(URL,json=json_query)
    return r.json()
