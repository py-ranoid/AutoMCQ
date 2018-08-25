import requests
import os
from string import Template

URL = os.environ.get("DB_URL")

query_string = """
mutation insert_logs {
  insert_logs(
    objects: [
      {
        UID: "$uid",
        email: "$email",
        name:"$name"
        info: "$info",
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
query_template = Template(query_string)

def get_query(user,info):
    return query_template.substitute(uid = user['uid'],
                                     name=user['name'],
                                     info=info,
                                     email=user['mailId'])

def insert(user,log_type,content):
    query = get_query(user,log_type+"::"+content)
    json_query = {
        "operationName":"insert_logs",
        "query":query,
    }
    r = requests.post(URL,json=json_query)
    return r.json()
