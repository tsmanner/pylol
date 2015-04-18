'''
This file contains API wrappers for every League Of Legends API.  Currently, only a few are implemented
    but I will continue to add more over the next weeks, until the LeagueOfLegendsApi object can make
    requests to all of them.
'''
from   multiprocessing import Queue, Process, Value
from   loldata         import *
import requests, sys, time
import sqlite3 as sql

# API Request types
CHAMPION_API_REQ     =  0
CURRENT_GAME_REQ     =  1
FEATURED_GAMES_REQ   =  2
GAME_REQ             =  3
LEAGUE_REQ           =  4
# LoL Static Data API
CHAMPION_ALL_REQ     =  5
CHAMPION_ALL_IMM_REQ =  6

STATUS_REQ           =  7
MATCH_REQ            =  8
HISTORY_REQ          =  9
STATS_REQ            = 10
SUMMONER_IMM_REQ     = 11
TEAM_REQ             = 12


class LeagueOfLegendsApi:
    def __init__(self, parent, key, region, callback, db=":memory:"):
        self.parent = parent
        self.key    = key
        self.region = region
        self.db     = db
        # Register a data callback for this api, callback function must take a tuple as the only argument
        #   The tuple has two elements: request_id and data(a loldata class)
        self.data_callback = callback
        # Requester - Handles all http requests.  Uses multiprocessing to run in the background and
        #                 throttles the number of requests to ensure we stay within the bourndaries
        self.requester = Requester(self, callback=self.pushCompletedRequestData)
        # TODO optionally init db per api? Or do all w/db or wout/db. If a user wants additional
        #   data anywhere, they will need to make seperate table for that data and relate it to
        #   the tables created by each api object as described by the tables in loldata.py.
        self.summoner        = SummonerApi(     self)
        self.champion        = ChampionApi(     self)
        self.current_game    = CurrentGameApi(  self)
        self.featured_games  = FeaturedGamesApi(self)
        self.game            = GameApi(         self)
        self.league          = LeagueApi(       self)
        self.lol_static_data = LoLStaticDataApi(self)
        self.lol_status      = LoLStatusApi(    self)
        self.match           = MatchApi(        self)
        self.match_history   = MatchHistoryApi( self)
        self.stats           = StatsApi(        self)
        self.team            = TeamApi(         self)

        # All the requests + db writes run multithreaded.  These lists let us track which request IDs
        #   correspond to which APIs so we can 
        self.pending_champion        = []
        self.pending_current_game    = []
        self.pending_featured_games  = []
        self.pending_game            = []
        self.pending_league          = []
        self.pending_lol_static_data = []
        self.pending_lol_status      = []
        self.pending_match           = []
        self.pending_match_history   = []
        self.pending_stats           = []
        self.pending_team            = []

    def getData(self, req_type, *args, **kwargs):
        if   req_type == HISTORY_REQ:
            req_id = self.match_history.getHistory(*args, **kwargs)
            self.pending_match_history.append(req_id)
            return req_id
        elif req_type == CHAMPION_ALL_REQ:
            req_id = self.lol_static_data.getAllChampions(*args, **kwargs)
            self.pending_lol_static_data.append(req_id)
            return req_id
        elif req_type == CHAMPION_ALL_IMM_REQ:
            return self.lol_static_data.getAllChampionsImm(*args, **kwargs)
        elif req_type == STATS_REQ:
            req_id = self.stats.getStatSummary(*args, **kwargs)
            self.pending_stats.append(req_id)
            return req_id
        elif req_type == STATUS_REQ:
            req_id = self.lol_status.getStatus(self.region)
            self.pending_lol_status.append(req_id)
            return req_id
        elif req_type == SUMMONER_IMM_REQ:
            return self.summoner.getSummoner(*args, **kwargs)

    def pushCompletedRequestData(self, req):
        self.data_callback((req.id, req.data))

#        print(req.data)
        # Requester pushes completed requests in here, we'll figure out where they belong on this end
#        if req.id in self.pending_champion:
#            pass #TODO DO STUFF
#        elif req.id in self.pending_current_game:
#            pass #TODO DO STUFF
#        elif req.id in self.pending_featured_games:
#            pass #TODO DO STUFF
#        elif req.id in self.pending_game:
#            pass #TODO DO STUFF
#        elif req.id in self.pending_league:
#            pass #TODO DO STUFF
#        elif req.id in self.pending_lol_static_data:
#            print("LoL Static Data Request Completed")
#            champ_ids = [int(key) for key in req.data.keys()]
#            champ_ids.sort()
#            [print(req.data[str(champ_id)]) for champ_id in champ_ids]
#            self.data_callback((req.id, req.data))
#        elif req.id in self.pending_lol_status:
#            print("Status Request Completed")
#            print(req.data)
#            self.data_callback((req.id, req.data))
#        elif req.id in self.pending_match:
#            pass #TODO DO STUFF
#        elif req.id in self.pending_match_history:
#            print("Match History Request Completed")
#            [print(match) for match in req.data]
#            self.data_callback((req.id, req.data))
#        elif req.id in self.pending_stats:
#            print("Stats Request Completed")
#            print(req.data)
#            self.data_callback((req.id, req.data))
#        elif req.id in self.pending_team:
#            pass #TODO DO STUFF

    def cleanup(self):
        self.requester.cleanup()


# Classes for each API available for League of Legends
# Base class for all League of Legends API wrappers
class LeagueOfLegendsApiBase:
    def __init__(self, parent):
        self.parent    = parent
        self.api_root  = 'https://na.api.pvp.net'

    def initDbTable(self):
        conn = sql.connect(self.parent.db)
        c    = conn.cursor()
        for item in self.classes:
            c.execute(item.getSqlTableFormatStr())
        conn.commit()
        conn.close()
        

class ChampionApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.url = '{api_root}/api/lol/{region}/v1.2/champion?{key}'
        self.classes = [ChampionListDto,
                        ChampionDto]
#        self.initDbTable()


class CurrentGameApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.classes = []
        self.initDbTable()


class FeaturedGamesApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.classes = []
        self.initDbTable()


class GameApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.classes = []
        self.initDbTable()


class LeagueApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.classes = []
        self.initDbTable()


class LoLStaticDataApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.api_root = 'https://global.api.pvp.net'
        self.url = '{api_root}/api/lol/static-data/{region}/v1.2/{category}{id}?{options}'
        self.classes = [ChampionData            ,\
                        ImageData               ,\
                        ChampionInfoData        ,\
                        ChampionPassiveData     ,\
                        ChampionRecommendedData ,\
                        ChampionItemData        ,\
                        ChampionSkinData        ,\
                        ChampionSpellData       ,\
                        LevelTipData            ,\
                        SpellVarsData           ,\
                        ChampionStatsData        ]
        self.initDbTable()

    def getAllChampionsImm(self, champData=None, dataById=True):
        options = []
        if champData:
            options.append('champData=' + ','.join(champData))
        if dataById:
            options.append('dataById=true')
        options_str = ''
        options.append('api_key='+self.parent.key)
        if len(options) > 1:
            options_str = '&'.join(options)
        elif len(options) == 1:
            options_str = options[0]
        req_str = self.url.format(api_root=self.api_root    ,\
                                  region=self.parent.region ,\
                                  category='champion'       ,\
                                  id=''                     ,\
                                  options=options_str        )
        return self.parent.requester.getImmediate(req_str)

    def getAllChampions(self, champData=None, dataById=True):
        options = []
        if champData:
            options.append('champData=' + ','.join(champData))
        if dataById:
            options.append('dataById=true')
        options_str = ''
        options.append('api_key='+self.parent.key)
        if len(options) > 1:
            options_str = '&'.join(options)
        elif len(options) == 1:
            options_str = options[0]
        req_str = self.url.format(api_root=self.api_root    ,\
                                  region=self.parent.region ,\
                                  category='champion'       ,\
                                  id=''                     ,\
                                  options=options_str)
        return self.parent.requester.get(CHAMPION_ALL_REQ, self.parent.db, req_str)

    def getChampion(self, champion_id):
        req_str = None
        if region:
            req_str = self.url.format(api_root=self.api_root, region='/' + self.parent.region, key=self.parent.key)
        else:
            req_str = self.url.format(api_root=self.api_root, region='', key=self.parent.key)
        return self.parent.requester.get(req_str)


class LoLStatusApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.api_root = 'http://status.leagueoflegends.com'
        self.url = '{api_root}/shards{region}'
        self.classes = []
        self.initDbTable()

    def getStatus(self, region=None):
        req_str = None
        if region:
            req_str = self.url.format(api_root=self.api_root, region='/' + region, key=self.parent.key)
        else:
            req_str = self.url.format(api_root=self.api_root, region='', key=self.parent.key)
        return self.parent.requester.get(STATUS_REQ, self.parent.db, req_str)


class MatchApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.classes = []
        self.initDbTable()

##################################################################################################
# This one's a doozy... Lots of data in here, which requires several tables added to the database
#   The constructor needs to create the tables if they don't exist yet.  Tables:
#   <table_name>              (<match_on/data_association>)
#   match_summaries           (summoner_id)
#   participants              (match_id)
#   participant_identities    (match_id)
#   players                   (match_id)
#   masteries                 (match_id, participant_id)
#   runes                     (match_id, participant_id)
#   participant_stats         (match_id, participant_id) - not in data class
#   participant_timelines     (match_id, participant_id) - not in data class
#   participant_timeline_data (match_id, participant_id, data_point) - not in data class
##################################################################################################
class MatchHistoryApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.url = '{api_root}/api/lol/{region}/v2.2/matchhistory/{summonerId}?{options}'
        self.classes = [MatchSummary        ,\
                        ParticipantIdentity ,\
                        Participant         ,\
                        Mastery             ,\
                        Rune                ,\
                        ParticipantStats    ,\
                        ParticipantTimeline  ]
        self.initDbTable()

    def getHistory(self, summoner, champions=[], queues=[], begin=None, end=None):
        options = []
        options_str = ''
        champions_str = ','.join(champions)
        queues_str    = ','.join(queues)
        if champions_str != '':
            options.append('championIds='  + champions_str)
        if queues_str != '':
            options.append('rankedQueues=' + queues_str)
        if begin:
            options.append('beginIndex='   + str(begin))
        if end:
            options.append('endIndex='     + str(end))
        options.append('api_key='+self.parent.key)
        if len(options) > 1:
            options_str = '&'.join(options)
        elif len(options) == 1:
            options_str = options[0]
        return self.parent.requester.get(HISTORY_REQ, self.parent.db                     ,\
                                         self.url.format(api_root   = self.api_root      ,\
                                                         region     = self.parent.region ,\
                                                         summonerId = summoner['id']     ,\
                                                          options    = options_str      ) )


class StatsApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.url = '{api_root}/api/lol/{region}/v1.3/stats/by-summoner/{summonerId}/{stats_type}?{options}'
        self.classes = [PlayerStatSummary      ,\
                        AggregatedStats         ]
        self.initDbTable()

    def getStatSummary(self, summoner, season='SEASON2015'):
        options = []
        options_str = ''
        options.append('api_key=' + self.parent.key)
        options.append('season=' + season)
        if len(options) > 1:
            options_str = '&'.join(options)
        elif len(options) == 1:
            options_str = options[0]
        return self.parent.requester.get(STATS_REQ, self.parent.db                       ,\
                                         self.url.format(api_root   = self.api_root      ,\
                                                         region     = self.parent.region ,\
                                                         summonerId = summoner['id']     ,\
                                                         stats_type = 'summary'          ,\
                                                         options    = options_str      )  )
        

class SummonerApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.url = '{api_root}/api/lol/{region}/v1.4/summoner/by-name/{summonerName}?api_key={key}'
        self.classes = [SummonerApiData]
        self.initDbTable()

    def getSummoner(self, name):
        name_hash = ''.join(name.lower().split())
        data = self.parent.requester.getImmediate(self.url.format(api_root=self.api_root    ,\
                                                                  region=self.parent.region ,\
                                                                  summonerName=name_hash    ,\
                                                                  key=self.parent.key       ))
        if data.status_code == 200:
            summoner = SummonerApiData(data.json()[name_hash])
            summoner.write(self.parent.db)
            return summoner
        else:
            return False


class TeamApi(LeagueOfLegendsApiBase):
    def __init__(self, *args, **kwargs):
        LeagueOfLegendsApiBase.__init__(self, *args, **kwargs)
        self.classes = []
        self.initDbTable()


###########################################################
# Request wrapper used for throttling/queuing requests    #
###########################################################
MAX_PER_TEN_SECS = 10
MAX_PER_TEN_MINS = 500

REQUEST_NOT_STARTED = 0
REQUEST_IN_PROGRESS = 1
REQUEST_COMPLETE    = 2
REQUEST_ABORTED     = 3

class Request:
    def __init__(self, req_id, req_type, *args):
        self.id       = req_id
        self.req_type = req_type
        self.q        = Queue()
        self.proc     = Process(target=multiRequestGet, args=(self.q, self.req_type) + tuple(args))
        self.time     = None
        self.data     = None
        self.state    = REQUEST_NOT_STARTED

    def evaluate(self):
        if   self.state == REQUEST_COMPLETE:
            return
        elif self.state == REQUEST_IN_PROGRESS:
            if not self.q.empty():
                self.data = self.q.get()
                self.proc.join()
                self.q    = None
                self.proc = None
                self.state = REQUEST_COMPLETE

    def start(self):
        self.time  = time.time()
        self.state = REQUEST_IN_PROGRESS
        self.proc.start()

    def terminate(self):
        self.state = REQUEST_ABORTED
        self.proc.terminate()


class Requester:
    def __init__(self, parent, callback):
        self.parent        = parent
        self.data_callback = callback
        self.request_count = 0
        self.requests_per_ten_secs = []
        self.requests_per_ten_mins = []
        # All requests go into pending, then are pulled out and moved to active if there is room
        #   depending on the throttling scheme.  Once done, they're put in completed_requests
        #   until the object that initiated it has retrieved the data and 10 minutes has passed
        self.pending_requests   = []
        self.active_requests    = []

    def evaluate(self):
        # Check wether we have any request timers that are older than 10 [seconds/minutes]. If we do,
        #   remove those timers, which will open up a slot to start a new request
        for req_time in self.requests_per_ten_secs:
            if req_time + 10 < time.time():
                self.requests_per_ten_secs.remove(req_time)
        for req_time in self.requests_per_ten_mins:
            if req_time + 600 < time.time():
                self.requests_per_ten_mins.remove(req_time)
        # While we have bandwidth for more requests, move them from pending to active and start them
        while len(self.requests_per_ten_secs) < MAX_PER_TEN_SECS and \
              len(self.requests_per_ten_mins) < MAX_PER_TEN_MINS and \
              len(self.pending_requests) > 0                         :
            self.active_requests.append(self.pending_requests[-1])
            self.pending_requests.pop()
            self.active_requests[-1].start()
            # Add new timers to the requests_per_ten_[secs,mins] lists
            self.requests_per_ten_secs.append(self.active_requests[-1].time)
            self.requests_per_ten_mins.append(self.active_requests[-1].time)
        # Check our active requests for any that have finished.  If they have, join them and move
        #   them to the finished list
#        if len(self.active_requests):
#            print('.', end='')
#            sys.stdout.flush()
        for req in self.active_requests:
            req.evaluate()
            if req.state == REQUEST_COMPLETE:
#                print()
#                print("Request complete!")
                sys.stdout.flush()
                self.active_requests.remove(req)
                self.data_callback(req)

    def get(self, req_type, db, *args, **kwargs):
        request_id = self.request_count
        request = Request(request_id, req_type, db, *args)
        self.pending_requests.append(request)
#        print(request_id, *args)
        self.request_count += 1
        return request_id

    def getImmediate(self, *args):
        return requests.get(*args)

    def cleanup(self):
        self.pending_requests = []
        for req in self.active_requests:
            req.terminate()


# This is the entry point for multithreaded requests.
#   It handles the HTTP request as well as writing the database
def multiRequestGet(data_q, req_type, db, *args):
#    print(req_type, args)
    req_data = requests.get(*args)
    # Requester pushes completed requests in here, we'll figure out where they belong on this end
    if   req_type == CHAMPION_API_REQ:
        pass #TODO DO STUFF
    elif req_type == CURRENT_GAME_REQ:
        pass #TODO DO STUFF
    elif req_type == FEATURED_GAMES_REQ:
        pass #TODO DO STUFF
    elif req_type == GAME_REQ:
        pass #TODO DO STUFF
    elif req_type == LEAGUE_REQ:
        pass #TODO DO STUFF
    elif req_type == CHAMPION_ALL_REQ:
#        print('LoL Static Data Request Completed:', req.data)
        if req_data.status_code == 200:
            obj = ChampionDataList(req_data.json())
            obj.write(db)
            champ_ids = [int(key) for key in obj.keys()]
            champ_ids.sort()
#            [print(obj[str(champ_id)]) for champ_id in champ_ids]
    elif req_type == STATUS_REQ:
#        print("Status Request Completed:", req.data)
        if req_data.status_code == 200:
            obj = LoLStatus(req_data.json())
#            print(obj)
    elif req_type == MATCH_REQ:
        pass #TODO DO STUFF
    elif req_type == HISTORY_REQ:
#        print("Match History Request Completed:", req.data)
        if req_data.status_code == 200:
            summoner_id = int(args[0].split('/')[-1].split('?')[0])
            data_dict = req_data.json()
            if len(data_dict):
                obj = PlayerHistory(data_dict['matches'], summoner_id)
                obj.write(db)
#                    [print(match) for match in obj]
            else:
                obj = PlayerHistory([], summoner_id)
        elif req.data.status_code == 404:
            obj = PlayerHistory([], summoner_id)
    elif req_type == STATS_REQ:
#        print("Stats Request Completed:", req.data)
        if req_data.status_code == 200:
            obj = PlayerStatsSummaryList(req_data.json())
            obj.write(db)
#            print(obj)
    elif req_type == TEAM_REQ:
        pass #TODO DO STUFF

    data_q.put(obj)
    return

