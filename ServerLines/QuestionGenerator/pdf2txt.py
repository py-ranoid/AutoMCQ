import requests
from requests.auth import HTTPBasicAuth

api_key = 'xxxxx'
endpoint = "https://sandbox.zamzar.com/v1/jobs"

def create_job(source_file = "/tmp/abc.pdf",target_format = "txt"):
    file_content = {'source_file': open(source_file, 'rb')}
    data_content = {'target_format': target_format}
    res = requests.post(endpoint, data=data_content, files=file_content, auth=HTTPBasicAuth(api_key, ''))
    resp_json = res.json()
    print (resp_json)
    return resp_json['id']

def get_job_status(job_id = 15):    
    endpoint = "https://sandbox.zamzar.com/v1/jobs/{}".format(job_id)

    response = requests.get(endpoint, auth=HTTPBasicAuth(api_key, ''))
    resp_json = response.json()
    print (resp_json)
    print ("Target File ID :",resp_json["target_files"]["id"])

def get_dest(file_id = 3):    
    local_filename = '/tmp/portrait.txt'
    endpoint = "https://sandbox.zamzar.com/v1/files/{}/content".format(file_id)
    response = requests.get(endpoint, stream=True, auth=HTTPBasicAuth(api_key, ''))

    try:
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
            print ("File downloaded")

    except IOError:
        print ("IO Error")