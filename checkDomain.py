import requests
import json

base64encodedtoken = 'ZmFqcmkuaGFu_bnlAY29udGVudGZ1bC5jb20vdG9rZW46dDA4VjVSSEVvSHFIejVNZG9GVmVaYUdZd2J1Mnh0M2FsNTduM0ZsbA=='
headers = {'Authorization':'Basic '+base64encodedtoken}
user_url = 'https://contentful.zendesk.com/api/v2/users/'
ticket_url = 'https://contentful.zendesk.com/api/v2/tickets/'

def checkDom():
    showTicketURL = 'https://contentful.zendesk.com/api/v2/tickets/51924.json'
    ticketDetails = requests.get(showTicketURL,headers=headers)
    requesterID = ticketDetails.json()['ticket']['requester_id']
    if (ticketDetails.json()['ticket']['organization_id'] is not None):
        print ('Enterprise')
    else:
        print ('Not Enterprise')
    originalRequester = requesterID
    if(requesterID is not None):
        showUserURL = user_url+str(requesterID)+'.json'
        userDetails = requests.get(showUserURL,headers=headers)
        userEmail = userDetails.json()['user']['email']
        if(userEmail is not None):
            if '@contentful.com' in userEmail:
                print('This ticket is coming from Contentful - ' + userEmail)
                followerURL = ticket_url+str(52147)+'/followers'
                followerDetails = requests.get(followerURL,headers=headers)
                followerCount = followerDetails.json()['count']
                if (followerCount > 0):
                    print ('Follower count : ',followerCount)
                    for followeremail in range (0,followerCount):
                        print ('Follower email : ', str(followerDetails.json()['users'][followeremail]['email']))
                        if('@contentful.com' not in followerDetails.json()['users'][followeremail]['email']):
                            originalRequester = followerDetails.json()['users'][followeremail]['id']
                            print ('update the requester to : '+str(followerDetails.json()['users'][followeremail]['email']))
                            break
                else:
                    originalRequester = requesterID
            else:
                originalRequester = requesterID
    else:
        originalRequester = requesterID
    print (str(originalRequester))

checkDom()
