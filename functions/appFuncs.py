import numpy, sys
import pymysql as mdb
from scipy.spatial import distance
from data.StaticData import championDict
import dill
global dblogin, dbpw, riot_api_key,database
with open('crds.pickle','rb') as f:
    dblogin, dbpw,riot_api_key, database = dill.load(f)
#from treeinterpreter import treeinterpreter as ti

#def rf_frame_feature_importance(sample1,sample2,featureLabels,randomforest,winner):
##  Determines the importance of features for classifying teams as winning or losing
##  sample1 - features of team1
##  sample2 - features of team2
##  feature labels - label names for features
##  randomforest - sklearn random forest object
##  winner - team that won (1 or 2)
#    prediction1, bias1, contributions1 = ti.predict(randomforest,numpy.array([sample1]))
#    prediction2, bias2, contributions2 = ti.predict(randomforest,numpy.array([sample2]))
#    if winner == 1:
#        featureDiff = abs(contributions1[0,:,1]-contributions2[0,:,0])
#    elif winner == 2:
#        featureDiff = abs(contributions1[0,:,0]-contributions2[0,:,1])
#    return sorted(zip(featureDiff,featureLabels),reverse=True)

def load_effect_means(data_limit=1000):
  #data_limit - number of SQL rows to pull
    
    
  #Thresholds for kills should be 20/1000
  #Thresholds for purchases should be 40/1000 
  #Distance metrics should be fine 2000 to ...?
  #Dragon  
  db = mdb.connect(user=dblogin, passwd=dbpw, host="localhost", db=database, charset='utf8')
  sqlcommand = [None]*11
  sqlcommand[0]='SELECT drag_trigg_kill_effect-drag_trigg_kill_baseline FROM team_drag_trigg_kill_mean WHERE ABS(drag_trigg_kill_effect-drag_trigg_kill_baseline) <= (20/1000) AND ABS(drag_trigg_kill_effect-drag_trigg_kill_baseline) > 0 AND Id <= 20001 LIMIT ' + str(data_limit)   
  sqlcommand[1]='SELECT baron_trigg_purchase_effect-baron_trigg_purchase_baseline FROM team_baron_trigg_purchase_mean WHERE ABS(baron_trigg_purchase_effect-baron_trigg_purchase_baseline) <= (20/1000) AND ABS(baron_trigg_purchase_effect-baron_trigg_purchase_baseline) > 0 AND Id <= 20001 LIMIT ' + str(data_limit)    
  sqlcommand[2]='SELECT drag_trigg_wardplace_effect-drag_trigg_wardplace_baseline FROM team_drag_trigg_wardplace_mean WHERE ABS(drag_trigg_wardplace_effect-drag_trigg_wardplace_baseline) <= (20/1000) AND ABS(drag_trigg_wardplace_effect-drag_trigg_wardplace_baseline) > 0 AND Id <= 20001 LIMIT ' + str(data_limit)    
  sqlcommand[3]='SELECT drag_trigg_wardkill_effect-drag_trigg_wardkill_baseline FROM team_drag_trigg_wardkill_mean WHERE ABS(drag_trigg_wardkill_effect-drag_trigg_wardkill_baseline) <= (20/1000) AND  ABS(drag_trigg_wardkill_effect-drag_trigg_wardkill_baseline) > 0 AND Id <= 20001 LIMIT ' + str(data_limit)    
  sqlcommand[4]='SELECT inhib_trigg_purchase_effect-inhib_trigg_purchase_baseline FROM team_inhib_trigg_purchase_mean WHERE ABS(inhib_trigg_purchase_effect-inhib_trigg_purchase_baseline) <= (20/1000) AND  ABS(inhib_trigg_purchase_effect-inhib_trigg_purchase_baseline) > 0 AND Id <= 20001 LIMIT ' + str(data_limit) 
  sqlcommand[5]='SELECT team_dist_time_early-team_dist_time_mid FROM team_dist_time_mean WHERE ABS(team_dist_time_early-team_dist_time_mid) <= (5000000) AND Id <= 20001 LIMIT ' + str(data_limit) 
  sqlcommand[6]='SELECT teammate_killed_teamdist_effect-teammate_killed_teamdist_baseline FROM team_teammate_killed_teamdist_mean WHERE ABS(teammate_killed_teamdist_effect-teammate_killed_teamdist_baseline) <= (5000000) AND Id <= 20001 LIMIT ' + str(data_limit) 
  sqlcommand[7]='SELECT enemy_killed_teamdist_effect-enemy_killed_teamdist_baseline FROM team_enemy_killed_teamdist_mean WHERE ABS(enemy_killed_teamdist_effect-enemy_killed_teamdist_baseline) <= (5000000) AND Id <= 20001 LIMIT ' + str(data_limit) 
  sqlcommand[8]='SELECT death_after_kill_baseline-death_after_kill_effect FROM team_death_after_kill_mean WHERE ABS(death_after_kill_effect-death_after_kill_baseline) <= (20/100) AND Id <= 20001  LIMIT ' + str(data_limit)    
  sqlcommand[9]='SELECT earlyCS FROM team_behavior_data WHERE Id <= 20001 LIMIT ' + str(data_limit)    
  sqlcommand[10]='SELECT earlyJGS FROM team_behavior_data WHERE Id <= 20001 LIMIT ' + str(data_limit)   

  thresholdU = [None]*11
  thresholdU[0] = 0.001 # thresholdDragChampKill=0.001
  thresholdU[1] = 0.001 # thresholdBaronPurchase=0.001
  thresholdU[2] = 0.0001 # thresholdDragWardPlace=0.0001
  thresholdU[3] = 0.0001 #thresholdDragWardKill=0.0001
  thresholdU[4] = 0.001 # thresholdInhibPurchase = 0.001
  thresholdU[5] = 50000 # thresholdDistTime = 50000  #Do NOT muptily by 1000*60 for distance metrics!
  thresholdU[6] = 50000 # thresholdTeamKillDist = 50000
  thresholdU[7] = 50000 # thresholdEnemyKillDist = 50000
  thresholdU[8] = 0.001 # thresholdDeathAfterKill = 0.001 #Reverse distribution here, since death after kill is BAD
  thresholdU[9] = 1000000 # thresholdEarlyCS = 25 #Greater than 50
  thresholdU[10] = 1000000 # thresholdEarlyJGS = -1 # No Threshold - all values are positive so -1 works
  
  thresholdL = [None]*11
  thresholdL[0] = 0 # thresholdDragChampKill=0.001
  thresholdL[1] = 0 # thresholdBaronPurchase=0.001
  thresholdL[2] = 0 # thresholdDragWardPlace=0.0001
  thresholdL[3] = 0 #thresholdDragWardKill=0.0001
  thresholdL[4] = 0 # thresholdInhibPurchase = 0.001
  thresholdL[5] = 0 # thresholdDistTime = 50000  #Do NOT muptily by 1000*60 for distance metrics!
  thresholdL[6] = 0 # thresholdTeamKillDist = 50000
  thresholdL[7] = 0 # thresholdEnemyKillDist = 50000
  thresholdL[8] = 0 # thresholdDeathAfterKill = 0.001 #Reverse distribution here, since death after kill is BAD
  thresholdL[9] = 25 # thresholdEarlyCS = 25 #Greater than 50
  thresholdL[10] = -1 # thresholdEarlyJGS = -1 # No Threshold - all values are positive so -1 works
  stDev=[]
  meanEffect=[]
  results_list = [None]*11  
  for s, sqlcmd in enumerate(sqlcommand):
      with db:
          cur = db.cursor()
          cur.execute(sqlcmd)
          query_results=cur.fetchall()
      results_array = numpy.array(query_results)[:]
      results_list[s] = results_array[(abs(results_array[:]) < thresholdU[s]) & (abs(results_array[:]) > thresholdL[s])]
      stDev.append(numpy.nanstd(results_list[s]))
      meanEffect.append(numpy.nanmean(results_list[s]))
  return results_list, meanEffect, stDev
  #results_array=numpy.array(query_results)
  #plt.figure()
  #plt.hist(results_array[(abs(results_array[:]) > -1)],50,normed=1)
  #plt.hist(results_array[(abs(results_array[:]) < 0.001) & (abs(results_array[:]) > 0)]*1000*60,50,normed=1)
  #stDev = numpy.nanstd(asdf[(abs(asdf[:]) < 50000) & (abs(asdf[:]) > 0)])


def extract_features_single(gamedata, return_type, frameEval = 20):
#   Extract features from json data of a single game
#   
#   Inputs:
#       gamedata:       Game data from Riot API (json format)
#       return_type:    Whether to return frame data ('frame'), behavior data ('behavior'), or ('both')
#                       frame data is essentially a game snapshot at that frame
#                       behavior data are various event triggered and otherwise metrics
#       frameEval:      The frame number to return when returning frame data

    returnVals=[]
    
    assistingParticipantIds=[]
    buildingType=[]
    creatorId=[]
    itemAfter=[]
    itemBefore=[]
    itemId=[]
    killerId=[]
    laneType=[]
    levelUpType=[]
    monsterType=[]
    participantId=[]
    pointCaptured=[]
    position=[]
    skillSlot=[]
    teamId=[]
    towerType=[]
    victimId=[]
    wardType=[] 
    EventKeyList = ['assistingParticipantIds', 'buildingType', 'creatorId', 'itemAfter', 'itemBefore', 'itemId', 'killerId', 'laneType', 'levelUpType', 'monsterType', 'participantId', 'pointCaptured', 'position', 'skillSlot', 'teamId', 'towerType', 'victimId', 'wardType']
    EventAttributesLists = [assistingParticipantIds, buildingType, creatorId, itemAfter, itemBefore, itemId, killerId, laneType, levelUpType, monsterType, participantId, pointCaptured, position, skillSlot, teamId, towerType, victimId, wardType]    
            
    eventType = []
    eventTimeStamp=[]
    participantRank=[]
    participantId=[]
    participantTeam=[]
    eventParticipantRank=[]
    eventTeamRank=[]
    eventTeamWin=[]
    teamRank=[None]*2
    teamDist=[None]*2
    eventParticipantId=[]
    eventTeamId=[]
    #eventTeamWin=[]
    eventParticipantWin=[] # if the participant was on the winning team
    eventTeammateDistance=[]
    frameTeammateDistance=[]
    participantPos=[]
    participantRole=[]
    participantLane=[]
    participantChampId=[]
    eventJGParticipate1=[] # BOOL if the JG participated in an event (e.g. did he help gank?)
    eventJGParticipate2=[] # BOOL if the JG participated in an event (e.g. did he help gank?)
    teamRoles=[]
    teamLanes=[]
    frameTeamCreepScore=[]
    frameTeamJGScore=[]
    participantCreepScore=[]
    participantJGScore=[]
    teamCS=[None]*2
    teamJGS=[None]*2
    firstJGGankTime1=[]
    firstJGGankTime2=[]
    WinLoss1=[]
    WinLoss2=[]
    FirstBlood1=[]
    FirstBlood2=[]
    teamGold1AtFrame=[]
    teamGold2AtFrame=[]
    teamXP1AtFrame=[]
    teamXP2AtFrame=[]
    numAssists1AtFrame=[]
    numAssists2AtFrame=[]
    
    
    WinLoss1.append(gamedata['teams'][0]['winner'])
    WinLoss2.append(gamedata['teams'][1]['winner'])
    FirstBlood1.append(gamedata['teams'][0]['firstBlood'])
    FirstBlood2.append(gamedata['teams'][1]['firstBlood'])
    #get 'Data @ frame'
    if len(gamedata['timeline']['frames'])-1 < frameEval:
        frameEval=len(gamedata['timeline']['frames'])-1
        
    teamGold1AtFrame.append(sum([gamedata['timeline']['frames'][frameEval]['participantFrames'][str(i)]['totalGold'] for i in range(1,6)]))
    teamGold2AtFrame.append(sum([gamedata['timeline']['frames'][frameEval]['participantFrames'][str(i)]['totalGold'] for i in range(6,11)]))
    teamXP1AtFrame.append(sum([gamedata['timeline']['frames'][frameEval]['participantFrames'][str(i)]['xp'] for i in range(1,6)]))
    teamXP2AtFrame.append(sum([gamedata['timeline']['frames'][frameEval]['participantFrames'][str(i)]['xp'] for i in range(6,11)]))
    
    #get participant ranks
    for participant in gamedata['participants']:
        participantRank.append(participant['highestAchievedSeasonTier'])
        participantId.append(participant['participantId'])
        participantTeam.append(participant['teamId']) 
        participantRole.append(participant['timeline']['role'])
        participantLane.append(participant['timeline']['lane'])
        participantChampId.append(participant['championId'])
        
 
    teamRank[0]=sum([i != 'UNRANKED' for j, i in enumerate(participantRank) if participantTeam[j]==100])
    teamRank[1]=sum([i != 'UNRANKED' for j, i in enumerate(participantRank) if participantTeam[j]==200])            
    
    teamRoles.append([])
    teamRoles.append([])
    teamRoles[0]=[i for j, i in enumerate(participantRole) if participantTeam[j]==100]
    teamRoles[1]=[i for j, i in enumerate(participantRole) if participantTeam[j]==200]
    
    teamLanes.append([])
    teamLanes.append([])
    teamLanes[0]=[i for j, i in enumerate(participantLane) if participantTeam[j]==100]
    teamLanes[1]=[i for j, i in enumerate(participantLane) if participantTeam[j]==200]
                
    for frame in gamedata['timeline']['frames']:
        #Calculate team distance
        participantPos.append([])
        participantCreepScore.append([])
        participantJGScore.append([])
        numAssists1AtFrame.append([])
        numAssists1AtFrame[-1]=0
        numAssists2AtFrame.append([])
        numAssists2AtFrame[-1]=0
        for i in range(0,10):
            participantPos[-1].append([])
            if 'position' in frame['participantFrames'][str(i+1)]:  # the final frame has no position, so we check
                participantPos[-1][-1].append(frame['participantFrames'][str(i+1)]['position']['x'])
                participantPos[-1][-1].append(frame['participantFrames'][str(i+1)]['position']['y'])
            else:   
                participantPos[-1][-1].append(float('nan'))
                participantPos[-1][-1].append(float('nan'))
                
            participantCreepScore[-1].append(frame['participantFrames'][str(i+1)]['minionsKilled'])
            participantJGScore[-1].append(frame['participantFrames'][str(i+1)]['jungleMinionsKilled'])
            
            
            
        #Assumes first 5 participants are in team 1 (this is true as far as i know) - check teamRank calculation to do it right                         
        teamDist[0]=sum(numpy.unique(distance.cdist(participantPos[-1][0:5],participantPos[-1][0:5],'euclidean')))
        teamDist[1]=sum(numpy.unique(distance.cdist(participantPos[-1][5:10],participantPos[-1][5:10],'euclidean')))                      
        frameTeammateDistance.append([])
        frameTeammateDistance[-1].append(teamDist[0])
        frameTeammateDistance[-1].append(teamDist[1])
        
        teamCS[0]=sum(participantCreepScore[-1][0:5])
        teamCS[1]=sum(participantCreepScore[-1][5:10])
        frameTeamCreepScore.append([])
        frameTeamCreepScore[-1].append(teamCS[0])
        frameTeamCreepScore[-1].append(teamCS[1])
    
        teamJGS[0]=sum(participantJGScore[-1][0:5])
        teamJGS[1]=sum(participantJGScore[-1][5:10])
        frameTeamJGScore.append([])
        frameTeamJGScore[-1].append(teamJGS[0])
        frameTeamJGScore[-1].append(teamJGS[1])
        
        if 'events' in frame:
            
            for event in frame['events']:
                #Get Continuous Data
                eventType.append(event['eventType'])
                eventTimeStamp.append(event['timestamp'])
                                        
                
                
                
                for i, eventKey in enumerate(EventKeyList):
                    if eventKey in event:
                        EventAttributesLists[i].append(event[eventKey]) #note, multiple participants are placed in a list
                        
                        if (eventKey == 'participantId' or eventKey == 'killerId' or eventKey == 'creatorId'):  #Assumes these 3 keys never co-exist within an event, and at least one always exists
                            if event[eventKey] > 0:  #For some events participantId = 0 which is invalid                             
                                eventParticipantRank.append(participantRank[participantId.index(event[eventKey])])                            
                                eventParticipantId.append(event[eventKey])
                                eventTeamId.append(participantTeam[participantId.index(event[eventKey])])
                                if participantTeam[participantId.index(event[eventKey])] == 100:
                                    eventTeamRank.append(teamRank[0])
                                    eventTeammateDistance.append(teamDist[0])
                                else:
                                    eventTeamRank.append(teamRank[1])
                                    eventTeammateDistance.append(teamDist[1])
                            else: 
                                eventParticipantRank.append(float('nan'))
                                eventParticipantId.append(float('nan'))
                                eventTeamId.append(float('nan'))
                                eventTeamRank.append(float('nan'))
                                eventTeammateDistance.append(float('nan'))
                           
                        if (eventKey == 'killerId' and event['eventType']=='CHAMPION_KILL'):
                            if event[eventKey] > 0:
                                team1JGId=[j for j, i in enumerate(participantLane[0:5]) if i =='JUNGLE']
                                team2JGId=[j for j, i in enumerate(participantLane[5:10]) if i =='JUNGLE']
                                if eventKey == 'killerId' and event['killerId'] in team1JGId:
                                    eventJGParticipate1.append(1)
                                    if not firstJGGankTime1:
                                        firstJGGankTime1.append(event['timestamp'])   
                                elif eventKey == 'assistingParticipantIds' and any(jg in team1JGId for jg in event['assistingParticipantIds']):
                                    eventJGParticipate1.append(1)
                                    if not firstJGGankTime1:
                                        firstJGGankTime1.append(event['timestamp'])
                                else:
                                    eventJGParticipate1.append(0)
                                if eventKey == 'killerId' and event['killerId'] in team2JGId:
                                    eventJGParticipate2.append(1)
                                    if not firstJGGankTime2:
                                        firstJGGankTime2.append(event['timestamp'])                          
                                elif eventKey == 'assistingParticipantIds' and any(jg in team2JGId for jg in event['assistingParticipantIds']):
                                    eventJGParticipate2.append(1)
                                    if not firstJGGankTime2:
                                        firstJGGankTime2.append(event['timestamp'])                                              
                                else:
                                    eventJGParticipate2.append(0)
                            else:
                                eventJGParticipate1.append(float('nan'))
                                eventJGParticipate2.append(float('nan'))
                        elif eventKey == 'killerId':
                            eventJGParticipate1.append(float('nan'))
                            eventJGParticipate2.append(float('nan'))
                            
                        if eventKey=='assistingParticipantIds' and event['eventType']=='CHAMPION_KILL':
                            if event['killerId'] in participantId[0:5]:
                                numAssists1AtFrame[-1] += len(event[eventKey])
                            if event['killerId'] in participantId[5:10]:
                                numAssists2AtFrame[-1] += len(event[eventKey])
                        if eventKey=='participantId' or eventKey=='creatorId':
                            eventJGParticipate1.append(float('nan'))
                            eventJGParticipate2.append(float('nan'))        
                                    
                    else:
                        EventAttributesLists[i].append(float('nan'))
                       # if (eventKey == 'participantId' or eventKey == 'killerId' or eventKey == 'creatorId'):
                       #     eventParticipantRank.append(float('nan'))
                       #     eventTeamRank.append(float('nan'))       
    if len(firstJGGankTime1) == 0:
        firstJGGankTime1.append(999999999) #rather than nan we use really large number
    if len(firstJGGankTime2) == 0:
        firstJGGankTime2.append(999999999)    

#%% 

    eventTypeArray=numpy.array(eventType) 
    eventTimeStampArray=numpy.array(eventTimeStamp)           
    monsterTypeArray=numpy.array(monsterType)
    eventParticipantRankArray=numpy.array(eventParticipantRank)
    eventParticipantIdArray=numpy.array(eventParticipantId)
    eventTeamIdArray=numpy.array(eventTeamId)
    buildingTypeArray=numpy.array(buildingType)
    eventTeammateDistanceArray=numpy.array(eventTeammateDistance,dtype=numpy.float64)
    frameTeammateDistanceArray1=numpy.array(frameTeammateDistance,dtype=numpy.float64)[:,0]
    frameTeammateDistanceArray2=numpy.array(frameTeammateDistance,dtype=numpy.float64)[:,1]
    team1Roles=numpy.array(teamRoles[0])
    team2Roles=numpy.array(teamRoles[1])
    team1Lanes=numpy.array(teamLanes[0])
    team2Lanes=numpy.array(teamLanes[1])
    frameCSArray1=numpy.array(frameTeamCreepScore,dtype=numpy.float64)[:,0]
    frameCSArray2=numpy.array(frameTeamCreepScore,dtype=numpy.float64)[:,1]
    frameJGSArray1=numpy.array(frameTeamJGScore,dtype=numpy.float64)[:,0]
    frameJGSArray2=numpy.array(frameTeamJGScore,dtype=numpy.float64)[:,1]
    eventJGParticipateArray1=numpy.array(eventJGParticipate1)
    eventJGParticipateArray2=numpy.array(eventJGParticipate2)
    
    T1WinLoss=WinLoss1[0]
    T2WinLoss=WinLoss2[0]
    Winner = 1*T1WinLoss + 2*T2WinLoss #1 if team 1 wins, 2 if team 2 wins
    T1FirstJGGank=firstJGGankTime1[0] #Only include this if < 20 min! Otherwise set it to really large number 
    T2FirstJGGank=firstJGGankTime2[0]
    
    
    #####################
    #   Team makeup     #
    #####################
    #MID,MIDDLE, TOP, JUNGLE, BOT, BOTTOM
    #DUO_SUPPORT, DUO_CARRY
    numMid1=len([k for m, k in enumerate(teamLanes[0]) if teamLanes[0][m]=='MIDDLE' or teamLanes[0][m]=='MID'])
    numTop1=len([k for m, k in enumerate(teamLanes[0]) if teamLanes[0][m]=='TOP'])
    numJG1=len([k for m, k in enumerate(teamLanes[0]) if teamLanes[0][m]=='JUNGLE'])
    numBot1=len([k for m, k in enumerate(teamLanes[0]) if teamLanes[0][m]=='BOTTOM' or teamLanes[0][m]=='BOT'])
    numDSupp1=len([k for m, k in enumerate(teamRoles[0]) if teamRoles[0][m]=='DUO_SUPPORT'])
    numDCarry1=len([k for m, k in enumerate(teamRoles[0]) if teamRoles[0][m]=='DUO_CARRY'])
    numMid2=len([k for m, k in enumerate(teamLanes[1]) if teamLanes[1][m]=='MIDDLE' or teamLanes[0][m]=='MID'])
    numTop2=len([k for m, k in enumerate(teamLanes[1]) if teamLanes[1][m]=='TOP'])
    numJG2=len([k for m, k in enumerate(teamLanes[1]) if teamLanes[1][m]=='JUNGLE'])
    numBot2=len([k for m, k in enumerate(teamLanes[1]) if teamLanes[1][m]=='BOTTOM' or teamLanes[0][m]=='BOT'])
    numDSupp2=len([k for m, k in enumerate(teamRoles[1]) if teamRoles[1][m]=='DUO_SUPPORT'])
    numDCarry2=len([k for m, k in enumerate(teamRoles[1]) if teamRoles[1][m]=='DUO_CARRY'])
    #CHALLENGER, MASTER, DIAMOND, PLATINUM, GOLD, SILVER, BRONZE, UNRANKED
    numChallenger1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='CHALLENGER'])
    numMaster1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='MASTER'])
    numDiamond1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='DIAMOND'])
    numPlatinum1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='PLATINUM'])
    numGold1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='GOLD'])
    numSilver1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='SILVER'])
    numBronze1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='BRONZE'])
    numUnranked1=len([k for m, k in enumerate(participantRank[0:5]) if participantRank[m]=='UNRANKED'])        
    numChallenger2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='CHALLENGER'])
    numMaster2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='MASTER'])
    numDiamond2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='DIAMOND'])
    numPlatinum2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='PLATINUM'])
    numGold2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='GOLD'])
    numSilver2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='SILVER'])
    numBronze2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='BRONZE'])
    numUnranked2=len([k for m, k in enumerate(participantRank[5:10]) if participantRank[m+5]=='UNRANKED'])        
   
    sumAssists1AtFrame=sum(numAssists1AtFrame[0:frameEval])
    sumAssists2AtFrame=sum(numAssists2AtFrame[0:frameEval])
    #########################
    #  Champion Makeup      #
    #########################
    #Load championDict from StaticData!
    class Champs: pass
    obj=Champs()  
    for key in championDict: 
        setattr(obj, championDict[key] + 'T1', len([k for m, k in enumerate(participantChampId[0:5]) if participantChampId[m]==key]))
        setattr(obj, championDict[key] + 'T2', len([k for m, k in enumerate(participantChampId[5:10]) if participantChampId[m+5]==key]))

    if (return_type == 'frame') or (return_type == 'both'): 
        #############################
        #   Frame data START        # 
        #############################
        #  For win/loss prediction  #
        if len(numAssists1AtFrame)-1 < frameEval:
            frameEval=len(numAssists1AtFrame)-1
        FFEvalTime=frameEval*60*1000
        
        #NEED 2 tables - one for random forest, one for features         
        #Other stuff to write to SQL Database
        T1GoldAtFrame=teamGold1AtFrame[0]
        T2GoldAtFrame=teamGold2AtFrame[0]
        T1XPAtFrame=teamXP1AtFrame[0]
        T2XPAtFrame=teamXP2AtFrame[0]

        Team1KillsAtFrame=len(eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==100) & (eventTimeStampArray <= FFEvalTime))])
        Team2KillsAtFrame=len(eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==200) & (eventTimeStampArray <= FFEvalTime))])                
        
        #Team1Kills=len(eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==100))])
        #Team2Kills=len(eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==200))])
        Team1CSAtFrame=frameTeamCreepScore[frameEval][0]
        Team2CSAtFrame=frameTeamCreepScore[frameEval][1]
        Team1JGSAtFrame=frameTeamJGScore[frameEval][0]
        Team2JGSAtFrame=frameTeamJGScore[frameEval][1]
        Team1NumDragsAtFrame=len(eventTimeStampArray[numpy.where((monsterTypeArray=='DRAGON') & (eventTeamIdArray==100) & (eventTimeStampArray <= FFEvalTime))])
        Team2NumDragsAtFrame=len(eventTimeStampArray[numpy.where((monsterTypeArray=='DRAGON') & (eventTeamIdArray==200) & (eventTimeStampArray <= FFEvalTime))])
        Team1NumInhibsAtFrame=len(eventTimeStampArray[numpy.where((buildingTypeArray=='INHIBITOR_BUILDING') & (eventTeamIdArray==100) & (eventTimeStampArray <= FFEvalTime))])
        Team2NumInhibsAtFrame=len(eventTimeStampArray[numpy.where((buildingTypeArray=='INHIBITOR_BUILDING') & (eventTeamIdArray==200) & (eventTimeStampArray <= FFEvalTime))])
        Team1NumTowersAtFrame=len(eventTimeStampArray[numpy.where((buildingTypeArray=='TOWER_BUILDING') & (eventTeamIdArray==100) & (eventTimeStampArray <= FFEvalTime))])
        Team2NumTowersAtFrame=len(eventTimeStampArray[numpy.where((buildingTypeArray=='TOWER_BUILDING') & (eventTeamIdArray==200) & (eventTimeStampArray <= FFEvalTime))])
        T1FirstBlood=FirstBlood1[0]
        T2FirstBlood=FirstBlood2[0]
        FirstBloodTeam = 1*T1FirstBlood + 2*T2FirstBlood #1 if team 1 wins, 2 if team 2 wins
        
        if T1FirstJGGank > frameEval*60*1000:
            FirstJGGankElapsedTime1 = 0
        else:
            FirstJGGankElapsedTime1 = frameEval*60*1000 - T1FirstJGGank
        if T2FirstJGGank > frameEval*60*1000:
            FirstJGGankElapsedTime2 = 0
        else:
            FirstJGGankElapsedTime2 = frameEval*60*1000 - T2FirstJGGank

            
        returnVals.append([T1GoldAtFrame, T1XPAtFrame, Team1KillsAtFrame, Team1CSAtFrame, Team1JGSAtFrame, Team1NumDragsAtFrame, Team1NumInhibsAtFrame, Team1NumTowersAtFrame, FirstJGGankElapsedTime1, numMid1, numTop1, numJG1, numBot1, numDSupp1, numDCarry1, numChallenger1, numMaster1, numDiamond1, numPlatinum1, numGold1, numSilver1, numBronze1, numUnranked1, sumAssists1AtFrame, obj.AnnieT1, obj.OlafT1, obj.GalioT1, obj.Twisted_FateT1, obj.XinZhaoT1, obj.UrgotT1, obj.LeBlancT1, obj.VladimirT1, obj.FiddlesticksT1, obj.AatroxT1, obj.MasterYiT1, obj.AlistarT1, obj.RyzeT1, obj.SionT1, obj.SivirT1, obj.SorakaT1, obj.TeemoT1, obj.TristanaT1, obj.WarwickT1, obj.NunuT1, obj.MissFortuneT1, obj.AsheT1, obj.TryndamereT1, obj.JaxT1, obj.MorganaT1, obj.ZileanT1, obj.SingedT1, obj.EvelynnT1, obj.TwitchT1, obj.KarthusT1, obj.ChoGathT1, obj.AmumuT1, obj.RammusT1, obj.AniviaT1, obj.ShacoT1, obj.DrMundoT1, obj.SonaT1, obj.KassadinT1, obj.IreliaT1, obj.JannaT1, obj.GankplankT1, obj.CorkiT1, obj.KarmaT1, obj.TaricT1, obj.VeigarT1, obj.TrundleT1, obj.SwainT1, obj.CaitlynT1, obj.BlitzcrankT1, obj.MalphiteT1, obj.KatarinaT1, obj.NocturneT1, obj.MaokaiT1, obj.RenektonT1, obj.JarvanIVT1, obj.EliseT1, obj.KayleT1, obj.WukongT1, obj.BrandT1, obj.LeeSinT1, obj.NamiT1, obj.RumbleT1, obj.CassiopeiaT1, obj.SkarnerT1, obj.AzirT1, obj.HeimerdingerT1, obj.NasusT1, obj.NidaleeT1, obj.UdyrT1, obj.PoppyT1, obj.GragasT1, obj.PantheonT1, obj.EzrealT1, obj.MordekaiserT1, obj.YorickT1, obj.AkaliT1, obj.KennenT1, obj.GarenT1, obj.LeonaT1, obj.MalzaharT1, obj.TalonT1, obj.RivenT1, obj.KogMawT1, obj.ShenT1, obj.LuxT1, obj.XerathT1, obj.ShyvanaT1, obj.AhriT1, obj.GravesT1, obj.FizzT1, obj.VolibearT1, obj.RengarT1, obj.VarusT1, obj.OriannaT1, obj.ViktorT1, obj.SejuaniT1, obj.FioraT1, obj.ZiggsT1, obj.LuluT1, obj.DravenT1, obj.HecarimT1, obj.KhaZixT1, obj.DariusT1, obj.JayceT1, obj.LissandraT1, obj.DianaT1, obj.QuinnT1, obj.SyndraT1, obj.ZyraT1, obj.VayneT1, obj.GnarT1, obj.ZacT1, obj.NautilusT1, obj.ThreshT1, obj.YasunoT1, obj.VelKozT1, obj.RekSaiT1, obj.KalistaT1, obj.BardT1, obj.BraumT1, obj.JinxT1, obj.TahmKenchT1, obj.LucianT1, obj.ZedT1, obj.EkkoT1, obj.ViT1, T2GoldAtFrame, T2XPAtFrame, Team2KillsAtFrame, Team2CSAtFrame, Team2JGSAtFrame, Team2NumDragsAtFrame, Team2NumInhibsAtFrame, Team2NumTowersAtFrame, FirstJGGankElapsedTime2, numMid2, numTop2, numJG2, numBot2, numDSupp2, numDCarry2, numChallenger2, numMaster2, numDiamond2, numPlatinum2, numGold2, numSilver2, numBronze2, numUnranked2, sumAssists2AtFrame, obj.AnnieT2, obj.OlafT2, obj.GalioT2, obj.Twisted_FateT2, obj.XinZhaoT2, obj.UrgotT2, obj.LeBlancT2, obj.VladimirT2, obj.FiddlesticksT2, obj.AatroxT2, obj.MasterYiT2, obj.AlistarT2, obj.RyzeT2, obj.SionT2, obj.SivirT2, obj.SorakaT2, obj.TeemoT2, obj.TristanaT2, obj.WarwickT2, obj.NunuT2, obj.MissFortuneT2, obj.AsheT2, obj.TryndamereT2, obj.JaxT2, obj.MorganaT2, obj.ZileanT2, obj.SingedT2, obj.EvelynnT2, obj.TwitchT2, obj.KarthusT2, obj.ChoGathT2, obj.AmumuT2, obj.RammusT2, obj.AniviaT2, obj.ShacoT2, obj.DrMundoT2, obj.SonaT2, obj.KassadinT2, obj.IreliaT2, obj.JannaT2, obj.GankplankT2, obj.CorkiT2, obj.KarmaT2, obj.TaricT2, obj.VeigarT2, obj.TrundleT2, obj.SwainT2, obj.CaitlynT2, obj.BlitzcrankT2, obj.MalphiteT2, obj.KatarinaT2, obj.NocturneT2, obj.MaokaiT2, obj.RenektonT2, obj.JarvanIVT2, obj.EliseT2, obj.KayleT2, obj.WukongT2, obj.BrandT2, obj.LeeSinT2, obj.NamiT2, obj.RumbleT2, obj.CassiopeiaT2, obj.SkarnerT2, obj.AzirT2, obj.HeimerdingerT2, obj.NasusT2, obj.NidaleeT2, obj.UdyrT2, obj.PoppyT2, obj.GragasT2, obj.PantheonT2, obj.EzrealT2, obj.MordekaiserT2, obj.YorickT2, obj.AkaliT2, obj.KennenT2, obj.GarenT2, obj.LeonaT2, obj.MalzaharT2, obj.TalonT2, obj.RivenT2, obj.KogMawT2, obj.ShenT2, obj.LuxT2, obj.XerathT2, obj.ShyvanaT2, obj.AhriT2, obj.GravesT2, obj.FizzT2, obj.VolibearT2, obj.RengarT2, obj.VarusT2, obj.OriannaT2, obj.ViktorT2, obj.SejuaniT2, obj.FioraT2, obj.ZiggsT2, obj.LuluT2, obj.DravenT2, obj.HecarimT2, obj.KhaZixT2, obj.DariusT2, obj.JayceT2, obj.LissandraT2, obj.DianaT2, obj.QuinnT2, obj.SyndraT2, obj.ZyraT2, obj.VayneT2, obj.GnarT2, obj.ZacT2, obj.NautilusT2, obj.ThreshT2, obj.YasunoT2, obj.VelKozT2, obj.RekSaiT2, obj.KalistaT2, obj.BardT2, obj.BraumT2, obj.JinxT2, obj.TahmKenchT2, obj.LucianT2, obj.ZedT2, obj.EkkoT2, obj.ViT2, FirstBloodTeam, frameEval, Winner])
       
    if return_type == 'behavior' or return_type == 'both':
        ###########################################
        #   Event Triggered Features START        # 
        ###########################################
        #   FOR COACHING ADVICE                   #
        interval_length=8*60*1000
        time_window=1*60*1000
        time_step=2500
        end_time=eventTimeStamp[-1]

        #Death rate near dragon   
        AnyDragonTime = eventTimeStampArray[numpy.where(monsterTypeArray=='DRAGON')]    
        ChampionKillTimesT1=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==100))]    
        ChampionKillTimesT2=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==200))]
        DragTrigChampKill1=event_triggered_eventTimes(AnyDragonTime,ChampionKillTimesT1,interval_length,time_window,time_step,end_time)
        DragTrigChampKill2=event_triggered_eventTimes(AnyDragonTime,ChampionKillTimesT2,interval_length,time_window,time_step,end_time)
    
        #Baron behavior    
        FirstBaronTime = eventTimeStampArray[numpy.where(monsterTypeArray=='BARON_NASHOR')[0][0:1]]
        BaronTeam = eventTeamIdArray[numpy.where(monsterTypeArray=='BARON_NASHOR')[0][0:1]]    
        ItemPurchase=eventTimeStampArray[numpy.where((eventTypeArray=='ITEM_PURCHASED') & (eventTeamIdArray==BaronTeam))]
        if BaronTeam==100:
            BaronTrigPurchase1=event_triggered_eventTimes(FirstBaronTime,ItemPurchase,interval_length,time_window,time_step,end_time)
            BaronTrigPurchase2=[]
        elif BaronTeam==200:
            BaronTrigPurchase1=[]
            BaronTrigPurchase2=event_triggered_eventTimes(FirstBaronTime,ItemPurchase,interval_length,time_window,time_step,end_time)
        else:
            BaronTrigPurchase1=[]
            BaronTrigPurchase2=[]
        #Ward place
        WardPlacedTime1 = eventTimeStampArray[numpy.where((eventTypeArray=='WARD_PLACED') & (eventTeamIdArray==100))]
        WardPlacedTime2 = eventTimeStampArray[numpy.where((eventTypeArray=='WARD_PLACED') & (eventTeamIdArray==200))]    
        AnyDragonTime = eventTimeStampArray[numpy.where(monsterTypeArray=='DRAGON')]    
        DragTrigWardPlaced1=event_triggered_eventTimes(AnyDragonTime,WardPlacedTime1,interval_length,time_window,time_step,end_time)
        DragTrigWardPlaced2=event_triggered_eventTimes(AnyDragonTime,WardPlacedTime2,interval_length,time_window,time_step,end_time)
        
        #Ward Killed
        AnyDragonTime = eventTimeStampArray[numpy.where(monsterTypeArray=='DRAGON')]
        WardKillTimes1 = eventTimeStampArray[numpy.where((eventTypeArray=='WARD_KILL') & (eventTeamIdArray==100))]
        WardKillTimes2 = eventTimeStampArray[numpy.where((eventTypeArray=='WARD_KILL') & (eventTeamIdArray==200))]
        DragTrigWardKill1=event_triggered_eventTimes(AnyDragonTime,WardKillTimes1,interval_length,time_window,time_step,end_time)
        DragTrigWardKill2=event_triggered_eventTimes(AnyDragonTime,WardKillTimes2,interval_length,time_window,time_step,end_time)
    
        #Inhibitor behavior    
        FirstInhibTime = eventTimeStampArray[numpy.where(buildingTypeArray=='INHIBITOR_BUILDING')[0][0:1]]
        InhibTeam = eventTeamIdArray[numpy.where(buildingTypeArray=='INHIBITOR_BUILDING')[0][0:1]]    
        ItemPurchase=eventTimeStampArray[numpy.where((eventTypeArray=='ITEM_PURCHASED') & (eventTeamIdArray==InhibTeam))]
        if InhibTeam==100:
            InhibTrigPurchase1=event_triggered_eventTimes(FirstInhibTime,ItemPurchase,interval_length,time_window,time_step,end_time)
            InhibTrigPurchase2=[]
        elif InhibTeam==200:
            InhibTrigPurchase1=[]
            InhibTrigPurchase2=event_triggered_eventTimes(FirstInhibTime,ItemPurchase,interval_length,time_window,time_step,end_time)
        elif numpy.isnan(InhibTeam):  #when minions kill inhib, I don't know which team killed it
            InhibTrigPurchase1=[]
            InhibTrigPurchase2=[]
        else:
            InhibTrigPurchase1=[]
            InhibTrigPurchase2=[]
        #Team distance over time  (frames)      
        # The arrays frameTeammateDistanceArray1, frameTeammateDistanceArray2 contain distance
        # These are NOT padded with nans for each game!
        
        #Teammate distance on teammate killed  
        Team1MemberKilled=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==200) & (eventTimeStampArray >= 1200000))]
        Team1Distance=eventTeammateDistanceArray[numpy.where((eventTeamIdArray==100) & (eventTimeStampArray >= 1200000))]
        valueTimes1=eventTimeStampArray[numpy.where((eventTeamIdArray==100) & (eventTimeStampArray >= 1200000))]    
        Team2MemberKilled=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==100) & (eventTimeStampArray >= 1200000))]
        Team2Distance=eventTeammateDistanceArray[numpy.where((eventTeamIdArray==200) & (eventTimeStampArray >= 1200000))]
        valueTimes2=eventTimeStampArray[numpy.where((eventTeamIdArray==200) & (eventTimeStampArray >= 1200000))]    
        DistOnTeamMemberKilled1=event_triggered_valueTimes(Team1MemberKilled,Team1Distance,valueTimes1,interval_length,time_window,time_step,end_time)
        DistOnTeamMemberKilled2=event_triggered_valueTimes(Team2MemberKilled,Team2Distance,valueTimes2,interval_length,time_window,time_step,end_time)
    
        #Teammate distance on enemy kill  
        Team1EnemyKilled=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==100) & (eventTimeStampArray > 1200000))]
        Team1Distance=eventTeammateDistanceArray[numpy.where((eventTeamIdArray==100) & (eventTimeStampArray > 1200000))]
        valueTimes1=eventTimeStampArray[numpy.where((eventTeamIdArray==100) & (eventTimeStampArray > 1200000))]    
        Team2EnemyKilled=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==200) & (eventTimeStampArray > 1200000))]
        Team2Distance=eventTeammateDistanceArray[numpy.where((eventTeamIdArray==200) & (eventTimeStampArray > 1200000))]
        valueTimes2=eventTimeStampArray[numpy.where((eventTeamIdArray==200) & (eventTimeStampArray > 1200000))]    
        DistOnEnemyKilled1=event_triggered_valueTimes(Team1EnemyKilled,Team1Distance,valueTimes1,interval_length,time_window,time_step,end_time)
        DistOnEnemyKilled2=event_triggered_valueTimes(Team2EnemyKilled,Team2Distance,valueTimes2,interval_length,time_window,time_step,end_time)
            
        # Teammates death after killing enemy
        Team1EnemyKilled=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==100) & (eventTimeStampArray < 1200000))]
        Team2EnemyKilled=eventTimeStampArray[numpy.where((eventTypeArray=='CHAMPION_KILL') & (eventTeamIdArray==200) & (eventTimeStampArray < 1200000))]
        DeathAfterEnemyKill1=event_triggered_eventTimes(Team2EnemyKilled,Team1EnemyKilled,interval_length,time_window,time_step,end_time)
        DeathAfterEnemyKill2=event_triggered_eventTimes(Team1EnemyKilled,Team2EnemyKilled,interval_length,time_window,time_step,end_time)
        
        # Early Creep Score
        earlyCreepScore1=frameTeamCreepScore[10][0]
        earlyCreepScore2=frameTeamCreepScore[10][1]
    
        # Jungle minions killed early
        earlyJGScore1=frameTeamJGScore[10][0]
        earlyJGScore2=frameTeamJGScore[10][1] 
        
        # First successful Gank already exists
     
        #JG Gank Rate
        JGPartic1=len(eventJGParticipateArray1[numpy.where((eventJGParticipateArray1==1) & (eventTimeStampArray < 1200000))])
        JGPartic2=len(eventJGParticipateArray1[numpy.where((eventJGParticipateArray2==1) & (eventTimeStampArray < 1200000))])
        JGNoPartic1=len(eventJGParticipateArray1[numpy.where((eventJGParticipateArray1==0) & (eventTimeStampArray < 900000))])
        JGNoPartic2=len(eventJGParticipateArray1[numpy.where((eventJGParticipateArray2==0) & (eventTimeStampArray < 900000))])
         
        #Total assists
        sumAssists1AtEnd=sum(numAssists1AtFrame)
        sumAssists2AtEnd=sum(numAssists2AtFrame)

        returnVals.append([[DragTrigChampKill1, BaronTrigPurchase1, DragTrigWardPlaced1, DragTrigWardKill1, InhibTrigPurchase1, frameTeammateDistanceArray1, DistOnTeamMemberKilled1, DistOnEnemyKilled1, DeathAfterEnemyKill1, earlyCreepScore1, earlyJGScore1, JGPartic1, JGNoPartic1, T1FirstJGGank, numMid1, numTop1, numJG1, numBot1, numDSupp1, numDCarry1, numChallenger1, numMaster1, numDiamond1, numPlatinum1, numGold1, numSilver1, numBronze1, numUnranked1, sumAssists1AtEnd, T1WinLoss], [DragTrigChampKill2, BaronTrigPurchase2, DragTrigWardPlaced2, DragTrigWardKill2, InhibTrigPurchase2, frameTeammateDistanceArray2, DistOnTeamMemberKilled2, DistOnEnemyKilled2, DeathAfterEnemyKill2, earlyCreepScore2, earlyJGScore2, JGPartic2, JGNoPartic2, T2FirstJGGank, numMid2, numTop2, numJG2, numBot2, numDSupp2, numDCarry2, numChallenger2, numMaster2, numDiamond2, numPlatinum2, numGold2, numSilver2, numBronze2, numUnranked2, sumAssists2AtEnd, T2WinLoss]])
    
    return returnVals

    
def event_triggered_eventTimes(alignTimes,eventsToAlign,interval_length,time_window,time_step,end_time):
    # alignTimes - numpy array of times to align data to
    # eventsToAlign - numpy array of times of the events that need to be aligned    
    numsteps = round(interval_length/time_step) 
    #event_triggered_avg=-9999
    event_triggered_avg=numpy.empty([len(alignTimes),numsteps],dtype='float64')
    event_triggered_avg[:]=numpy.nan
    for j, a in enumerate(alignTimes):
        ratehold=numpy.empty(numsteps)
        if (a + (interval_length/2.) <= end_time) & (a - (interval_length/2.) >= 0):
            for i in range(0,numsteps):
                eventSum = len(eventsToAlign[(eventsToAlign >= a-(time_window/2.)-(interval_length/2.)+(i*time_step)) & (eventsToAlign < a+(time_window/2.)-(interval_length/2.)+(i*time_step))])
                ratehold[i]=eventSum/time_window
            event_triggered_avg[j]=ratehold
    return event_triggered_avg     

def event_triggered_valueTimes(alignTimes,valuesToAlign,timeVector,interval_length,time_window,time_step,end_time):
    # alignTimes - numpy array of times to align data to
    # valuesToAlign - numpy array of values at each event type that need to be aligned
    # timeVector- numpy array of vector of times for each value in valuesToAlign
    numsteps = round(interval_length/time_step) 
    #event_triggered_avg=-9999
    event_triggered_avg=numpy.empty([len(alignTimes),numsteps],dtype='float64')
    event_triggered_avg[:]=numpy.nan
    for j, a in enumerate(alignTimes):
        valuehold=numpy.empty(numsteps)
        if (a + (interval_length/2.) <= end_time) & (a - (interval_length/2.) >= 0):
            for i in range(0,numsteps):
                valuehold[i]=numpy.mean(valuesToAlign[(timeVector >= a-(time_window/2.)-(interval_length/2.)+(i*time_step)) & (timeVector < a+(time_window/2.)-(interval_length/2.)+(i*time_step))])
            event_triggered_avg[j]=valuehold
#        sum(valuesToAlign[[(timeVector >= a-(time_window/2.)-(interval_length/2.)+(i*time_step)) & (timeVector < a+(time_window/2.)-(interval_length/2.)+(i*time_step)) for i in range(0,numsteps)]])
    return event_triggered_avg 
#[(timeVector >= a-(time_window/2.)-(interval_length/2.)+(i*time_step)) & (timeVector < a+(time_window/2.)-(interval_length/2.)+(i*time_step)) for i in range(0,numsteps)]


#NOTE:  FUNCTION IS NOT COMPLETE!!!!!!
#NEED TO PAD CORRECTLY - E.g. if a game ends prior to a time, its 'rate' should not be 0, but nan
#DO NOT USE UNTIL IT IS FIXED!!!
def getRate(eventTimes,time_interval1,time_interval2,time_window,time_step,end_time):
    interval_length=time_interval2-time_interval1
    numsteps=round(interval_length/time_step)
    rate=0    
    rate=numpy.array([])
    for i in range(0,numsteps):
        if a-(time_window/2.)-(interval_length/2.)+(i*time_step) > end_time:
            rate=numpy.append(rate,numpy.nan)
        else:
            eventSum = len(eventTimes[(eventTimes >= a-(time_window/2.)-(interval_length/2.)+(i*time_step)) & (eventTimes < a+(time_window/2.)-(interval_length/2.)+(i*time_step))])
            rate=numpy.append(rate,eventSum/time_window)
    return rate                