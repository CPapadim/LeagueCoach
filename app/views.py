import sys
import numpy
from flask import render_template, request
from app import app
from functions.appFuncs import *
import pymysql as mdb
import dill
import time
import requests
import json
#from treeinterpreter import treeinterpreter as ti
from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.resources import CDN
import bokeh.models as bkm
from bokeh.models import HoverTool, CrosshairTool, SingleIntervalTicker, LinearAxis, ColumnDataSource
global WinLoseForests
with open('RandomForest64bit_20k_LastFrame45FStep3.pickle','rb') as f:
    WinLoseForests=dill.load(f)
    
#with open('crds.pickle','wb') as f:
#    dill.dump([dblogin, dbpw,riot_api_key, database],f)
global dblogin, dbpw, database, riot_api_key
with open('crds.pickle','rb') as f:
    dblogin, dbpw,riot_api_key, database = dill.load(f)
db = mdb.connect(user=dblogin, passwd=dbpw, host="localhost", db=database, charset='utf8')


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/gsinput')
def gamestatus_input():
  return render_template("gsinput.html")

@app.route('/gsoutput')
def gamestatus_output():

  #pull 'ID' from input field and store it
  summonerName = request.args.get('ID')

  #######################
  #  Get Game Data      #
  #######################
  url="https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/" + str(summonerName) + "?api_key=" + str(riot_api_key)
  response = requests.get(url)
  success=False
  while not success:  
    if str(response) == "<Response [200]>":
        summonerId=json.loads(response.text)[summonerName.lower()]['id']
        time.sleep(2)
        success=True
    else:
        return render_template("error.html",error = response)      
  url="https://na.api.pvp.net/api/lol/na/v1.3/game/by-summoner/" + str(summonerId) + "/recent?api_key=" + str(riot_api_key) 
  response = requests.get(url)
  success2 = False
  playerTeam=[]  
  #Only use the most recent game for probability analysis
  while not success2:
      if str(response) == "<Response [200]>":
          gameData = json.loads(response.text)['games']
          playerTeam=int(gameData[0]['teamId']/100)
          gid = gameData[0]['gameId']
          success2 = True
          time.sleep(2)
      else:
          return render_template("error.html",error = response)

  
  url="https://na.api.pvp.net/api/lol/na/v2.2/match/" + str(gid) + "?includeTimeline=true&api_key=" + str(riot_api_key)
  response = requests.get(url)
  success3 = False
  while not success3:
      if str(response) == "<Response [200]>":
          jsondata=json.loads(response.text)
          teamFeaturesDiff = numpy.empty([len(jsondata['timeline']['frames']),8])
          prob_win1win2=numpy.empty(len(jsondata['timeline']['frames']))
          frameStep=3
          maxForestFrame=45
          frameVec = range(0,maxForestFrame+1,frameStep)
          for frame in range(0,len(jsondata['timeline']['frames'])):
              if frame > maxForestFrame:
                  forestFrame = maxForestFrame
              else:
                  forestFrame = frameVec[round(frame/frameStep)]
              try:
                  extractedFeatures=extract_features_single(jsondata,'frame',frame)[0][:-1]
              except:
                  return render_template("error.html",error = "Recent game history may only contain Summoner's Rift games and all game participants must have played in the current season")                      
               
              rf = getattr(WinLoseForests,'f' + str(forestFrame))
              prob_win1win2[frame]=rf.predict_proba(extractedFeatures)[0,playerTeam-1] #Should be [0,0] for team 1
#              if playerTeam == 2:
#                  prob_win1win2[frame] = 1 - prob_win1win2[frame]
              teamFeaturesDiff[frame,:] = numpy.array([extractedFeatures[i+150*(playerTeam-1)] for i in range(0,8)])-numpy.array([extractedFeatures[i+150*(2-playerTeam)] for i in range(0,8)])
          winner = 1*jsondata['teams'][0]['winner'] + 2*jsondata['teams'][1]['winner']             
          success3=True
          time.sleep(2)        
      else:
          return render_template("error.html",error = response)
  ########################
  #   Generate Plot      #
  ########################
  # output to static HTML file
  source = ColumnDataSource(
      data = dict(
          x = range(0,len(jsondata['timeline']['frames'])),
          y = prob_win1win2,
          Gold = teamFeaturesDiff[:,0],
          XP = teamFeaturesDiff[:,1],
          Kills = teamFeaturesDiff[:,2],
          CS = teamFeaturesDiff[:,3],
          JGS = teamFeaturesDiff[:,4],
          Dragons = teamFeaturesDiff[:,5],
          Inhibitors = teamFeaturesDiff[:,6],
          Towers = teamFeaturesDiff[:,7]
      )
  )  

  crosshair = CrosshairTool(
    dimensions=["height"])
  # create a new plot with a title and axis labels
  p = figure(x_range=[0,len(teamFeaturesDiff)-1],y_range=[0,1],toolbar_location = None, title="Probability to Win", x_axis_label='Time (m)', y_axis_label='Win Probability',tools=[crosshair],width=960,height=300)
  p.line(x=[0,len(teamFeaturesDiff)-1],y=[0.5,0.5],line_color="#000000")  
  g1=p.line('x','y',line_width=2,source=source)  
  p.scatter('x','y',source=source)

  # add a line renderer with legend and line thickness
  hover = HoverTool(
    renderers=[g1],
    tooltips=[
        ("Gold","@Gold"), 
        ("XP","@XP"),        
        ("Kills","@Kills"),        
        ("CS","@CS"),        
        ("JGS","@JGS"),        
        ("Dragons","@Dragons"),        
        ("Inhibitors","@Inhibitors"),        
        ("Towers","@Towers"),               
    ],
    line_policy='nearest',
    point_policy = 'snap_to_data'
  )
  p.add_tools(hover)
  ft = file_html(p,CDN,'title')
  return render_template("gsoutput.html",ft = ft)
#  return render_template("gsoutput.html", prob_win1win2 = prob_win1win2, winner = winner, playerTeam = playerTeam)


@app.route('/coachinput')
def coach_input():
  return render_template("coachinput.html")

@app.route('/coachadvice')
def coach_output():
  #pull 'ID' from input field and store it
  summonerName = request.args.get('ID')
 # with open('randomForest64bit.pickle','rb') as f:
  #  winLoseForest=dill.load(f)
  
  
  ###############################
  #    GET GAMES ---  START     #  
  ###############################
  url="https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/" + str(summonerName) + "?api_key=" + str(riot_api_key)
  response = requests.get(url)
  success=False
  while not success:  
    if str(response) == "<Response [200]>":
        summonerId=json.loads(response.text)[summonerName.lower()]['id']
        time.sleep(2)
        success=True
    else:
        return render_template("error.html",error = response)      
  url="https://na.api.pvp.net/api/lol/na/v1.3/game/by-summoner/" + str(summonerId) + "/recent?api_key=" + str(riot_api_key) 
  response = requests.get(url)
  success2 = False
  playerTeam=[]  
  while not success2:
      if str(response) == "<Response [200]>":
          gameId=[]
          gameData = json.loads(response.text)['games']
          for game in gameData:
              gameId.append(game['gameId']) 
              playerTeam.append(int(game['teamId']/100))
          success2 = True
          time.sleep(2)
      else:
          return render_template("error.html",error = response)
  extractedFeatures=[]
  for gid in gameId:   
      url="https://na.api.pvp.net/api/lol/na/v2.2/match/" + str(gid) + "?includeTimeline=true&api_key=" + str(riot_api_key)
      response = requests.get(url)
      success3 = False
      while not success3:
          if str(response) == "<Response [200]>":
              jsondata=json.loads(response.text)
              try:
                  extractedFeatures.append(extract_features_single(jsondata,'behavior'))
              except:
                  return render_template("error.html",error = "Recent game history may only contain Summoner's Rift games and all game participants must have played in the current season")                      
           
              success3=True
              time.sleep(2)
          else:
              return render_template("error.html",error = response)              
  #############################################
  #    GET DATA AND CALCULATE ---  START      #  
  #############################################             
  indicesB=[];
  indicesB.append(range(0,24))
  indicesB.append(range(12,60))
  indicesB.append(range(36,60))
  indicesB.append(range(12,48))
  indicesB.append(range(12,48))
  indicesB.append(range(10,20))
  indicesB.append(range(12,36))
  indicesB.append(range(12,36))
  indicesB.append(range(0,24))
  # Effect indices
  indicesE=[]
  indicesE.append(range(60,78))
  indicesE.append(range(103,113))
  indicesE.append(range(84,96))
  indicesE.append(range(84,96))
  indicesE.append(range(108,120))
  indicesE.append(range(3,10))
  indicesE.append(range(72,96))
  indicesE.append(range(78,84))
  indicesE.append(range(90,102))
  tables=[]
  tables.append('team_drag_trigg_kill_mean')        
  tables.append('team_baron_trigg_purchase_mean')                
  tables.append('team_drag_trigg_wardplace_mean')        
  tables.append('team_drag_trigg_wardkill_mean')        
  tables.append('team_inhib_trigg_purchase_mean')        
  tables.append('team_dist_time_mean')        
  tables.append('team_teammate_killed_teamdist_mean')        
  tables.append('team_enemy_killed_teamdist_mean')        
  tables.append('team_death_after_kill_mean')
  drag_trigg_kill_isSet = 0
  baron_trigg_purchase_isSet = 0
  drag_trigg_wardplaced_isSet = 0
  drag_trigg_wardkilled_isSet = 0
  inhib_trigg_purchase_isSet = 0
  team_dist_time_isSet = 0
  teammate_killed_teamdist_isSet = 0
  enemy_killed_teamdist_isSet = 0
  death_after_kill_isSet = 0
  earlyCreepScore = numpy.empty(len(extractedFeatures))
  earlyJGScore = numpy.empty(len(extractedFeatures))
  JGParticRate = numpy.empty(len(extractedFeatures))
  numJG = numpy.empty(len(extractedFeatures))
  numBot = numpy.empty(len(extractedFeatures))
  numDSupp = numpy.empty(len(extractedFeatures))
  numDCarry = numpy.empty(len(extractedFeatures))
  assistsAtEnd = numpy.empty(len(extractedFeatures))
  for ff, feature in enumerate(extractedFeatures):
      #0: DragTrigChampKill, 1: BaronTrigPurchase, 2: DragTrigWardPlaced, 3: DragTrigWardKill, 4: InhibTrigPurchase, 
      #5: frameTeammateDistanceArra1, 6: DistOnTeamMemberKilled, 7: DistOnEnemyKilled, 8: DeathAfterEnemyKill, 
      #9: earlyCreepScore, 10: earlyJGScore, 11: JGPartic, 12: JGNoPartic, 13: FirstJGGank, 14: numMid, 15: numTop, 16: numJG, 
      #17: numBot, 18: numDSupp, 19: numDCarry, 20: numChallenger, 21: numMaster, 22: numDiamond, 23: numPlatinum, 24: numGold, 
      #25: numSilver, 26: numBronze, 27: numUnranked, 28: sumAssistsAtEnd, 29: WinLoss
      
      #effect=feature[0][team][metric_type][num_measures,indicesEffect]       
      #dragkill_effect=numpy.nanmean(numpy.nanmean(feature[0][playerTeam[ff]-1][0][:,indicesE[0]],axis=1),axis=0)
      #dragkill_base=numpy.nanmean(numpy.nanmean(feature[0][playerTeam[ff]-1][0][:,indicesB[0]],axis=1),axis=0)
      if len(feature[0][playerTeam[ff]-1][0]) > 0:
          if drag_trigg_kill_isSet == 0:
              drag_trigg_kill=feature[0][playerTeam[ff]-1][0][:,indicesE[0]]
              drag_trigg_kill_base=feature[0][playerTeam[ff]-1][0][:,indicesB[0]]
              drag_trigg_kill_isSet = 1
          else:
              drag_trigg_kill = numpy.vstack((drag_trigg_kill,feature[0][playerTeam[ff]-1][0][:,indicesE[0]]))
              drag_trigg_kill_base = numpy.vstack((drag_trigg_kill_base,feature[0][playerTeam[ff]-1][0][:,indicesB[0]]))
              
              
      if len(feature[0][playerTeam[ff]-1][1]) > 0:             
          if baron_trigg_purchase_isSet == 0:
              baron_trigg_purchase=feature[0][playerTeam[ff]-1][1][:,indicesE[1]]
              baron_trigg_purchase_base=feature[0][playerTeam[ff]-1][1][:,indicesB[1]]
              baron_trigg_purchase_isSet = 1
          else:
              baron_trigg_purchase = numpy.vstack((baron_trigg_purchase,feature[0][playerTeam[ff]-1][1][:,indicesE[1]]))
              baron_trigg_purchase_base = numpy.vstack((baron_trigg_purchase_base,feature[0][playerTeam[ff]-1][1][:,indicesB[1]]))
              
      if len(feature[0][playerTeam[ff]-1][2]) > 0:               
          if drag_trigg_wardplaced_isSet == 0:
              drag_trigg_wardplaced=feature[0][playerTeam[ff]-1][2][:,indicesE[2]]
              drag_trigg_wardplaced_base=feature[0][playerTeam[ff]-1][2][:,indicesB[2]]
              drag_trigg_wardplaced_isSet = 1
          else:
              drag_trigg_wardplaced = numpy.vstack((drag_trigg_wardplaced,feature[0][playerTeam[ff]-1][2][:,indicesE[2]]))
              drag_trigg_wardplaced_base = numpy.vstack((drag_trigg_wardplaced_base,feature[0][playerTeam[ff]-1][2][:,indicesB[2]]))
              
      if len(feature[0][playerTeam[ff]-1][3]) > 0:               
          if drag_trigg_wardkilled_isSet == 0:
              drag_trigg_wardkilled=feature[0][playerTeam[ff]-1][3][:,indicesE[3]]
              drag_trigg_wardkilled_base=feature[0][playerTeam[ff]-1][3][:,indicesB[3]]
              drag_trigg_wardkilled_isSet = 1
          else:
              drag_trigg_wardkilled = numpy.vstack((drag_trigg_wardkilled,feature[0][playerTeam[ff]-1][3][:,indicesE[3]]))
              drag_trigg_wardkilled_base = numpy.vstack((drag_trigg_wardkilled_base,feature[0][playerTeam[ff]-1][3][:,indicesB[3]]))
              
      if len(feature[0][playerTeam[ff]-1][4]) > 0:               
         if inhib_trigg_purchase_isSet == 0:
              inhib_trigg_purchase=feature[0][playerTeam[ff]-1][4][:,indicesE[4]]
              inhib_trigg_purchase_base=feature[0][playerTeam[ff]-1][4][:,indicesB[4]]
              inhib_trigg_purchase_isSet = 1
         else:
              inhib_trigg_purchase = numpy.vstack((inhib_trigg_purchase,feature[0][playerTeam[ff]-1][4][:,indicesE[4]]))
              inhib_trigg_purchase_base = numpy.vstack((inhib_trigg_purchase_base,feature[0][playerTeam[ff]-1][4][:,indicesB[4]]))
              
      if len(feature[0][playerTeam[ff]-1][5]) > 0:               
          if team_dist_time_isSet == 0:
              team_dist_time=feature[0][playerTeam[ff]-1][5][indicesE[5]]
              team_dist_time_base=feature[0][playerTeam[ff]-1][5][indicesB[5]]
              team_dist_time_isSet = 1
          else:
              team_dist_time = numpy.vstack((team_dist_time,feature[0][playerTeam[ff]-1][5][indicesE[5]]))
              team_dist_time_base = numpy.vstack((team_dist_time_base,feature[0][playerTeam[ff]-1][5][indicesB[5]]))
              
      if len(feature[0][playerTeam[ff]-1][6]) > 0:               
          if teammate_killed_teamdist_isSet == 0:
              teammate_killed_teamdist=feature[0][playerTeam[ff]-1][6][:,indicesE[6]]
              teammate_killed_teamdist_base=feature[0][playerTeam[ff]-1][6][:,indicesB[6]]
              teammate_killed_teamdist_isSet = 1
          else:
              teammate_killed_teamdist = numpy.vstack((teammate_killed_teamdist,feature[0][playerTeam[ff]-1][6][:,indicesE[6]]))
              teammate_killed_teamdist_base = numpy.vstack((teammate_killed_teamdist_base,feature[0][playerTeam[ff]-1][6][:,indicesB[6]]))
              
      if len(feature[0][playerTeam[ff]-1][7]) > 0:               
          if enemy_killed_teamdist_isSet == 0:
              enemy_killed_teamdist=feature[0][playerTeam[ff]-1][7][:,indicesE[7]]
              enemy_killed_teamdist_base=feature[0][playerTeam[ff]-1][7][:,indicesB[7]]
              enemy_killed_teamdist_isSet = 1
          else:
              enemy_killed_teamdist = numpy.vstack((enemy_killed_teamdist,feature[0][playerTeam[ff]-1][7][:,indicesE[7]]))
              enemy_killed_teamdist_base = numpy.vstack((enemy_killed_teamdist_base,feature[0][playerTeam[ff]-1][7][:,indicesB[7]]))
              
      if len(feature[0][playerTeam[ff]-1][8]) > 0:               
          if death_after_kill_isSet == 0:
              death_after_kill=feature[0][playerTeam[ff]-1][8][:,indicesE[8]]
              death_after_kill_base=feature[0][playerTeam[ff]-1][8][:,indicesB[8]]
              death_after_kill_isSet = 1
          else:
              death_after_kill = numpy.vstack((death_after_kill,feature[0][playerTeam[ff]-1][8][:,indicesE[8]]))
              death_after_kill_base = numpy.vstack((death_after_kill_base,feature[0][playerTeam[ff]-1][8][:,indicesB[8]]))

      earlyCreepScore[ff] = feature[0][playerTeam[ff]-1][9]
      earlyJGScore[ff] = feature[0][playerTeam[ff]-1][10]
      JGParticRate[ff] = feature[0][playerTeam[ff]-1][11]/feature[0][playerTeam[ff]-1][12]
      numJG[ff] = feature[0][playerTeam[ff]-1][16]
      numBot[ff] = feature[0][playerTeam[ff]-1][17]
      numDSupp[ff] = feature[0][playerTeam[ff]-1][18]
      numDCarry[ff] = feature[0][playerTeam[ff]-1][19]
      assistsAtEnd[ff] = feature[0][playerTeam[ff]-1][28]  #NEED TO CHANGE THIS TO PERCENT ASSIST AT END!! DO NOT USE YET!!

  drag_trigg_kill_metric = (numpy.nanmean(drag_trigg_kill)-numpy.nanmean(drag_trigg_kill_base))*60*1000
  baron_trigg_purchase_metric = (numpy.nanmean(baron_trigg_purchase)-numpy.nanmean(baron_trigg_purchase_base))*60*1000
  drag_trigg_wardplaced_metric = (numpy.nanmean(drag_trigg_wardplaced)-numpy.nanmean(drag_trigg_wardplaced_base))*60*1000
  drag_trigg_wardkilled_metric = (numpy.nanmean(drag_trigg_wardkilled)-numpy.nanmean(drag_trigg_wardkilled_base))*60*1000
  inhib_trigg_purchase_metric = (numpy.nanmean(inhib_trigg_purchase)-numpy.nanmean(inhib_trigg_purchase_base))*60*1000
  team_dist_time_metric = (numpy.nanmean(team_dist_time)-numpy.nanmean(team_dist_time_base))
  teammate_killed_teamdist_metric = (numpy.nanmean(teammate_killed_teamdist)-numpy.nanmean(teammate_killed_teamdist_base))
  #enemy_killed_teamdist_metric Currently not working (effect in wrong direction), fix later:  
  enemy_killed_teamdist_metric = (numpy.nanmean(enemy_killed_teamdist)-numpy.nanmean(enemy_killed_teamdist_base))
  death_after_kill_metric = (numpy.nanmean(death_after_kill_base)-numpy.nanmean(death_after_kill))*60*1000
  earlyCreepScore_metric = numpy.nanmean(earlyCreepScore)
  earlyJGScore_metric = numpy.nanmean(earlyJGScore)
  #JGParticRate_metric = numpy.nanmean()
  numJG_metric = numJG
  numBot_metric = numBot
  numDSupp_metric = numDSupp
  numDCarry_metric = numDCarry
  #assistsAtEnd_metric = numpy.nanmean(assistsAtEnd)
  playerEffect = [None]*11
  playerEffect[0] = drag_trigg_kill_metric
  playerEffect[1] = baron_trigg_purchase_metric
  playerEffect[2] = drag_trigg_wardplaced_metric
  playerEffect[3] = drag_trigg_wardkilled_metric
  playerEffect[4] = inhib_trigg_purchase_metric
  playerEffect[5] = team_dist_time_metric
  playerEffect[6] = teammate_killed_teamdist_metric
  playerEffect[7] = enemy_killed_teamdist_metric
  playerEffect[8] = death_after_kill_metric
  playerEffect[9] = earlyCreepScore_metric
  playerEffect[10] = earlyJGScore_metric
  
  advice = [None]*11
  advice[0] = "Always contest the dragon.<br>Killing the dragon before winning a fight is risky."
  advice[1] = "Consider retreating after killing the baron.<br>Healing and regrouping for an attack is more effective."
  advice[2] = "Always maintain vision on the dragon.<br>This is especially true when he is about to spawn."
  advice[3] = "Scan for and kill any enemy wards when engaging the dragon.<br>Removing the enemy's vision will ensure your success."
  advice[4] = "Consider retreating after destroying an inhibitor.<br>Pushing further without regrouping and healing is risky."  
  advice[5] = "Stay close to your team in the middle and late game stages.<br>Pushing together ensures success."
  advice[6] = "Don't let yourself or your teammates get caught alone.<br>Fight together to increase chances of winning team fights."
  advice[7] = "Don't engage enemies on your own.<br>Chances are high that enemies will team up against you."
  advice[8] = "Don't make risky plays that cause you to die.<br>Greedy plays can lead to fed opponents."
  advice[9] = "Your Creep Score can be improved.<br>Try to get used to last-hitting minions for extra gold."
  advice[10] = "Your jungler is not clearing fast enough.<br>Consider refining your joungle routes."
  
  xlabels = [None]*11  
  xlabels[0] = "Dragon contest rate"  
  xlabels[1] = "Regroup rate after Baron"   
  xlabels[2] = "Vision acquisition rate near Dragon time"   
  xlabels[3] = "Enemy vision removal rate near Dragon time"   
  xlabels[4] = "Regroup rate after Inhibitor Kill"   
  xlabels[5] = "Average team closeness"   
  xlabels[6] = "Team closeness on teammate killed"   
  xlabels[7] = "Team closeness on enemy killed"   
  xlabels[8] = "Death rate after kill"   
  xlabels[9] = "Creep Score in early game"   
  xlabels[10] = "Jungle score in early game"   
  
  weights = [None]*11
  weights[0] = 0.25
  weights[1] = 0.1
  weights[2] = 0.5
  weights[3] = 0.05
  weights[4] = 0.25
  weights[5] = 0.5
  weights[6] = 0.33
  weights[7] = 0.1
  weights[8] = 0.33
  weights[9] = 0.20
  weights[10] = 0.15
  results_list, meanEffect, stDev = load_effect_means(2000)
  numstDevAway=[]
  importance=[]
  for r, result in enumerate(results_list):
      if abs(meanEffect[r]) < 1: #if it's smaller than magnitude 1, it's probably a rate, so multipy by 60,000 ms
          meanEffect[r] = meanEffect[r]*60*1000
          results_list[r] = results_list[r]*60*1000
          stDev[r] = stDev[r]*60*1000
      numstDevAway.append((meanEffect[r] - playerEffect[r]) / stDev[r] )
      importance.append(numstDevAway[r]*weights[r])
  sortedImportance = numpy.sort(importance)[::-1]
  sortIndex = numpy.argsort(importance)[::-1]
  sortIndex = numpy.delete(sortIndex,numpy.where(sortIndex==7))  #remove enemy_killed metric since that doesn't work well
  sortIndex = numpy.delete(sortIndex,numpy.where(numpy.isnan(sortedImportance)))  #remove enemy_killed metric since that doesn't work well
  
  
  ###################################
  #    PLOT RESULTS ---  START      #  
  ###################################
  
  # output to static HTML file

  
  crosshair1 = CrosshairTool(
      dimensions=["height"])

  crosshair2 = CrosshairTool(
      dimensions=["height"])

  crosshair3 = CrosshairTool(
      dimensions=["height"])


  # create a new plot with a title and axis labels
  hist, edges = numpy.histogram(results_list[sortIndex[0]], density=True, bins=50)    
  p1 = figure(min_border=1, x_axis_label=xlabels[sortIndex[0]], y_axis_label="y",tools=[crosshair1],width=400,height=350,toolbar_location=None)
  p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="#036564", line_color="#033649")
  p1.line([playerEffect[sortIndex[0]],playerEffect[sortIndex[0]]],[0,numpy.max(hist)*1.05],line_width=2)  
  g1=p1.scatter(x=playerEffect[sortIndex[0]],y=[numpy.max(hist)*1.05],marker="inverted_triangle",size=20)
  p1.yaxis.major_label_text_font_size='0pt'
  p1.xaxis.major_label_text_font_size='0pt'
  p1.yaxis.axis_label_text_color='#ffffff'

  advice1 = advice[sortIndex[0]]
  
  hist, edges = numpy.histogram(results_list[sortIndex[1]], density=True, bins=50)
  p2 = figure(min_border=1, x_axis_label=xlabels[sortIndex[1]], y_axis_label='y',tools=[crosshair2],width=400,height=350,toolbar_location=None) 
  p2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="#036564", line_color="#033649")
  p2.line([playerEffect[sortIndex[1]],playerEffect[sortIndex[1]]],[0,numpy.max(hist)*1.05],line_width=2)  
  g2=p2.scatter(x=playerEffect[sortIndex[1]],y=[numpy.max(hist)*1.05],marker="inverted_triangle",size=20)
  p2.yaxis.major_label_text_font_size='0pt'
  p2.xaxis.major_label_text_font_size='0pt'
  p2.yaxis.axis_label_text_color='#ffffff'
  advice2 = advice[sortIndex[1]]
  
  hist, edges = numpy.histogram(results_list[sortIndex[2]], density=True, bins=50)
  p3 = figure(min_border=1, x_axis_label=xlabels[sortIndex[2]], y_axis_label='y',tools=[crosshair3],width=400,height=350,toolbar_location=None)  
  p3.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="#036564", line_color="#033649")
  p3.line([playerEffect[sortIndex[2]],playerEffect[sortIndex[2]]],[0,numpy.max(hist)*1.05],line_width=2)
  g3=p3.scatter(x=playerEffect[sortIndex[2]],y=[numpy.max(hist)*1.05],marker="inverted_triangle",size=20)
  p3.yaxis.major_label_text_font_size='0pt'
  p3.xaxis.major_label_text_font_size='0pt'
  p3.yaxis.axis_label_text_color='#ffffff'
  advice3 = advice[sortIndex[2]]  
  hover1 = HoverTool(
      renderers=[g1],
      tooltips=[
          ("index", "$index"),
          ("(x,y)", "(@xD1, @yD1)"),
          ("desc", "@desc"),
      ],
      line_policy='nearest',
      point_policy = 'snap_to_data'
  )
  hover2 = HoverTool(
      renderers=[g2],
      tooltips=[
          ("index", "$index"),
          ("(x,y)", "(@xD2, @yD2)"),
          ("desc", "@desc"),
      ],
      line_policy='nearest',
      point_policy = 'snap_to_data'
  )
  hover3 = HoverTool(
      renderers=[g3],
      tooltips=[
          ("index", "$index"),
          ("(x,y)", "(@xD3, @yD3)"),
          ("desc", "@desc"),
      ],
      line_policy='nearest',
      point_policy = 'snap_to_data'
  )        
  
  #p1.add_tools(hover1)
  #p2.add_tools(hover2)
  #p3.add_tools(hover3)
   
  ft1a = file_html(p1,CDN,'title')
  ft2a = file_html(p2,CDN,'title')
  ft3a = file_html(p3,CDN,'title')

  return render_template("coachadvice.html",ft1a=ft1a,ft2a=ft2a,ft3a=ft3a,advice1=advice1,advice2=advice2,advice3=advice3)
  
  
  
  
  