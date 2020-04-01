# start of new autoassignment.py

from datetime import datetime
from datetime import date
from datetime import timedelta
import time
from pytz import timezone
import json
import requests
import sqlite3
from workalendar.europe import Germany
from workalendar.oceania import NewZealand
from workalendar.usa import California

# ALL CONSTANTS GO HERE 

# zendesk basic url and queries
basic_url = 'https://contentful.zendesk.com/api/v2/search.json?query='
ticket_url = 'https://contentful.zendesk.com/api/v2/tickets/'
user_url = 'https://contentful.zendesk.com/api/v2/users/'
unassignedTicketsQuery = 'type:ticket status<=pending assignee:none group:'

# token and headers
base64encodedtoken = 'ZmFqcmkuaGFu_bnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA=='
headers = {'Authorization':'Basic '+base64encodedtoken}
headersWithContentType = {'Authorization':'Basic '+base64encodedtoken,'Content-Type':'application/json'}

# zendesk groups
group_id_ops = '360000168347'
group_id_support = '20917813'
ops_switchoff = False
support_switchoff = False

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
        print('Program starts : '+datetime.now().strftime(("%Y-%m-%d %H:%M:%S")))
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

    def checkDomain(ticketToCheckID):
        showTicketURL = ticket_url+str(ticketToCheckID)+'.json'
        ticketDetails = requests.get(showTicketURL,headers=headers)
        requesterID = ticketDetails.json()['ticket']['requester_id']
        showUserURL = user_url+str(requesterID)+'.json'
        userDetails = requests.get(showUserURL,headers=headers)
        userEmail = userDetails.json()['user']['email']
        if '@contentful.com' in userEmail:
            followerURL = ticket_url+str(ticketToCheckID)+'/followers'
            followerDetails = requests.get(followerURL,headers=headers)
            originalRequester = followerDetails.json()['users'][0]['id']
        else:
            originalRequester = requesterID
        return originalRequester
    
    # getting current time zone
    def getCurrentTimeZone():
        timeBER = datetime.now(timezone('Europe/Berlin'))
        timeSF = datetime.now(timezone('America/Los_Angeles'))
        timeNZ = datetime.now(timezone('Pacific/Auckland'))
        tz_BER = timeBER.hour
        calBerlin = Germany()
        calSF = California()
        calNZ = NewZealand()
        isBerlinWeekday = datetime.isoweekday(timeBER)
        print ('Berlin time: ', tz_BER)
        tz_SF = timeSF.hour
        isSFWeekday = datetime.isoweekday(timeSF)
        print ('San Fransisco time : ', tz_SF)
        tz_NZ = timeNZ.hour
        isNZWeekday = datetime.isoweekday(timeNZ)
        print ('New Zealand time : ', tz_NZ)
        if (tz_BER >= startTime and tz_BER <= endTime) and (isBerlinWeekday < 6) and not (calBerlin.is_holiday(date(timeBER.year,timeBER.month,timeBER.day))):
            availableTimeZone.append('berlin')
        if (tz_NZ >= startTime and tz_NZ <= endTime) and (isNZWeekday < 6) and not (calSF.is_holiday(date(timeSF.year,timeSF.month,timeSF.day))):
            availableTimeZone.append('nz')
        if (tz_SF >= startTime and tz_SF <= endTime) and (isSFWeekday < 6) and not (calNZ.is_holiday(date(timeNZ.year,timeNZ.month,timeNZ.day))):
            availableTimeZone.append('sf')
        print ('Working timezone: ',availableTimeZone)

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
        print('Available agents in : '+str(timeZoneToCheck)+' are '+str(availableAgents))
        return availableAgents
    
    # searching last assignment of the agents
    def getLastAssignment(agentType):
        if agentType == 'support':
            query = "select agent_id from autoassignment where agent_type='support' order by last_at asc"
        else:
            query = "select agent_id from autoassignment where agent_type='ops' order by last_at asc"
        # conn1 = sqlite3.connect('/Users/fajrihanny/Documents/Projects/support-autoassignment/autoassignment.db')
        conn1 = sqlite3.connect('./autoassignment.db')
        orderofAgent = []
        c = conn1.cursor()
        for row in c.execute(query):
            orderofAgent.append(row[0])
        print('Order of '+str(agentType)+' agent : '+str(orderofAgent))
        conn1.close()
        return orderofAgent
    
    # getting the final order of the agents
    def getOrderAgent(order,agents):
        finalAgentOrder = []
        for agentOrder in range (0,len(order)):
            if order[agentOrder] in agents:
                finalAgentOrder.append(order[agentOrder])
        return finalAgentOrder
    
    # assigning tickets to agent and update the ticket
    def assignTickets(finalOrder,finalTickets):
        # conn2 = sqlite3.connect('/Users/fajrihanny/Documents/Projects/support-autoassignment/autoassignment.db')
        conn2 = sqlite3.connect('./autoassignment.db')
        d = conn2.cursor()
        for ticketID in range(0,len(finalTickets)):
            getAssignedTime = int(datetime.utcnow().timestamp())
            agentToWorkWith = ticketID%len(finalOrder)
            updateTicketURL = ticket_url+str(finalTickets[ticketID])+'.json'
            newRequester = checkDomain(finalTickets[ticketID])
            location = getLocation(finalTickets[ticketID])
            if (location == 'None'):
                ticketComment = 'This ticket has been auto-assigned'
            else:
                ticketComment = 'This ticket coming from ' + location + ' and has been auto-assigned'
            print('Ticket '+str(finalTickets[ticketID])+ ' coming from '+ location + ' is assigned to '+str(finalOrder[agentToWorkWith])+ ' at '+str(getAssignedTime))
            payloadTicket = {'ticket': {'comment': {'body':ticketComment,'public':'false','author_id':'25264784308'},'assignee_id':finalOrder[agentToWorkWith],'requester_id':newRequester}}
            payloadJson = json.dumps(payloadTicket)
            requests.put(updateTicketURL,headers=headersWithContentType, data=payloadJson)
            d.execute("update autoassignment SET last_at = ? where agent_id = ?", (getAssignedTime,finalOrder[agentToWorkWith]))
            conn2.commit()
        conn2.close()

    def getLocation(ticketID):
        ticketLocation = 'None'
        auditTicketURL = ticket_url+str(ticketID)+'/audits.json'
        ticketAudit = requests.get(auditTicketURL,headers=headers)
        system = ticketAudit.json()['audits'][0]['metadata']['system']
        print (len(system))
        if ('location' in system):
            ticketLocation = str(ticketAudit.json()['audits'][0]['metadata']['system']['location'])
        return ticketLocation

	# MAIN LOGIC IS HERE # 

    # 1. Get the tickets to distribute from both groups - Ops and Support Group.
    getUnassignedTickets()
    if (len(supportTicket)>0 or len(opsTicket)>0):
		# 2. Get the current time zone(s)
        getCurrentTimeZone()
        if (len(availableTimeZone)>0):
            print ('Getting available agents..')
            # 3. Get the available agents based (param:available time zone from no 2)
            if (len(supportTicket)>0 and support_switchoff ==  False):
                orderSupport = []
                availSupport = []
                finalSupportOrder = []
                print ('Starting distribution for Support tickets')
                availSupport = getAvailableAgents(availableTimeZone,'support')
                if (len(availSupport)>0):
                    # print ('Available agents in : '+availableTimeZone+' , '+availSupport)
                    # 4. Get the last assignments of the agent and order them 
                    orderSupport = getLastAssignment('support')
                    # 5. Get the final order
                    finalSupportOrder = getOrderAgent(orderSupport,availSupport)
                    # print ('Final order of the agent : '+finalSupportOrder)
                    # 6. Assign the ticket to the agents, save the assignment time, and update the ticket with message from bot
                    assignTickets(finalSupportOrder,supportTicket)
                else:
                    print ('No available support agents during this timezone')
                # 7. Post update to Slack channel with the name of the agent
            else:
                print ('No unassigned support tickets to distribute')
            if (len(opsTicket)>0 and ops_switchoff == False):
                orderOps = []
                availOps = []
                finalOpsOrder = []
                print ('Starting distribution for Ops tickets')
                availOps = getAvailableAgents(availableTimeZone,'ops')
                if (len(availOps)>0):
                    # 4. Get the last assignments of the agent and order them
                    orderOps = getLastAssignment('ops')  
                    # 5. Get the final order 
                    finalOpsOrder = getOrderAgent(orderOps,availOps)      
                    # 6. Assign the ticket to the agents, save the assignment time, and update the ticket with message from bot
                    assignTickets(finalOpsOrder,opsTicket)
                    # 7. Update the ticket and post update to Slack channel with the name of the agent
                else:
                    print ('No available ops agents during this timezone')
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