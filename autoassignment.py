import requests
import json
import datetime
import sqlite3
import time

def main():
	# schedule construction - all in UTC timezone converted to 8 AM to 5 PM local time
	print ('Starting the program.. ')
	startBerlin = datetime.time(7,0,0)
	endBerlin = datetime.time(16,0,0)

	startAuckland = datetime.time(19,0,0)
	endAuckland = datetime.time(4,0,0)

	startSanFransisco = datetime.time(16,0,0)
	endSanFransisco = datetime.time(1,0,0)

	# prepare the basic parameters
	conn = sqlite3.connect('/Users/fajrihanny/Documents/autoassignment/autoassignment.db')
	availableAgentURL = 'https://contentful.zendesk.com/api/v2/search.json?query=type:user agent_ooo:false group:20917813 role:agent'
	url = 'https://contentful.zendesk.com/api/v2/search.json?query=type:ticket status<=pending assignee:none group:Support Group'
	headers = {'Authorization':'Basic ZmFqcmkuaGFu_bnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA=='}
	headersContentType = {'Authorization':'Basic ZmFqcmkuaGFubnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA==','Content-Type':'application/json'}

	# retrieve last date time assignment for each agent
	print ('Retrieve all the agents .. ')
	orderofAgent = []
	c = conn.cursor()
	for row in c.execute("SELECT AGENT_ID FROM AGENT_ASSIGNMENT order by LAST_ASSIGNMENT ASC"):
		orderofAgent.append(row[0])
	print ('Order of agent based on last date time assignment: ')
	for index in range (0,len(orderofAgent)):
		print(orderofAgent[index])


	# get all agents - make a request to Zendesk
	print ('Retrieve all available agents .. ')
	availableAgents = requests.get(availableAgentURL,headers=headers)
	agentData = availableAgents.json()
	agentDataString = json.dumps(agentData)
	agentDataDump = json.loads(agentDataString)
	numberofAgent = len(agentDataDump['results'])

	# get current time
	currentTime = datetime.datetime.utcnow().time()

	# get the current timezone of agent that can be assigned tickets
	def isTimeBetween(startTime,endTime):
		if startTime < endTime:
			return currentTime >= startTime and currentTime <= endTime
		else:
			return currentTime >= startTime or currentTime <= endTime

	print ('Retrieve all the schedules available .. ')
	tagSchedule = []
	if (isTimeBetween(startBerlin,endBerlin)):
		tagSchedule.append('Berlin')
	if (isTimeBetween(startSaoPaolo,endSaoPaolo)):
		tagSchedule.append('Sao Paolo')
	if (isTimeBetween(startAuckland,endAuckland)):
		tagSchedule.append('Auckland')

	print ('Available timezone: ')
	for index in range (0,len(tagSchedule)):
		print(tagSchedule[index])

	# get available agent's ID based on the current time
	print ('Retrieve all agents availabled for the time zone(s) .. ')
	finalAvailableAgent = []
	for agent in range (0,numberofAgent): # number of agent = 4
		agentTimezone = str((agentDataDump['results'][agent]['time_zone'])) # get agent's timezone
		agentName = str(agentDataDump['results'][agent]['name']) # get agent's name
		for index in range(0,len(tagSchedule)): # Auckland = 1
			if(str(tagSchedule[index]) == agentTimezone):
				finalAvailableAgent.append(agentDataDump['results'][agent]['id'])
	
	print ('Available agent based on timezone: ')
	for index in range (0,len(finalAvailableAgent)):
		print(finalAvailableAgent[index])

	# check which agent needs to be assigned based on the last assignment time based
	print ('Getting the final order of the agent .. ')
	finalAgentOrder = []
	for agentOrder in range (0,len(orderofAgent)):
		if orderofAgent[agentOrder] in finalAvailableAgent:
			finalAgentOrder.append(orderofAgent[agentOrder])
	print ('Final Agent Order: ')
	for index in range (0,len(finalAgentOrder)):
		print(finalAgentOrder[index])

	# Get all the unassigned tickets and assign them to the available agents
	print ('Getting all the unassigned tickets .. ')
	response = requests.get(url,headers=headers)
	newTicket = response.json()
	newTicketString = json.dumps(newTicket)
	newTicketDump = json.loads(newTicketString)
	numberOfTickets = len(newTicketDump['results'])

	# assigning ticket to available agent
	lastPosition = 0
	if(numberOfTickets>0):
		print ('Number of new unassigned tickets: ') + str(numberOfTickets) + (' tickets' )
		print ('Assigning tickets to agents .. ')
		for ticket in range (0,numberOfTickets):
			updateTicketURL = 'https://contentful.zendesk.com/api/v2/tickets/'+str(newTicketDump['results'][ticket]['id'])+'.json'
		 	for agentIndex in range(lastPosition,len(finalAgentOrder)):
				 assignedAgent = str(finalAgentOrder[agentIndex])
				 payload = {'ticket': {'status':'open', 'comment': {'body':'This ticket is being auto assigned','public':'false','author_id':'25264784308'}, 'assignee_id':assignedAgent}}
				 payloadJson = json.dumps(payload)
				 updateTicket = requests.put(updateTicketURL,headers=headersContentType, data=payloadJson)
				 getCurrentTime = datetime.datetime.utcnow()
				 assignmentTime = getCurrentTime.strftime('%s')
				 assignmentTimeinInt = int(assignmentTime)
				 c.execute("UPDATE AGENT_ASSIGNMENT SET LAST_ASSIGNMENT = ? WHERE AGENT_ID = ?", (assignmentTimeinInt,assignedAgent))
				 conn.commit()
				 if(agentIndex == len(finalAgentOrder)-1):
					 lastPosition = 0
				 else:
					 lastPosition = agent_to_assign + 1
				 break
	else:
		print ('No new tickets to assign')

	conn.close()
	return;

while 1:

	if __name__== "__main__":
		main()

	# run the program every 5 minutes
	# adding comment from code-refactoring branch
	dt = datetime.datetime.now() + datetime.timedelta(minutes=5)

	while datetime.datetime.now() < dt:
		time.sleep(1)




# start of time.py


from datetime import datetime
from pytz import timezone
import json
import requests

# ALL CONSTANTS GO HERE 

# zendesk basic url and queries
basic_url = 'https://contentful.zendesk.com/api/v2/search.json?query='
unassignedTicketsQuery = 'type:ticket status<=pending assignee:none group:'

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
            availableTimeZone.append('auto_assign_berlin')
        if (tz_NZ >= startTime and tz_NZ <= endTime):
            availableTimeZone.append('auto_assign_nz')
        if (tz_SF >= startTime and tz_SF <= endTime):
            availableTimeZone.append('auto_assign_sf')

    
    
    # get available agents based on current time zone
    
    # Logic to follow
    # 1. Get the tickets to distribute from both groups - Ops and Support Group.
    getUnassignedTickets()
    if (len(supportTicket)>0):
        print ('Starting distribution for Ops Tickets')
        # 2. Get the current available time zone for Ops Agent
        getCurrentTimeZone()
        if (len(availableTimeZone)>0):
        # 3. Get the available agents based (param:available time zone from no 2)
        getAvailableAgents(availableTimeZone)
    else:
        print('No tickets to assign')   
    # 4. Get the last assignments of the agent and order them (param: agents available from no 3)
    # 5. Assign the ticket to the agents (param: ordered agent from no 4) and save the assignment time along with agent ID

import json
import requests

basic_url = 'https://contentful.zendesk.com/api/v2/search.json?query='
group_id_ops = '360000168347'
group_id_support = '20917813'

unassignedTicketsQuery = 'type:ticket status<=pending assignee:none group:'
base64encodedtoken = 'ZmFqcmkuaGFu_bnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA=='
headers = {'Authorization':'Basic '+base64encodedtoken}

unassignedTicketsSupportresponse = requests.get(basic_url+unassignedTicketsQuery+group_id_support,headers=headers)
unassignedTicketsOpsresponse = requests.get(basic_url+unassignedTicketsQuery+group_id_ops,headers=headers)

supportDump = json.loads(json.dumps(unassignedTicketsSupportresponse.json()))
opsDump = json.loads(json.dumps(unassignedTicketsOpsresponse.json()))

supportTicket = []
opsTicket = []

if (len(supportDump['results']) > 0) :
    for ticket in range (0,len(supportDump['results'])):
        supportTicket.append(supportDump['results'][ticket]['id'])
if (len(opsDump['results']) > 0) :
    for ticket in range (0,len(opsDump['results'])):
        opsTicket.append(opsDump['results'][ticket]['id'])

print (supportTicket)
print (opsTicket)


# url = 'https://contentful.zendesk.com/api/v2/search.json?query=type:ticket status<=pending assignee:none group:Support Group'
    

if __name__== "__main__":
		main()
