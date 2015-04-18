from   tkinter import *
from   lolapi  import *
from   loldata import SummonerApiData
import sqlite3 as sql
import os
import tkinter as tk

positions = ['top', 'jungle', 'mid', 'support', 'adc']

class Positions:
    def __init__(self, master):
        self.master = master
        self.master.wm_title('Positions')
        self.master.focus_force()

        self.db = 'positions.db'
        if not os.path.exists(self.db):
            # Create the db if it doesn't exist
            open(self.db, 'w').close()

        # Pointers to API interface:
        #   API       - Interface object for game api.  Builds the request url and initiates a new
        #                   Request through the Requester
        # No db passed in to api_summoner, we need an extra column for user(os.getlogin())
        api_key = '11f66938-9351-4220-9c39-f8d61fc25732'
        self.api = LeagueOfLegendsApi(self, api_key, 'na', self.apiDataReturn, self.db)
        # Pending data request_id lists, one for each API object
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

        self.num_matches = {}

        self.initDatabase()
        self.setupGui()

        # Check if this user has signed in before.  If they have, load up the last summoner they were inspecting
        conn = sql.connect(self.db)
        c    = conn.cursor()
        summoners_data = list(c.execute("SELECT * from summoners WHERE id=(\
                                          SELECT summoner_id FROM users WHERE user=?)",(os.getlogin(),)))
#        print(summoners_data)
        if len(summoners_data) == 1:
            data_dict = {pair[0]:pair[1] for pair in zip(SummonerApiData.getKeys(), summoners_data)}
            self.summoner = SummonerApiData(data_dict)
            self.checkSummonerName()
        else:
            self.promptForSummonerName()
        conn.close()

        self.evaluate()

    # Database initialization(THIS USER APPLICATION ONLY).
    #   Here we add the keys, champion_ranks, and users tables, which are the db tables
    #   which are extensions to the base lolapi.py database
    def initDatabase(self):
        self.disp_data = {}
        # Then init it TODO
        conn = sql.connect(self.db)
        c    = conn.cursor()
        # Create all the database tables if they're not in the db file yet.
        # LoL API Key registration table
        c.execute('CREATE TABLE IF NOT EXISTS    keys           (\
                     summoner_id real NOT NULL                  ,\
                     key text         NOT NULL                  ,\
                     UNIQUE(summoner_id, key)                    \
                   )')
        # Champion ranking table
        c.execute('CREATE TABLE IF NOT EXISTS    champion_ranks (\
                     champion text    NOT NULL                  ,\
                     position text    NOT NULL                  ,\
                     rank real        NOT NULL                  ,\
                     summoner_id real NOT NULL                  ,\
                     UNIQUE(champion, position, summoner_id)     \
                   )')
        c.execute('CREATE TABLE IF NOT EXISTS users (\
                     user        text NOT NULL ,\
                     summoner_id real NOT NULL ,\
                     UNIQUE(user)               \
                  )')


        champ_names = [item[0] for item in c.execute('SELECT name FROM champions')]
        champ_names.sort()

        if len(champ_names) == 0:
            response = self.api.getData(CHAMPION_ALL_IMM_REQ)
            if response.status_code == 200:
                champ_data = ChampionDataList(response.json())
                champ_ids = [int(key) for key in champ_data.keys()]
                champ_ids.sort()
                champ_data.write(self.db)
                champ_names = [item[0] for item in c.execute('SELECT name FROM champions')]
                champ_names.sort()
#        else:
#            self.pending_champion.append(self.api.getData(CHAMPION_ALL_REQ))

        self.all_champions  = ["Champion..."]
        self.all_champions += [champ for champ in champ_names]

        conn.commit()
        conn.close()

    def setupGui(self):
        conn = sql.connect(self.db)
        c    = conn.cursor()

        # These UI elements are temporarily removed.  This application originally generated a very simply
        #   local database and stored simply a ranked list of champions there.  The ranking was done
        #   by hand and the champion list was from a text file I copied from a league wiki online. EW.
        '''
        self.menu_frame_1 = Frame(self.master)
        self.menu_frame_1.pack(side=TOP,fill=X)
        self.view = Button(self.menu_frame_1,text="View: positions")
        self.view.pack(side=LEFT)
        self.keyb = Button(self.menu_frame_1,text="Register API Key",command=self.registerApiKey)
        self.keyb.pack(side=LEFT)

        self.champ_var = StringVar(self.master)
        self.champ_var.set(self.all_champions[0])
        self.champs = OptionMenu(self.menu_frame_1,self.champ_var,*self.all_champions)
        self.champs.config(width=14)
        self.champs.pack(side=LEFT)

        self.all_positions = ["Position...","Top","Jungle","Mid","Support","ADC"]
        self.position_var = StringVar(self.master)
        self.position_var.set(self.all_positions[0])
        self.position_in = OptionMenu(self.menu_frame_1,self.position_var,*self.all_positions)
        self.position_in.config(width=8)
        self.position_in.pack(side=LEFT)

        self.add  = Button(self.menu_frame_1,text="Add",command=self.addChampion)
        self.add.pack(side=LEFT)
        '''

        self.menu_frame_2 = Frame(self.master)
        self.menu_frame_2.pack(side=TOP,fill=X)

        self.champ_var = StringVar(self.master)
        self.champ_var.set(self.all_champions[0])
        self.champs = OptionMenu(self.menu_frame_2,self.champ_var,*self.all_champions)
        self.champs.config(width=14)
        self.champs.pack(side=LEFT)

        self.ch_summoner = Button(self.menu_frame_2,text="Summoner",command=self.promptForSummonerName)
        self.ch_summoner.pack(side=LEFT)
        self.statusb = Button(self.menu_frame_2,text="Status",command=self.refreshStatus)
        self.statusb.pack(side=LEFT)
        self.histb = Button(self.menu_frame_2,text="History",command=self.refreshHistory)
        self.histb.pack(side=LEFT)
        self.statsb = Button(self.menu_frame_2,text="Stats",command=self.refreshStatSummary)
        self.statsb.pack(side=LEFT)
        self.champb = Button(self.menu_frame_2,text="Champions",command=self.refreshChampions)
        self.champb.pack(side=LEFT)
        
        self.magic = Button(self.menu_frame_2,text="Magic!",command=self.analyzeSummonerHistory)
        self.magic.pack(side=LEFT)

        self.label_frame = Frame(self.master)
        self.label_frame.pack(side=TOP,fill=X)
        self.labels = {}

        self.table_frame = Frame(self.master)
        self.table_frame.pack(side=TOP,fill=X)
        self.tables = {}

#        self.positionView()
        self.ratingsView()

        self.status_frame = Frame(self.master)
        self.status_frame.pack(side=TOP,fill=X)
        self.status = Label(self.status_frame,text="Welcome")
        self.status.pack()
        conn.close()

    # Any functionality that must be run or polled periodically is called here, with an adjustable
    #   timer, courtesy of TK
    def evaluate(self):
        self.api.requester.evaluate()
        self.master.after(100, self.evaluate)

    # This function isn't broken out current to the user, For now it defaults to registering my personal
    #   key.  This function exists to be expanded to allow any user to enter their own key.  A release
    #   version of this code would NOT include my API key as a default, to help keep people from hitting
    #   HTTP Status Code 429 - Rate Limit Exceeded
    def registerApiKey(self,event=None):
        conn = sql.connect(self.db)
        c = conn.cursor()
        c.execute('DELETE FROM keys WHERE summoner_id=?',(self.summoner['id'],))
        c.execute('INSERT INTO keys VALUES (?,?)',(self.summoner['id'],'11f66938-9351-4220-9c39-f8d61fc25732'))
        conn.commit()
        conn.close()
        self.api.key = '11f66938-9351-4220-9c39-f8d61fc25732'
#        print('Registered API key for',self.summoner['name'],'11f66938-9351-4220-9c39-f8d61fc25732')

    def refreshTables(self):
        return
#        conn = sql.connect(self.db)
#        c    = conn.cursor()
#        for position in positions:
#            self.disp_data[position] = [item[0] for item in c.execute("SELECT * FROM champion_ranks WHERE position=? AND summoner_id=\
#                                 (SELECT id FROM summoners WHERE user=?) ORDER BY rank",(position,os.getlogin()))]
#            self.tables[position].delete(0,END)
#            [self.tables[position].insert(END,champ_data) for champ_data in self.disp_data[position]]
#        conn.close()

    # This function is not ever called right now, it will eventually be used to whos champion rankings
    #   by lane/position based on the analysis done further down of a summoners match history
    def positionView(self):
        self.tables['top']     = Listbox(self.table_frame,width=12,font='courier 9',selectmode=EXTENDED)
        self.tables['jungle']  = Listbox(self.table_frame,width=12,font='courier 9',selectmode=EXTENDED)
        self.tables['mid']     = Listbox(self.table_frame,width=12,font='courier 9',selectmode=EXTENDED)
        self.tables['support'] = Listbox(self.table_frame,width=12,font='courier 9',selectmode=EXTENDED)
        self.tables['adc']     = Listbox(self.table_frame,width=12,font='courier 9',selectmode=EXTENDED)

        self.labels['top']     = Label(self.label_frame,text="Top"    ,width=12,font='courier 9')
        self.labels['jungle']  = Label(self.label_frame,text="Jungle" ,width=12,font='courier 9')
        self.labels['mid']     = Label(self.label_frame,text="Mid"    ,width=12,font='courier 9')
        self.labels['support'] = Label(self.label_frame,text="Support",width=12,font='courier 9')
        self.labels['adc']     = Label(self.label_frame,text="ADC"    ,width=12,font='courier 9')
        for position in positions:
            self.labels[position].pack(side=LEFT)
        for position in positions:
            self.tables[position].pack(side=LEFT)
            self.tables[position].bind("<Delete>",self.deleteSelection)
        self.refreshTables()

    # Sets up the tables currently visible in the GUI so we can take a look at the matches and your rating!
    def ratingsView(self):
        self.tables['matchId'  ] = Listbox(self.table_frame, width=10, font='courier 9')
        self.tables['mapId'    ] = Listbox(self.table_frame, width= 6, font='courier 9')
        self.tables['queueType'] = Listbox(self.table_frame, width=15, font='courier 9')
        self.tables['season'   ] = Listbox(self.table_frame, width=10, font='courier 9')
        self.tables['kda'      ] = Listbox(self.table_frame, width= 8, font='courier 9')
        self.tables['rating'   ] = Listbox(self.table_frame, width= 6, font='courier 9')
        self.tables['subRating'] = Listbox(self.table_frame, width=25, font='courier 9')

        self.labels['matchId'  ] = Label(  self.label_frame, width=10, font='courier 9', text="Match ID"  )
        self.labels['mapId'    ] = Label(  self.label_frame, width= 6, font='courier 9', text="Map ID"    )
        self.labels['queueType'] = Label(  self.label_frame, width=15, font='courier 9', text="Queue"     )
        self.labels['season'   ] = Label(  self.label_frame, width=10, font='courier 9', text="Match ID"  )
        self.labels['kda'      ] = Label(  self.label_frame, width= 8, font='courier 9', text="KDA"       )
        self.labels['rating'   ] = Label(  self.label_frame, width= 6, font='courier 9', text="Rating"    )
        self.labels['subRating'] = Label(  self.label_frame, width=25, font='courier 9', text="Sub Rating")

        for key in ['matchId', 'mapId', 'queueType', 'season', 'kda', 'rating', 'subRating']:
            self.labels[key].pack(side=LEFT)
            self.tables[key].pack(side=LEFT)

    # This goes back to the old hand-done ranking system.  Still in because I may use very similar functionality to
    #   do the ranking and display.  I doubt that will happen, but I figure it can't hurt to leave in here until I know
    #   I won't be using it
    def addChampion(self):
        champ = self.champ_var.get()
        position  = self.position_var.get()
        if champ == "Champion..." or position == "Position...":
            return
        conn = sql.connect(self.db)
        c    = conn.cursor()
        # UPDATE champion_ranks SET rank=rank+<n> WHERE champion=<champ>
        # Initial rank = SELECT Count(*) FROM champion_ranks
        #                                   name,position,rank,summoner
        try:
            c.execute("INSERT INTO champion_ranks VALUES(?,?,(SELECT Count(*) FROM champion_ranks),?)",(champ,position.lower(),self.summoner.id))
        except sql.IntegrityError as err:
            if not err.args[0].startswith('UNIQUE constraint failed:'):
                raise
        conn.commit()
        conn.close()
        self.champ_var.set(self.all_champions[0])
        self.position_var.set(self.all_positions[0])
        self.refreshTables()

    def deleteSelection(self,event=None):
        conn = sql.connect(self.db)
        c    = conn.cursor()
        for position in positions:
            selected = self.tables[position]. curselection()
            for selection in selected:
#                print('Removing',self.disp_data[position][selection])
                c.execute("DELETE FROM champion_ranks WHERE champion=? AND position=?",(self.disp_data[position][selection],position))
        conn.commit()
        self.refreshTables()

    # Opens a dialog window with an entry and "Apply" button, used to enter the name of the summoner to change to.
    #   FIXME: Known bug where the apply button doesn't do anything... what. Haven't had time to look into it
    #           especially since the '<Return>' binding works just fine
    def promptForSummonerName(self):
        self.dlg = Toplevel(self.master)
        self.dlg.title("Enter Summoner Name")
        self.dlg.entry = Entry(self.dlg,width=35)
        self.dlg.entry.bind('<Return>', self.checkSummonerName)
        self.dlg.entry.pack(side=LEFT)
        self.dlg.ok = Button(self.dlg,text="Apply",width=10,command=self.checkSummonerName)
        self.dlg.ok.pack(side=LEFT)

        self.dlg.entry.focus_set()
        self.dlg.entry.focus_force()
        self.dlg.attributes('-topmost',True)
        self.master.wait_window(self.dlg)

    # Check that we have entered a valid summoner name.  This results in a request to the summoners API.
    #   I'm generally distrustful of any locally cached data here, and it's not passing a ton of data around
    #   If the summoner name isn't found, keep the window active.
    def checkSummonerName(self,event=None):
        if event:
            name = self.dlg.entry.get()
            summoner = self.getSummoner(name)
            if summoner:
                self.dlg.destroy()
                self.master.focus_force()
                self.master.lift()
                self.updateSummoner(summoner)
            else:
                self.dlg.entry.focus_force()
                return
        else:
            conn = sql.connect(self.db)
            c    = conn.cursor()
            summoner_name = list(c.execute('SELECT name FROM summoners WHERE id=(\
                                                SELECT summoner_id FROM users WHERE user=?)' ,\
                                             (os.getlogin(),)))
            if len(summoner_name) == 1:
                summoner = self.getSummoner(summoner_name[0][0])
                if summoner:
                    self.updateSummoner(summoner)
                else:
                    self.promptForSummonerName()

    # Once a valid summoner is found, make the current self.summoner pointer that and update our db
    #   to associate the current user and this summoner.
    def updateSummoner(self, summoner):
        self.summoner = summoner
        conn = sql.connect(self.db)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users VALUES (?,?)", (os.getlogin(), self.summoner['id']))
        except sql.IntegrityError:
            c.execute("UPDATE users SET summoner_id=? where user=?", (self.summoner['id'], os.getlogin()))
        data = list(c.execute('SELECT key FROM keys WHERE summoner_id=?', (self.summoner['id'],)))
        if len(data) == 1:
            self.api.key = data[0][0]
        self.master.wm_title("Positions - " + self.summoner['name'])
        conn.commit()
        conn.close()

    # Update the rating display tables when a new analysis is run(via the "Magic!" button.  I'll rename that later, promise.
    def updateRatingDisplay(self, analysis):
        columns = ['matchId', 'mapId', 'queueType', 'season', 'rating', 'subRating']
        [self.tables[table].delete(0, END) for table in columns]
        match_ids = list(analysis.keys())
        match_ids.sort()
        if len(match_ids) > 10:
            match_ids = match_ids[-10:]
        for match_id in match_ids:
            match = analysis[match_id]
            kills =   match['stats']['kills']
            deaths =  match['stats']['deaths']
            assists = match['stats']['assists']
            sub_rating_str = ' '.join([key + (':%.2f' % round(match['ratingData'][key], 2)) \
                                       for key in match['ratingData'] if key != 'rating'])
            self.tables['matchId'  ].insert(END, match['matchId'  ])
            self.tables['mapId'    ].insert(END, match['mapId'    ])
            self.tables['queueType'].insert(END, match['queueType'])
            self.tables['season'   ].insert(END, match['season'   ])
            self.tables['kda'      ].insert(END, '{K}/{D}/{A}'.format(K=kills, D=deaths, A=assists))
            self.tables['rating'   ].insert(END, '%.2f' % round(match['ratingData']['rating'], 2))
            self.tables['subRating'].insert(END, sub_rating_str)

    # Entry point for the "Magic!" button.  Doesn't do a lot by itself, mostly just hands data off to updateRatingDisplay
    def analyzeSummonerHistory(self, event=None):
        # Get data out of our database, and then DO STUFFFF!!!!!
        summoner_data = SummonerData(self.summoner, self.db)
        analysis = summoner_data.getAnalysisData()
#        for match_id in analysis:
#            match = analysis[match_id]
#            print(match_id, match['ratingData'])
        self.updateRatingDisplay(analysis)

    # Makes a summoner API request(foreground)
    def getSummoner(self,name):
        return self.api.getData(SUMMONER_IMM_REQ, name)

    # Makes a match history API request(background)
    def refreshHistory(self, event=None):
        self.status.config(text='Requesting Match History...')
        self.pending_match_history.append(self.api.getData(HISTORY_REQ, self.summoner, queues=['RANKED_SOLO_5x5'], begin=0))

    # Makes a targetted match history API request(background)
    def getHistory(self, begin):
        self.status.config(text='Requesting Match History from ' + str(begin) + '...')
        self.pending_match_history.append(self.api.getData(HISTORY_REQ, self.summoner, queues=['RANKED_SOLO_5x5'], begin=begin))

    # Makes a stats API request(background)
    def refreshStatSummary(self, event=None):
#        print('Requesting Stat Summary')
        self.pending_stats.append(self.api.getData(STATS_REQ, self.summoner))

    # Makes a service status API request(background)
    def refreshStatus(self, event=None):
#        print('Requesting LoL Status')
        self.pending_lol_status.append(self.api.getData(STATUS_REQ))

    # Makes a lol static data champions API request(background)
    def refreshChampions(self, event=None):
#        print('Requesting Champions')
        self.pending_lol_static_data.append(self.api.getData(CHAMPION_ALL_REQ))

    # Data return callback registered with the LeagueOfLegendsApi object for it to push new data back through
    def apiDataReturn(self, data):
        # LeagueOfLegendsApi pushes completed requests in here, we'll figure out where they belong on this end
        if data[0] in self.pending_champion:
            conn = sql.connect(self.db)
            c    = conn.cursor()
            champ_names = [item[0] for item in c.execute('SELECT name FROM champions')]
            conn.close()
            champ_names.sort()
            self.all_champions  = ["Champion..."]
            self.all_champions += [champ for champ in champ_names]

            # Reset var and delete all old options
            self.champs['menu'].delete(0, 'end')
            # Insert list of new options (tk._setit hooks them up to var)
            for champ in self.all_champions:
                self.champs['menu'].add_command(label=champ, command=tk._setit(self.champ_var, champ))
        elif data[0] in self.pending_current_game:
            pass #TODO DO STUFF
        elif data[0] in self.pending_featured_games:
            pass #TODO DO STUFF
        elif data[0] in self.pending_game:
            pass #TODO DO STUFF
        elif data[0] in self.pending_league:
            pass #TODO DO STUFF
        elif data[0] in self.pending_lol_static_data:
            pass
#            print('LoL Static Data in app!')
        elif data[0] in self.pending_lol_status:
            pass
#            print('Status data in app!')
        elif data[0] in self.pending_match:
            pass #TODO DO STUFF
        elif data[0] in self.pending_match_history:
            conn = sql.connect(self.db)
            c    = conn.cursor()
            numMatches = len(list(c.execute('SELECT matchId FROM participant_identities \
                                             WHERE summonerId=?', (self.summoner['id'],) )))
            conn.close()
            if len(data[1]) != 0 and numMatches < 40:
                # Keep going!
                self.getHistory(numMatches)
            else:
                self.status.config(text='All finished! ' +str(numMatches) + ' retrieved')
        elif data[0] in self.pending_stats:
            pass
#            print('Stats in data app!')
        elif data[0] in self.pending_team:
            pass #TODO DO STUFF

    def cleanup(self):
        self.api.cleanup()


#############################################################################################
# Local Data Classes                                                                        #
#############################################################################################
MAX_CS_AT_TEN = 107

class Summoner(dict):
    def __init__(self, summoner_id, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        cols = ['summonerLevel' ,\
                'revisionDate'  ,\
                'name'          ,\
                'profileIconId' ,\
                'id'            ,\
                'nameKey'        ]
        sel_str = 'SELECT ' + ', '.join(cols) + ' FROM summoners WHERE id=?'
        data = list(c.execute(sel_str, (summoner_id, )))[0]
        conn.close()
        self.update({pair[0]:pair[1] for pair in zip(cols, data)})


class SummonerData(dict):
    def __init__(self, summoner, db):
        self.update(summoner)
        self['matches'] = {}

        conn = sql.connect(db)
        c    = conn.cursor()
        match_ids = [item[0] for item in list(c.execute('SELECT matchId FROM participant_identities WHERE summonerId=?', (self['id'],) ))]
        conn.close()

        for match_id in match_ids:
            self['matches'][match_id] = Match(match_id, db)

    def getAnalysisData(self):
        data = {}
        for match_id in self['matches']:
            match = self['matches'][match_id]
            data[match['matchId']] = {}
            keys = ['mapId'         ,\
                    'matchCreation' ,\
                    'matchDuration' ,\
                    'matchId'       ,\
                    'matchMode'     ,\
                    'matchType'     ,\
                    'matchVersion'  ,\
                    'platformId'    ,\
                    'queueType'     ,\
                    'region'        ,\
                    'season'         ]
            data[match['matchId']].update({key:match[key] for key in keys})
            current_participant = None
            for participant in match['participants']:
                if participant['summonerId'] == self['id']:
                    current_participant = participant
            data[match['matchId']].update(current_participant)
            data[match['matchId']]['ratingData'] = current_participant.getRating()
        return data

    def getStrLines(self):
        out_lines  = [self['name'] + ' ' + str(self['id']) + ' Matches:']
        matches    = [self['matches'][match_id] for match_id in self['matches']]
        matches.sort(key=lambda m: m['matchCreation'])
        for match in matches:
            [out_lines.append('  ' + line) for line in match.getStrLines()]
        return out_lines

    def __str__(self):
        return os.linesep.join(self.getStrLines())

    def __repr__(self):
        return str(self)


class Match(dict):
    def __init__(self, match_id, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        cols = ['mapId'         ,\
                'matchCreation' ,\
                'matchDuration' ,\
                'matchId'       ,\
                'matchMode'     ,\
                'matchType'     ,\
                'matchVersion'  ,\
                'platformId'    ,\
                'queueType'     ,\
                'region'        ,\
                'season'         ]
        sel_str = 'SELECT ' + ', '.join(cols) + ' FROM match_summaries WHERE matchId=?'
        data = list(c.execute(sel_str, (match_id, )))[0]
        self.update({pair[0]:pair[1] for pair in zip(cols, data)})

        summ_sel_str = 'SELECT summonerId FROM participant_identities WHERE matchId=?'
        summoner_ids = [item[0] for item in list(c.execute(summ_sel_str, (match_id,) ))]
        conn.close()
        self['participants'] = []
        for summoner_id in summoner_ids:
            self['participants'].append(Participant(match_id, summoner_id, self['matchDuration'], db))

    def getStrLines(self):
        out_lines  = ['Queue: ' + self['queueType'] + ' ID: ' + str(self['matchId'])]
        for participant in self['participants']:
            [out_lines.append('  ' + line) for line in participant.getStrLines()]
        return out_lines

    def __str__(self):
        return os.linesep.join(self.getStrLines())


class Participant(dict):
    def __init__(self, match_id, summoner_id, match_duration, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        cols = ['summonerId' ,\
                'championId' ,\
                'spell1Id'   ,\
                'spell2Id'   ,\
                'matchId'    ,\
                'teamId'      ]
        sel_str = 'SELECT ' + ', '.join(cols) + ' FROM participants WHERE matchId=? AND summonerId=?'
        data = list(c.execute(sel_str, (match_id, summoner_id)))[0]
        conn.close()
        self.update({pair[0]:pair[1] for pair in zip(cols, data)})
        # Splice in the summoner data so we have the name etc
        self.update(Summoner(summoner_id, db))
        self['matchDuration'] = match_duration
        # Go grab the stats!
        self['stats']    = ParticipantStats(match_id, summoner_id, db)
        self['timeline'] = ParticipantTimeline(match_id, summoner_id, db)
        self['champion'] = Champion(self['championId'], db)

    def getRating(self):
        lane = self['timeline']['lane']
        role = self['timeline']['role']
        rating = {}

        if   lane == 'TOP':
            rating['cs']     = self.calculateCarryCsRating()
            rating['kda']    = self.calculateCarryKdaRating()
            rating['rating'] = ((rating['cs'] * 1) + (rating['kda'] + 1)) / 2
            return rating
        elif lane == 'JUNGLE':
            rating['cs']     = self.calculateCarryJungleCsRating()
            rating['kda']    = self.calculateCarryKdaRating()
            rating['rating'] = ((rating['cs'] * 1) + (rating['kda'] + 1)) / 2
            return rating
        elif lane == 'MIDDLE':
            rating['cs']     = self.calculateCarryCsRating()
            rating['kda']    = self.calculateCarryKdaRating()
            rating['rating'] = ((rating['cs'] * 1) + (rating['kda'] + 1)) / 2
            return rating
        elif lane == 'BOTTOM':
            if   role in ['DUO_CARRY', 'SOLO']:
                rating['cs']     = self.calculateCarryCsRating()
                rating['kda']    = self.calculateCarryKdaRating()
                rating['rating'] = ((rating['cs'] * 1) + (rating['kda'] + 1)) / 2
                return rating
            elif role == 'DUO_SUPPORT':
                rating['vision'] = self.calculateSupportVisionRating()
                rating['kda']    = self.calculateCarryKdaRating()
                rating['rating'] = ((rating['vision'] * 1) + (rating['kda'] + 1)) / 2
                return rating
        return 0
        raise RuntimeError('No Role Detected! ' + lane + ' ' + role)

    #################################################################################
    # Sub-category rating calculations: Champion roles determine the algorithm used #
    #################################################################################
    # Vision Control Rating calculations
    def calculateSupportVisionRating(self):
        duration_mins = self['matchDuration'] / 60
        wards_placed  = self['stats']['wardsPlaced']
        wards_killed  = self['stats']['wardsKilled']
        vision_rating = 10 * (wards_placed + wards_killed) / duration_mins
        return vision_rating

    # CS Rating calculations
    def calculateCarryCsRating(self):
        cs_0_10   = self['timeline']['creepsPerMinDeltas_0_10'  ]
        cs_10_20  = self['timeline']['creepsPerMinDeltas_10_20' ]
        cs_20_30  = self['timeline']['creepsPerMinDeltas_20_30' ]
        cs_30_end = self['timeline']['creepsPerMinDeltas_30_end']
        if cs_0_10 == None:
            cs_0_10 = 0
        if cs_10_20 == None:
            cs_10_20 = 0
        if cs_20_30 == None:
            cs_20_30 = 0
        if cs_30_end == None:
            cs_30_end = 0
        cs_rating = ((cs_0_10 * 5) + (cs_10_20 * 4) + (cs_20_30 * 2) + (cs_30_end * 2)) / 13
        return cs_rating

    def calculateCarryJungleCsRating(self):
        duration_mins = self['matchDuration'] / 60
        cs_rating     = self.calculateCarryCsRating()
        cs_rating    += self['stats']['neutralMinionsKilled'] / duration_mins
        return cs_rating

    # KDA Rating calculations
    def calculateCarryKdaRating(self):
        # This calculation took about 2 hours to settle on... For carry roles I wanted
        #   to have a calculation that weighted kills above assists and really factored
        #   in the ability to snowball and press an advantage.  To do this, I raise the
        #   kills to a power > 1(originally was squaring... the ratings got out of hand
        #   FAST).  I settled on 4/3 for that power because of the way it scaled next to
        #   the linear addition of assists.  In this scheme 10/1/0 is roughly equivalent
        #   to 8/1/5, 6/1/11, 4/1/15 etc.  Specifically for a carry, this weight made sense
        #   Deaths reduce it the same as with normal KDA, but I count "lives" instead so
        #   the rating fairly represents a perfect game, with a crazy high rating.
        kills =   self['stats']['kills']
        deaths =  self['stats']['deaths']
        assists = self['stats']['assists']
        kda_rating = (pow(kills, 4/3) + assists)/(deaths + 1)
        return kda_rating

    def calculateSupportKdaRating(self):
        kills =   self['stats']['kills']
        deaths =  self['stats']['deaths']
        assists = self['stats']['assists']
        kda_rating = (pow(assists, 4/3) + kills)/(deaths + 1)
        return kda_rating

    def getStrLines(self):
        out_lines = []
        line  = self['name'].ljust(16) + ' ' + str(self['summonerId']).rjust(8)

        champ_str = self['champion']['name']
        lane  = self['timeline']['lane']
        role  = self['timeline']['role']
        if lane in ['TOP', 'MIDDLE', 'JUNGLE']:
            champ_str += ' ' + lane
        elif role in ['DUO_CARRY', 'SOLO']:
            champ_str += ' CARRY'
        elif role == 'DUO_SUPPORT':
            champ_str += ' SUPPORT'
        else:
            champ_str += ' ' + lane + ' ' + role
        line += ' ' + champ_str.ljust(18)

        if self['stats']['winner']:
            line += ' WIN '
        else:
            line += ' LOSS'
        rating = self.getRating()
        line += ' Rating: %.2f' % round(rating['rating'], 2)

        kills =   self['stats']['kills']
        deaths =  self['stats']['deaths']
        assists = self['stats']['assists']
        line += ' K/D/A: ' + (str(kills) + '/' + str(deaths) + '/' + str(assists)).rjust(8)

        line += ' CS: ' + (str(self['stats']['minionsKilled']) + '/' + str(self['stats']['neutralMinionsKilled'])).rjust(3)

        out_lines.append(line)
        return out_lines


class ParticipantStats(dict):
    def __init__(self, match_id, summoner_id, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        cols = ['assists'                         ,\
                'champLevel'                      ,\
                'combatPlayerScore'               ,\
                'deaths'                          ,\
                'doubleKills'                     ,\
                'firstBloodAssist'                ,\
                'firstBloodKill'                  ,\
                'firstInhibitorAssist'            ,\
                'firstInhibitorKill'              ,\
                'firstTowerAssist'                ,\
                'firstTowerKill'                  ,\
                'goldEarned'                      ,\
                'goldSpent'                       ,\
                'inhibitorKills'                  ,\
                'item0', 'item1', 'item2', 'item3',\
                'item4', 'item5', 'item6'         ,\
                'killingSprees'                   ,\
                'kills'                           ,\
                'largestCriticalStrike'           ,\
                'largestKillingSpree'             ,\
                'largestMultiKill'                ,\
                'magicDamageDealt'                ,\
                'magicDamageDealtToChampions'     ,\
                'magicDamageTaken'                ,\
                'minionsKilled'                   ,\
                'neutralMinionsKilled'            ,\
                'neutralMinionsKilledEnemyJungle' ,\
                'neutralMinionsKilledTeamJungle'  ,\
                'nodeCapture'                     ,\
                'nodeCaptureAssist'               ,\
                'nodeNeutralize'                  ,\
                'nodeNeutralizeAssist'            ,\
                'objectivePlayerScore'            ,\
                'pentaKills'                      ,\
                'physicalDamageDealt'             ,\
                'physicalDamageDealtToChampions'  ,\
                'physicalDamageTaken'             ,\
                'quadraKills'                     ,\
                'sightWardsBoughtInGame'          ,\
                'teamObjective'                   ,\
                'totalDamageDealt'                ,\
                'totalDamageDealtToChampions'     ,\
                'totalDamageTaken'                ,\
                'totalHeal'                       ,\
                'totalPlayerScore'                ,\
                'totalScoreRank'                  ,\
                'totalTimeCrowdControlDealt'      ,\
                'totalUnitsHealed'                ,\
                'towerKills'                      ,\
                'tripleKills'                     ,\
                'trueDamageDealt'                 ,\
                'trueDamageDealtToChampions'      ,\
                'trueDamageTaken'                 ,\
                'unrealKills'                     ,\
                'visionWardsBoughtInGame'         ,\
                'wardsKilled'                     ,\
                'wardsPlaced'                     ,\
                'winner'                           ]
        sel_str = 'SELECT ' + ', '.join(cols) + ' FROM participant_stats WHERE matchId=? AND summonerId=?'
        data = list(c.execute(sel_str, (match_id, summoner_id)))[0]
        conn.close()
        self.update({pair[0]:pair[1] for pair in zip(cols, data)})


class ParticipantTimeline(dict):
    def __init__(self, match_id, summoner_id, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        cols = [info[1] for info in c.execute('PRAGMA table_info(participant_timelines)').fetchall()]
        sel_str = 'SELECT * FROM participant_timelines WHERE matchId=? AND summonerId=?'
        data = list(c.execute(sel_str, (match_id, summoner_id)))[0]
        conn.close()
        self.update({pair[0]:pair[1] for pair in zip(cols, data) if pair[0] not in ['matchId', 'summonerId']})


class Champion(dict):
    def __init__(self, champion_id, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        cols = ['allytips'  ,\
                'blurb'     ,\
                'enemytips' ,\
                'id'        ,\
                'image'     ,\
                'key'       ,\
                'lore'      ,\
                'name'      ,\
                'partype'   ,\
                'tags'      ,\
                'title'      ]
        sel_str = 'SELECT ' + ', '.join(cols) + ' FROM champions WHERE id=?'
        data = list(c.execute(sel_str, (champion_id, )))[0]
        conn.close()
        self.update({pair[0]:pair[1] for pair in zip(cols, data) if pair[0]})


# Entry point.  Pretty self-explanitory... make a Tk window, bind the Positions thing to it and let 'er rip!
if __name__ == '__main__':
    root = Tk()
    p    = Positions(root)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    try:
        root.mainloop()
        p.cleanup()
        print()
    except KeyboardInterrupt:
        p.cleanup()
        print()
        raise
