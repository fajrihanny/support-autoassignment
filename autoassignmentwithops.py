# start of new autoassignment.py


from datetime import datetime
from pytz import timezone
import json
import requests
import sqlite3


# ALL CONSTANTS GO HERE 

# database initiation
conn = sqlite3.connect('/Users/fajrihanny/Documents/autoassignment/autoassignment.db')

# zendesk basic url and queries
basic_url = 'https://contentful.zendesk.com/api/v2/search.json?query='
unassignedTicketsQuery = 'type:ticket status<=pending assignee:none group:'
agentSearch = 'type:user agent_ooo:false '

# token and headers
base64encodedtoken = 'ZmFqcmkuaGFu_bnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA=='
headers = {'Authorization':'Basic '+base64encodedtoken}

# zendesk groups
group_id_ops = '360000168347'
group_id_support = '20917813'

# variables for timezone
startTime = 8
endTime = 17

def main():
    availableTimeZone = []
    supportTicket = []
    opsTicket = []
    opsAgent = []
    supportAgent = []

	# ALL METHODS GO HERE #

    # get unassigned tickets
    def getUnassignedTickets():
        unassignedTicketsSupportresponse = requests.get(basic_url+unassignedTicketsQuery+group_id_support,headers=headers)
        unassignedTicketsOpsresponse = requests.get(basic_url+unassignedTicketsQuery+group_id_ops,headers=headers)
        supportDump = json.loads(json.dumps(unassignedTicketsSupportresponse.json()))
        opsDump = json.loads(json.dumps(unassignedTicketsOpsresponse.json()))
        if (len(supportDump['results']) > 0) :
            for ticket in range (0,len(supportDump['results'])):
                supportTicket.append(supportDump['results'][ticket]['id'])
        if (len(opsDump['results']) > 0) :
            for ticket in range (0,len(opsDump['results'])):
                opsTicket.append(opsDump['results'][ticket]['id'])
    
    # getting current time zone
    def getCurrentTimeZone():
        tz_BER = datetime.now(timezone('Europe/Berlin')).hour
        tz_SF = datetime.now(timezone('America/Los_Angeles')).hour
        tz_NZ = datetime.now(timezone('Pacific/Auckland')).hour
        if (tz_BER >= startTime and tz_BER <= endTime):
            availableTimeZone.append('berlin')
        if (tz_NZ >= startTime and tz_NZ <= endTime):
            availableTimeZone.append('nz')
        if (tz_SF >= startTime and tz_SF <= endTime):
            availableTimeZone.append('sf')

    # searching available agents based on timezones using user tags
    def getAvailableAgents(timeZoneToCheck,agentType):
        availableAgents = []
        for tz in range (0,len(timeZoneToCheck)):
            agentSearch = agentSearch + 'tags:' + agentType + '_' + timeZoneToCheck[tz] + ' '
        agentSearchURL = basic_url+agentSearch
        getAgents = requests.get(agentSearchURL,headers=headers)
        agentDump = json.loads(json.dumps(getAgents.json()))
        if (agentDump['count']>0):
            for agentIndex in range(0,agentDump['count']):
                availableAgents.append(agentDump['result'][agentIndex]['id'])
        return availableAgents
    
	# MAIN LOGIC IS HERE # 

    # 1. Get the tickets to distribute from both groups - Ops and Support Group.
    getUnassignedTickets()
    if (len(supportTicket)>0 or len(opsTicket)>0):
		# 2. Get the current time zone(s)
		getCurrentTimeZone()
		if (len(availableTimeZone)>0):
			print ('Getting available agents..')
            # 3. Get the available agents based (param:available time zone from no 2)
			if (len(supportTicket)>0):
				print ('Starting distribution for Support tickets')
                getAvailableAgents(availableTimeZone,'support')
                # 4. Get the last assignments of the agent and order them (param: agents available from no 3)
                # 5. Assign the ticket to the agents (param: ordered agent from no 4) and save the assignment time along with agent ID
                # 6. Update the ticket and post update to Slack channel with the name of the agent
			else:
				print ('No unassigned support tickets to distribute')
			if (len(opsTicket)>0):
				print ('Starting distribution for Ops tickets')
                getAvailableAgents(availableTimeZone,'ops')
                # 4. Get the last assignments of the agent and order them (param: agents available from no 3)
                # 5. Assign the ticket to the agents (param: ordered agent from no 4) and save the assignment time along with agent ID
                # 6. Update the ticket and post update to Slack channel with the name of the agent
			else:
				print ('No unassigned ops tickets to distribute')
		else:
			print ('No active time zone')
	else:
		print ('No unassigned tickets to distribute')




while 1:

	if __name__== "__main__":
		main()

	# run the program every 5 minutes
	# adding comment from code-refactoring branch
	dt = datetime.datetime.now() + datetime.timedelta(minutes=5)

	while datetime.datetime.now() < dt:
		time.sleep(1)
