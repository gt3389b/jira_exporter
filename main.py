# Based off of:
#    https://github.com/cbonitz/jira-influx

import json
from datetime import datetime
import utils
import string
import requests 
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def checkError(err): 
    if err != None:
        print(err)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def getPasswd():
    try:
        with open('.session', 'r') as infile:
            data = json.load(infile)
    except:
        data = {}
        random.seed()
        data['key'] = id_generator()
        passwd = getpass.getpass("JIRA Password:");
        data['secret'] = utils.encode(data['key'], passwd).decode("utf-8")
        with open('.session', 'w') as outfile:
            json.dump(data, outfile)

    return utils.decode(data['key'], data['secret'].encode("utf-8"))

def runJqlQuery(config, jql):
    host = config["jiraUrl"]
    username = config["jiraUsername"]
    passwd = getPasswd()

    payload = {}
    #payload['fields'] = 'key, childissue, subtasks, labels, parent.id, status'
    payload['fields'] = 'editmeta'
    payload['jql'] = jql
    params = "&".join("%s=%s" % (k,v) for k,v in payload.items())
    # 'format=json&key=site:dummy+type:example+group:wheel'

    response = requests.get(host+"/rest/api/latest/search?", params=params, auth=(username, passwd), verify=False)
    pprint(json.loads(response.text))

    #response2 = requests.get(host+"/rest/api/latest/issue/OCB-1", auth=(username, passwd), verify=False)
    #pprint(json.loads(response2.text))

    #checkError(err)

    m = json.loads(response.text)

    #extract the interesting data
    return int(m["total"])

# addPoint adds a point with tags to a BatchPoints object for sending them later
def addPoint(batchPoints, timeOfQuery, tags, count, durationMilliseconds):
    # put tags from config into the right type of map
    fields = { "count": count,
            "durationMilliseconds": durationMilliseconds}
    # for now, the measurement name is fixed
    #pt, err := client.NewPoint("issue_count", tags, fields, timeOfQuery)
    print("Prepared for sending: %s: %d issues (in %d ms)" % (tags, count, durationMilliseconds))
    #batchPoints.AddPoint(pt)

def main():
    with open('config.json', 'r') as infile:
        config = json.load(infile)

    queries = config["queries"]

    # create influx client and batch points (only one send operation at the end)
    #influxClient := createInfluxClient(config)
    #batchPoints= createBatchPoints(config, influxClient)
    batchPoints={}
    #durationBetweenJiraQueries := time.Duration(100) * time.Millisecond

    #if config["jiraPauseMilliseconds"]:
    #    durationBetweenJiraQueries = time.Duration(int(val.(float64))) * time.Millisecond

    for q in queries: 
        jql = q["jql"]

        #timeBeforeQuery := time.Now()
        timeBeforeQuery = datetime.now()
        count = runJqlQuery(config, jql)
        timeAfterQuery = datetime.now()

        #queryDurationMilliseconds = (timeAfterQuery-timeBeforeQuery).microseconds / 1000
        delta = timeAfterQuery-timeBeforeQuery
        queryDurationMilliseconds = int(delta.total_seconds() * 1000)

        #// create influx point and save for later
        addPoint(batchPoints, timeBeforeQuery, q["tags"], count, queryDurationMilliseconds)
        #time.Sleep(durationBetweenJiraQueries)

    #fmt.Println("Writing data to InfluxDB")
    #// write the points
    #influxErr := influxClient.Write(batchPoints)
    #checkError(influxErr)

if __name__ == "__main__":
    main()
