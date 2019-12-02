from collections import Counter
from jira import JIRA
import json
from datetime import datetime
import utils
import chalk
#import requests
import string
import requests 
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

def followLinks(links):
    print(links)
    for issueLinked in links:
        issue_link = jira.issue_link(issueLinked)
        print("**", issue_link)
        if issue_link.inwardIssue:
            print("      Linked issue '%s'" % issue_link.inwardIssue) 
            issues = jira.search_issues("key="+str(issue_link.inwardIssue))
            for issue in issues:
                followLinks(issue.fields.issuelinks)

with open('config.json', 'r') as infile:
    config = json.load(infile)

host = config["jiraUrl"]
username = config["jiraUsername"]
passwd = getPasswd()

# By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK.
# See
# https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK
# for details.
#options={'server': "https://jira-prod.tcc.etn.com", 'verify':False}
options={'server': host, 'verify':False}
jira = JIRA(options=options, basic_auth=(username, passwd))  # a username/password tuple

# Get the mutable application properties for this server (requires
# jira-system-administrators permission)
#props = jira.application_properties()

# Find all issues reported by the admin
#issues = jira.search_issues("key=OCB-1")
#issues = jira.search_issues("key=PCB-34")
#issues = jira.search_issues("key=WVX-4937")
#issues = jira.search_issues("key=WVX-4851")

status = Counter()

initiative="OCB-1"
epics = jira.search_issues("\"cf[12901]\" = "+initiative)
for epic in epics:
    jql="\"cf[12901]\" = "+str(epic)
    print("EPIC: ",epic, epic.fields.status)
    stories = jira.search_issues(jql)
    for story in stories:
        print("  STORY:",story, chalk.yellow(story.fields.status), story.fields.summary)
        #pprint(story.raw)
        status.update({str(story.fields.status): 1})
        #followLinks(story.fields.issuelinks)

print(initiative, status)
