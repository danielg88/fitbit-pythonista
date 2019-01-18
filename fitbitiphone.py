# Fitbit API debug tool https://dev.fitbit.com/apps/oauthinteractivetutorial
# by Daniel Gonçalves
import requests
import base64
import random
import os
import datetime
import pickle
import logging
import clipboard
import notification

#Fill this information
inputauthCode = ''
inputRefreshToken = ''

steps=clipboard.get()
clientID=''
clientSecret=''

baseUrl='https://api.fitbit.com'
dateToday=datetime.datetime.now().strftime("%Y-%m-%d")
authPickle='./Auth.pckl'

def fileUpdate (authCode, irefreshToken):
	global authDict
	f = open(authPickle, 'wb')
	authDict={'access_token':authCode,'refresh_token':irefreshToken}
	pickle.dump(authDict, f)
	f.close()
	return None

def fileRead ():
	global authDict
	f = open(authPickle, 'rb')
	authDict = pickle.load(f)
	f.close()
	return authDict

def refreshToken (authDict):
	authorizationRefresh=clientID+":"+clientSecret
	b64authorizationRefresh = base64.b64encode(authorizationRefresh.encode('utf-8'))
	b64authorizationRefresh="Basic "+b64authorizationRefresh.decode('utf-8')
	headers = {'Authorization': b64authorizationRefresh,'Content-Type': 'application/x-www-form-urlencoded'}
	data = {'grant_type':'refresh_token','refresh_token':authDict['refresh_token']}
	resp = requests.post(baseUrl+'/oauth2/token', headers=headers, params=data)
	if resp.status_code==200:
		fileUpdate (resp.json()['access_token'],resp.json()['refresh_token'])
	return resp		

def updateActivity (authDict):
	global steps
	activityID="90013"
	distanceUnits="Steps"
	headers = {'Authorization': 'Bearer '+authDict['access_token'],'Content-Type': 'application/x-www-form-urlencoded'}
	data = {'activityId':activityID,'startTime': '09:00:00', 'date':dateToday, 'manualCalories':int(steps)/20,'durationMillis':'43200000','distanceUnit':distanceUnits,'distance':steps}
	resp = requests.post(baseUrl+'/1/user/-/activities.json', headers=headers, params=data)
	return resp		
	
def getActivity (authDict):
	headers = {'Authorization': 'Bearer '+authDict['access_token'],'Content-Type': 'application/x-www-form-urlencoded'}
	resp = requests.post(baseUrl+'/1/user/-/activities/date/'+dateToday+'.json', headers=headers)
	return resp		


if os.path.exists(authPickle)==False:
	fileUpdate (inputauthCode, inputRefreshToken)
authDict=fileRead()

if steps.isdigit():
	resp=updateActivity(authDict)
	if 500 <= resp.status_code < 600:
		print ('Server error')
	else:
		if resp.status_code== 201 :
			print ('Steps updated!')
		elif resp.status_code == 401 :
			print ('Update token')
			refreshToken(authDict)
			authDict=fileRead()
			if updateActivity(authDict)==201:
				print ("Steps Updated")
		print('Today steps : '+str(getActivity(authDict).json()['activities'][0]['steps']))
else:
	print ('Clipboard data is not a number')

