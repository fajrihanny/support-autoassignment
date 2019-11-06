import requests
import json
import datetime
import sqlite3
import time

def main():
	# schedule construction - all in UTC timezone
	print 'Starting the program .. '
	startBerlin = datetime.time(6,0,0)
	endBerlin = datetime.time(14,0,0)

	startAuckland = datetime.time(18,0)
	endAuckland = datetime.time(2,0)

	startSaoPaolo = datetime.time(11,0)
	endSaoPaolo = datetime.time(19,0)

	startSanFransisco
	endSanFransisco

	# prepare the basic parameters
	conn = sqlite3.connect('/Users/fajrihanny/Documents/autoassignment/autoassignment.db')
	availableAgentURL = 'https://contentful.zendesk.com/api/v2/search.json?query=type:user agent_ooo:false group:20917813 role:agent'
	url = 'https://contentful.zendesk.com/api/v2/search.json?query=type:ticket status<=pending assignee:none group:Support Group requester:fajri.hanny@contentful.com'
	headers = {'Authorization':'Basic ZmFqcmkuaGFu_bnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA=='}
	headersContentType = {'Authorization':'Basic ZmFqcmkuaGFubnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA==','Content-Type':'application/json'}

	# retrieve last date time assignment for each agent
	print 'Retrieve all the agents .. '
	orderofAgent = []
	c = conn.cursor()
	for row in c.execute("SELECT AGENT_ID FROM AGENT_ASSIGNMENT order by LAST_ASSIGNMENT ASC"):
		orderofAgent.append(row[0])
	print "Order of agent based on last date time assignment: "
	for index in range (0,len(orderofAgent)):
		print(orderofAgent[index])


	# get all agents - make a request to Zendesk
	print 'Retrieve all available agents .. '
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

	print 'Retrieve all the schedules available .. '
	tagSchedule = []
	if (isTimeBetween(startBerlin,endBerlin)):
		tagSchedule.append('Berlin')
	if (isTimeBetween(startSaoPaolo,endSaoPaolo)):
		tagSchedule.append('Sao Paolo')
	if (isTimeBetween(startAuckland,endAuckland)):
		tagSchedule.append('Auckland')

	print "Available timezone: " 
	for index in range (0,len(tagSchedule)):
		print(tagSchedule[index])

	# get available agent's ID based on the current time
	print 'Retrieve all agents availabled for the time zone(s) .. '
	finalAvailableAgent = []
	for agent in range (0,numberofAgent): # number of agent = 4
		agentTimezone = str((agentDataDump['results'][agent]['time_zone'])) # get agent's timezone
		agentName = str(agentDataDump['results'][agent]['name']) # get agent's name
		for index in range(0,len(tagSchedule)): # Auckland = 1
			if(str(tagSchedule[index]) == agentTimezone):
				finalAvailableAgent.append(agentDataDump['results'][agent]['id'])
	
	print "Available agent based on timezone: " 
	for index in range (0,len(finalAvailableAgent)):
		print(finalAvailableAgent[index])

	# check which agent needs to be assigned based on the last assignment time based
	print 'Getting the final order of the agent .. '
	finalAgentOrder = []
	for agentOrder in range (0,len(orderofAgent)):
		if orderofAgent[agentOrder] in finalAvailableAgent:
			finalAgentOrder.append(orderofAgent[agentOrder])
	print "Final Agent Order: " 
	for index in range (0,len(finalAgentOrder)):
		print(finalAgentOrder[index])

	# Get all the unassigned tickets and assign them to the available agents
	print 'Getting all the unassigned tickets .. '
	response = requests.get(url,headers=headers)
	newTicket = response.json()
	newTicketString = json.dumps(newTicket)
	newTicketDump = json.loads(newTicketString)
	numberOfTickets = len(newTicketDump['results'])

	# assigning ticket to available agent
	lastPosition = 0
	if(numberOfTickets>0):
		print 'Number of new unassigned tickets: ' + str(numberOfTickets) + ' tickets' 
		print 'Assigning tickets to agents .. '
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
		print 'No new tickets to assign'

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




