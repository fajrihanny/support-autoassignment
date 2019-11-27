# start of new autoassignment.py

from datetime import datetime
from datetime import timedelta
import time
from pytz import timezone
import json
import requests
import sqlite3

# ALL CONSTANTS GO HERE 

# zendesk basic url and queries
basic_url = 'https://contentful.zendesk.com/api/v2/search.json?query='
ticket_url = 'https://contentful.zendesk.com/api/v2/tickets/'
unassignedTicketsQuery = 'type:ticket status<=pending assignee:none group:'

# token and headers
base64encodedtoken = 'ZmFqcmkuaGFu_bnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA=='
headers = {'Authorization':'Basic '+base64encodedtoken}
headersWithContentType = {'Authorization':'Basic '+base64encodedtoken,'Content-Type':'application/json'}

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

	# ALL METHODS GO HERE #

    # get unassigned tickets
    def getUnassignedTickets():
        unassignedTicketsSupportresponse = requests.get(basic_url+unassignedTicketsQuery+group_id_support,headers=headers)
        unassignedTicketsOpsresponse = requests.get(basic_url+unassignedTicketsQuery+group_id_ops,headers=headers)
        supportDump = json.loads(json.dumps(unassignedTicketsSupportresponse.json()))
        opsDump = json.loads(json.dumps(unassignedTicketsOpsresponse.json()))
        if (len(supportDump['results']) > 0):
            print (str(len(supportDump['results']))+' support tickets are found')
            for ticket in range (0,len(supportDump['results'])):
                supportTicket.append(supportDump['results'][ticket]['id'])
        if (len(opsDump['results']) > 0):
            print (str(len(opsDump['results']))+' ops tickets are found')
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
        agentSearch = 'type:user agent_ooo:false '
        for tz in range (0,len(timeZoneToCheck)):
            agentSearch = agentSearch + 'tags:' + agentType + '_' + timeZoneToCheck[tz] + ' '
        agentSearchURL = basic_url+agentSearch
        getAgents = requests.get(agentSearchURL,headers=headers)
        agentDump = json.loads(json.dumps(getAgents.json()))
        if (agentDump['count']>0):
            for agentIndex in range(0,agentDump['count']):
                availableAgents.append(agentDump['results'][agentIndex]['id'])
        return availableAgents
    
    # searching last assignment of the agents
    def getLastAssignment(agentType):
        if agentType == 'support':
            query = "select agent_id from autoassignment where agent_type='support' order by last_at asc"
        else:
            query = "select agent_id from autoassignment where agent_type='ops' order by last_at asc"
        conn1 = sqlite3.connect('/Users/fajrihanny/Documents/Projects/support-autoassignment/autoassignment.db')
        orderofAgent = []
        c = conn1.cursor()
        for row in c.execute(query):
            orderofAgent.append(row[0])
        conn1.close()
        return orderofAgent
    
    # getting the final order of the agents
    def getOrderAgent(agents,order):
        finalAgentOrder = []
        for agentOrder in range (0,len(order)):
            if order[agentOrder] in agents:
                finalAgentOrder.append(order[agentOrder])
        return finalAgentOrder
    
    # assigning tickets to agent and update the ticket
    def assignTickets(finalOrder,finalTickets):
        conn2 = sqlite3.connect('/Users/fajrihanny/Documents/Projects/support-autoassignment/autoassignment.db')
        d = conn2.cursor()
        for ticketID in range(0,len(finalTickets)):
            updateTicketURL = ticket_url+str(finalTickets[ticketID])+'.json'
            agentToWorkWith = str(finalOrder[(ticketID%len(finalOrder))])
            payloadTicket = {'ticket': {'comment': {'body':'This ticket has been auto-assigned','public':'false','author_id':'25264784308'}, 'assignee_id':agentToWorkWith}}
            payloadJson = json.dumps(payloadTicket)
            requests.put(updateTicketURL,headers=headersWithContentType, data=payloadJson)
            getAssignedTime = int(datetime.utcnow().timestamp())
            d.execute("update autoassignment SET last_at = ? where agent_id = ?", (getAssignedTime,agentToWorkWith))
            conn2.commit()
        conn2.close()

    # posting updates on Slack (later development)

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
                orderSupport = []
                availSupport = []
                finalSupportOrder = []
                print ('Starting distribution for Support tickets')
                availSupport = getAvailableAgents(availableTimeZone,'support')
                # 4. Get the last assignments of the agent and order them 
                orderSupport = getLastAssignment('support')
                # 5. Get the final order
                finalSupportOrder = getOrderAgent(orderSupport,availSupport)
                # 6. Assign the ticket to the agents, save the assignment time, and update the ticket with message from bot
                assignTickets(finalSupportOrder,supportTicket)
                # 7. Post update to Slack channel with the name of the agent
            else:
                print ('No unassigned support tickets to distribute')
            if (len(opsTicket)>0):
                orderOps = []
                availOps = []
                finalOpsOrder = []
                print ('Starting distribution for Ops tickets')
                availOps = getAvailableAgents(availableTimeZone,'ops')
                # 4. Get the last assignments of the agent and order them
                orderOps = getLastAssignment('ops')  
                # 5. Get the final order 
                finalOpsOrder = getOrderAgent(orderOps,availOps)      
                # 6. Assign the ticket to the agents, save the assignment time, and update the ticket with message from bot
                assignTickets(finalOpsOrder,opsTicket)
                # 7. Update the ticket and post update to Slack channel with the name of the agent
            else:
                print ('No unassigned ops tickets to distribute')
        else:
            print ('No active time zone')
    else:
        print ('No unassigned tickets to distribute')

while 1:
    if __name__== "__main__":
        main()

	# run the program every 10 minutes
	# adding comment from code-refactoring branch
    dt = datetime.now() + timedelta(minutes=10)
    # dt = datetime.now() + datetime.timedelta(minutes=10)
    while datetime.now() < dt:
        time.sleep(1)
