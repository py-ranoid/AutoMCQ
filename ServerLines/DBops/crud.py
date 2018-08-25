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

query_rev_string = """
mutation insert_reviews {
  insert_reviews(
    objects: [
      {
        ans: $ans,
        ques: $ques,
        score: $score,
        name: "$name",
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
query_rev_template = Template(query_rev_string)

def get_query(user,info):
    return query_template.substitute(uid = user['uid'],
                                     name=user['name'],
                                     info=info,
                                     email=user['mailId'])

def get_query_rev(user,ans,ques,score):
    return query_rev_template.substitute(ans = ans,
                                     name=user['name'],
                                     ques=ques,
                                     score=score)

def insert(user,log_type,content):
    query = get_query(user,log_type+"::"+content)
    json_query = {
        "operationName":"insert_logs",
        "query":query,
    }
    r = requests.post(URL,json=json_query)
    return r.json()

def insert_rev(user,ans,ques,score):
    query = get_query_rev(user,ans,ques,score)
    json_query = {
        "operationName":"insert_reviews",
        "query":query,
    }
    r = requests.post(URL,json=json_query)
    return r.json()
