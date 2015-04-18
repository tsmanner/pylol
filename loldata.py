'''
This file contains data container classes for League Of Legends API requests.  All data is unpacked into a
    list or dict-like class.  These classes contain two static methods if they correspond to db tables used
    by the API: getSqlTableFormatStr() and getKeys().  All of the db classes also contain a write method
    which writes the data out.
'''
import sqlite3 as sql
import os, sys, time
#----------------------------------------------------------------------------------------------------------#
# Champion Classes (ChampionApi):                                                                          #
#   ChampionListDto                                                                                        #
#   ChampionDto                                                                                            #
#----------------------------------------------------------------------------------------------------------#
class ChampionListDto(list):
    def __init__(self, data):
        if type(matches) == type([]):
            self += [ChampionDto(champ) for champ in data]
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        for champ in self:
            pass
#            print('  Writing champion dto:', champ['matchId'])


class ChampionDto(dict):
    def __init__(self, data):
        if type(matches) == type({}):
            self.update(data)
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        for key in self:
            pass


#----------------------------------------------------------------------------------------------------------#
# Champion Static Data Classes (LoLStaticDataApi):                                                         #
#   ChampionDataList                                                                                       #
#   ChampionData                                                                                           #
#   ImageData                                                                                              #
#   ChampionInfoData                                                                                       #
#   ChampionPassiveData                                                                                    #
#   ChampionRecommendedData                                                                                #
#   ChampionItemData                                                                                       #
#   ChampionSkinData                                                                                       #
#   ChampionSpellData                                                                                      #
#   LevelTipData                                                                                           #
#   SpellVarsData                                                                                          #
#   ChampionStatsData                                                                                      #
#----------------------------------------------------------------------------------------------------------#
class ChampionDataList(dict):
    def __init__(self, data):
        if type(data) == type({}):
            self.update({champ:ChampionData(data['data'][champ]) for champ in data['data']})
            self.type    = data['type']
            self.version = data['version']
            if 'format' in data:
                self.format  = data['format']
            if 'keys' in data:
                self.keys    = data['keys']
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        for champ in self:
            self[champ].write(db)


class ChampionData(dict):
    def __init__(self, data):
        # data is a dict or tuple containing the following information:
        #  +-------------+-------------+--------------------+
        #  | Field       | Dict Key    | Type               |
        #  +-------------+-------------+--------------------+
        #  | Ally Tips   | allytips    | [str]              |
        #  | Blurb       | blurb       | str                |
        #  | Enemy Tips  | enemytips   | [str]              |
        #  | ID          | id          | int                |
        #  | Image       | image       | ImageDto           |
        #  | Info        | info        | InfoDto            |
        #  | Key         | key         | str                |
        #  | Lore        | lore        | str                |
        #  | Name        | name        | str                |
        #  | Resource    | partype     | str                |
        #  | Passive     | passive     | PassiveDto         |
        #  | Recommended | recommended | [RecommendedDto]   |
        #  | Skins       | skins       | [SkinDto]          |
        #  | Spells      | spells      | [ChampionSpellDto] |
        #  | Stats       | stats       | StatsDto           |
        #  | Tags        | tags        | [str]              |
        #  | Title       | title       | str                |
        #  +-------------+-------------+--------------------+
        data_keys = ['allytips'    ,\
                     'blurb'       ,\
                     'enemytips'   ,\
                     'id'          ,\
                     'image'       ,\
                     'info'        ,\
                     'key'         ,\
                     'lore'        ,\
                     'name'        ,\
                     'partype'     ,\
                     'passive'     ,\
                     'recommended' ,\
                     'skins'       ,\
                     'spells'      ,\
                     'stats'       ,\
                     'tags'        ,\
                     'title'        ]
        self.update({key:None for key in data_keys})
        if type(data) == type({}):
            self['id']          = data['id']
            self['key']         = data['key']
            self['name']        = data['name']
            self['title']       = data['title']
            if 'allytips' in data:
                self['allytips']    = '|'.join(data['allytips'])
            if 'blurb' in data:
                self['blurb']       = data['blurb']
            if 'enemytips' in data:
                self['enemytips']   = '|'.join(data['enemytips'])
            if 'image' in data:
                self['image']       = ImageData(data['image'])
            if 'info' in data:
                self['info']        = ChampionInfoData(data['info'], data['id'])
            if 'lore' in data:
                self['lore']        = data['lore']
            if 'partype' in data:
                self['partype']     = data['partype']
            if 'passive' in data:
                self['passive']     =  ChampionPassiveData(data['passive'], data['id'])
            if 'recommended' in data:
                self['recommended'] = [ChampionRecommendedData(item, data['id']) for item in data['recommended']]
            if 'skins' in data:
                self['skins']       = [ChampionSkinData(       item, data['id']) for item in data['skins']]
            if 'spells' in data:
                self['spells']      = [ChampionSpellData(      item, data['id']) for item in data['spells']]
            if 'stats' in data:
                self['stats']       =  ChampionStatsData(data['stats'], data['id'])
            if 'tags' in data:
                self['tags']        = '|'.join(data['tags'])
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        # The image field must be the full name of the image, not the image instance
        db_data = [self[key] for key in self.getKeys()]
        if db_data[4]:
            db_data[4] = db_data[4]['full']
        return tuple(db_data)

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champions VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champions SET \
                        allytips=?  ,\
                        blurb=?     ,\
                        enemytips=? ,\
                        id=?        ,\
                        image=?     ,\
                        key=?       ,\
                        lore=?      ,\
                        name=?      ,\
                        partype=?   ,\
                        tags=?      ,\
                        title=?      \
                        WHERE id=?' ,\
                        self.getDbData() + (self['id'],))
        conn.commit()
        conn.close()
        if self['info']:
            self['info'].write(db)
        if self['passive']:
            self['passive'].write(db)
        if self['stats']:
            self['stats'].write(db)
        if self['recommended']:
            [recommendation.write(db) for recommendation in self['recommended']]
        if self['skins']:
            [skin.write(db) for skin in self['skins']]
        if self['spells']:
            [spell.write(db) for spell in self['spells']]

    def __str__(self):
        out_str = str(self['id']).rjust(3) + ' ' + self['name'].ljust(12) + ' - ' + self['title']
        return out_str

    def __repr__(self):
        return str(self)

    @staticmethod
    def getKeys():
        return ['allytips'  ,\
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

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champions('
        columns = []
        for key in keys:
            if   key in ['id']:
                columns.append(key + ' integer NOT NULL')
            elif key in ['key', 'name', 'title']:
                columns.append(key + ' text NOT NULL')
            else:
                columns.append(key + ' text')
        table_str += ', '.join(columns) + ', UNIQUE(id), UNIQUE(name) )'
        return table_str


class ImageData(dict):
    def __init__(self, data):
        # data is a dict or tuple containing the following information:
        #  +--------+----------+------+
        #  | Field  | Dict Key | Type |
        #  +--------+----------+------+
        #  | Full   | full     | str  |
        #  | Group  | group    | str  |
        #  | H      | h        | int  |
        #  | Sprite | sprite   | str  |
        #  | W      | w        | int  |
        #  | X      | x        | int  |
        #  | Y      | y        | int  |
        #  +--------+----------+------+
        if type(data) == type({}):
            self.update(data)
            self['img_group'] = data['group']
            self.remove('group')
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    @staticmethod
    def getKeys():
        return ['full'      ,\
                'img_group' ,\
                'h'         ,\
                'sprite'    ,\
                'w'         ,\
                'x'         ,\
                'y'          ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ImageData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS images('
        columns = []
        for key in keys:
            if   key in ['full', 'img_group', 'sprite']:
                columns.append(key + ' text NOT NULL')
            else:
                columns.append(key + ' integer NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(full) )'
        return table_str


class ChampionInfoData(dict):
    def __init__(self, data, champion_id):
        # data is a dict or tuple containing the following information:
        #  +---------------+------------+------+
        #  | Field         | Dict Key   | Type |
        #  +---------------+------------+------+
        #  | Attack Power  | attack     | int  |
        #  | Defense Power | defense    | int  |
        #  | Difficulty    | difficulty | int  |
        #  | Magic Power   | magic      | int  |
        #  +---------------+------------+------+
        if type(data) == type({}):
            self.update(data)
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_info VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_info SET \
                        attack=?     ,\
                        defense=?    ,\
                        difficulty=? ,\
                        magic=?      ,\
                        championId=?  \
                        WHERE championId=?' ,\
                        self.getDbData() + (self['championId'],))
        conn.commit()
        conn.close()

    @staticmethod
    def getKeys():
        return ['attack'     ,\
                'defense'    ,\
                'difficulty' ,\
                'magic'      ,\
                'championId' ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionInfoData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_info('
        columns = []
        for key in keys:
            columns.append(key + ' integer NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(championId) )'
        return table_str


class ChampionPassiveData(dict):
    def __init__(self, data, champion_id):
        # data is a dict or tuple containing the following information:
        #  +-----------------------+----------------------+-----------+
        #  | Field                 | Dict Key             | Type      |
        #  +-----------------------+----------------------+-----------+
        #  | Description           | description          | str       |
        #  | Image                 | image                | ImageData |
        #  | Name                  | name                 | str       |
        #  | Sanitized Description | sanitizedDescription | str       |
        #  +-----------------------+----------------------+-----------+
        if type(data) == type({}):
            self.update(data)
            self['image'] = ImageData(data['image'])
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        # The image field must be the full name of the image, not the image instance
        db_data = [self[key] for key in self.getKeys()]
        db_data[1] = db_data[1]['full']
        return tuple(db_data)

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_passives VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_passives SET \
                        description=?          ,\
                        image=?                ,\
                        name=?                 ,\
                        sanitizedDescription=? ,\
                        championId=?            \
                        WHERE championId=?' ,\
                        self.getDbData() + (self['championId'],))
        conn.commit()
        conn.close()
        self['image'].write(db)

    @staticmethod
    def getKeys():
        return ['description'          ,\
                'image'                ,\
                'name'                 ,\
                'sanitizedDescription' ,\
                'championId'            ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionPassiveData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_passives('
        columns = []
        for key in keys:
            if   key == 'championId':
                columns.append(key + ' integer NOT NULL')
            else:
                columns.append(key + ' text NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(championId) )'
        return table_str


class ChampionRecommendedData(dict):
    def __init__(self, data, champion_id):
        # data is a dict or tuple containing the following information:
        #  +-------------+----------+-------------+
        #  | Field       | Dict Key | Type        |
        #  +-------------+----------+-------------+
        #  | Item Blocks | blocks   | [BlockData] |
        #  | Champion    | champion | str         |
        #  | Map         | map      | str         |
        #  | Mode        | mode     | str         |
        #  | Priority    | priority | boolean     |
        #  | Title       | title    | str         |
        #  | Type        | type     | str         |
        #  +-------------+----------+-------------+
        if type(data) == type({}):
            self.update(data)
            self['blocks'] = [ChampionItemData(item, champion_id, self['map'], self['title']) for item in self['blocks']]
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_recommendations VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_recommendations SET \
                        champion=?   ,\
                        map=?        ,\
                        mode=?       ,\
                        priority=?   ,\
                        title=?      ,\
                        type=?       ,\
                        championId=?  \
                        WHERE championId=? AND map=? AND title=?' ,\
                        self.getDbData() + (self['championId'], self['map'], self['name']))
        conn.commit()
        conn.close()
        [block.write(db) for block in self['blocks']]

    @staticmethod
    def getKeys():
        return ['champion'   ,\
                'map'        ,\
                'mode'       ,\
                'priority'   ,\
                'title'      ,\
                'type'       ,\
                'championId'  ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionRecommendedData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_recommendations('
        columns = []
        for key in keys:
            if   key == 'championId':
                columns.append(key + ' integer NOT NULL')
            elif key == 'priority':
                columns.append(key + ' bool NOT NULL')
            else:
                columns.append(key + ' text NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(map, title, championId) )'
        return table_str


class ChampionItemData(dict):
    def __init__(self, data, champion_id, map_name, title):
        # data is a dict or tuple containing the following information:
        #  +-------------+----------+----------------+
        #  | Field       | Dict Key | Type           |
        #  +-------------+----------+----------------+
        #  | Items       | items    | [BlockItemDto] |
        #  | ???????     | recMath  | bool           |
        #  | Type        | type     | str            |
        #  +-------------+----------+----------------+
        if type(data) == type({}):
            self.update(data)
            self['map'] = map_name
            self['title'] = title
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        db_data = []
        for block in self['items']:
            db_data += [block['count']     ,\
                        block['id']        ,\
                        self['recMath']    ,\
                        self['type']       ,\
                        self['map']        ,\
                        self['title']      ,\
                        self['championId']  ]
        return db_data

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        for db_data_single in data:
            try:
                insert_str = 'INSERT INTO champion_recommended_items VALUES (' \
                           + ', '.join(['?'] * len(db_data_single)) + ')'
                c.execute(insert_str, db_data_single)
            except sql.IntegrityError:
                c.execute('UPDATE champion_recommended_items SET \
                            count=?      ,\
                            id=?         ,\
                            recMath=?    ,\
                            type=?       ,\
                            map=?        ,\
                            title=?      ,\
                            championId=?  \
                            WHERE championId=? AND map=? AND title=?' ,\
                            db_data_single + (self['championId'], self['map'], self['title']))
        conn.commit()
        conn.close()

    @staticmethod
    def getKeys():
        return ['count'      ,\
                'id'         ,\
                'recMath'    ,\
                'type'       ,\
                'map'        ,\
                'title'      ,\
                'championId'  ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionItemData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_recommended_items('
        columns = []
        for key in keys:
            if   key in ['type', 'map', 'title']:
                columns.append(key + ' text NOT NULL')
            elif key == 'recMath':
                columns.append(key + ' bool NOT NULL')
            else:
                columns.append(key + ' integer NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(id, map, championId) )'
        return table_str


class ChampionSkinData(dict):
    def __init__(self, data, champion_id):
        # data is a dict or tuple containing the following information:
        #  +-------------+----------+------+
        #  | Field       | Dict Key | Type |
        #  +-------------+----------+------+
        #  | Skin ID     | id       | int  |
        #  | Skin Name   | name     | str  |
        #  | Skin Number | num      | int  |
        #  +-------------+----------+------+
        if type(data) == type({}):
            self.update(data)
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_skins VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_skins SET \
                        id=?         ,\
                        name=?       ,\
                        num=?        ,\
                        championId=?  \
                        WHERE championId=? AND name=?' ,\
                        self.getDbData() + (self['championId'], self['name']))
        conn.commit()
        conn.close()

    @staticmethod
    def getKeys():
        return ['id'         ,\
                'name'       ,\
                'num'        ,\
                'championId'  ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionSkinData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_skins('
        columns = []
        for key in keys:
            if   key in ['name']:
                columns.append(key + ' text NOT NULL')
            else:
                columns.append(key + ' integer NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(id, championId) )'
        return table_str


class ChampionSpellData(dict):
    def __init__(self, data, champion_id):
        # data is a dict or tuple containing the following information:
        #  +-----------------------+----------------------+-----------------+
        #  | Field                 | Dict Key             | Type            |
        #  +-----------------------+----------------------+-----------------+
        #  | Alternate Images      | altimages            | [ImageData]     |
        #  | Cooldown              | cooldown             | [float]         |
        #  | Cooldown Burn         | cooldownBurn         | str             |
        #  | Cost                  | cost                 | [int]           |
        #  | Cost Burn             | costBurn             | str             |
        #  | Cost Type             | costType             | str             |
        #  | Description           | description          | str             |
        #  | Effect                | effect               | [[float]]       |
        #  | Effect Burn           | effectBurn           | [str]           |
        #  | Image                 | image                | ImageData       |
        #  | Key                   | key                  | str             |
        #  | Level Tip             | levelTip             | LevelTipData    |
        #  | Max Rank              | maxRank              | int             |
        #  | Name                  | name                 | str             |
        #  | Range                 | range                | [int] OR str    |
        #  | Range Burn            | rangeBurn            | str             |
        #  | Resource              | resource             | str             |
        #  | Sanitized Description | sanitizedDescription | str             |
        #  | Sanitized Tooltip     | sanitizedTooltip     | str             |
        #  | Tooltip               | tooltip              | str             |
        #  | Variables             | vars                 | [SpellVarsData] |
        #  +-----------------------+----------------------+-----------------+
        if type(data) == type({}):
            self.update(data)
            self['altImages']  = [ImageData(item) for item in data['altImages']]
            self['image']      =  ImageData(data['image'])
            self['levelTip']   =  LevelTipData(data['levelTip'], champion_id, data['name'])
            self['vars']       = [SpellVarsData(item, champion_id, data['name']) for item in data['vars']]
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        db_data = [self[key] for key in self.getKeys()]
        # Several of these fields are lists of simple types. It seems like a waste of code/time/memory/disk
        #   to make new tables for these lists and have foreign keys etc etc... soooo str concatenate them!
        db_data[0]  = '|'.join(self['altimages'])
        db_data[1]  = '|'.join([str(item) for item in self['cooldown']])
        db_data[3]  = '|'.join([str(item) for item in self['cost']])
        # This one is ugly... list of lists of floats... nested comprehension FTW?
        db_data[7]  = ':'.join(['|'.join([str(item) for item in eff_list]) for eff_list in self['effect']])
#        print(db_data[7])
        db_data[8]  = '|'.join(self['effectBurn'])
        # This one may be a list of ints, or a single str == 'self'. If it's ints, convert it
        if type(self['range']) != str:
            db_data[13] = '|'.join([str(item) for item in self['range']])
        return tuple(db_data)

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_spells VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_spells SET \
                        altImages=?              ,\
                        cooldown=?               ,\
                        cooldownBurn=?           ,\
                        cost=?                   ,\
                        costBurn=?               ,\
                        costType=?               ,\
                        description=?            ,\
                        effect=?                 ,\
                        effectBurn=?             ,\
                        image=?                  ,\
                        key=?                    ,\
                        maxRank=?                ,\
                        name=?                   ,\
                        range=?                  ,\
                        rangeBurn=?              ,\
                        resource=?               ,\
                        sanitizedDescription=?   ,\
                        sanitizedTooltip=?       ,\
                        tooltip=?                ,\
                        championId=?              \
                        WHERE championId=? AND name=?' ,\
                        self.getDbData() + (self['championId'], self['name']))
        conn.commit()
        conn.close()
        self['levelTip'].write(db)
        [spell_vars.write(db) for spell_vars in self['vars']]

    @staticmethod
    def getKeys():
        return ['altImages'            ,\
                'cooldown'             ,\
                'cooldownBurn'         ,\
                'cost'                 ,\
                'costBurn'             ,\
                'costType'             ,\
                'description'          ,\
                'effect'               ,\
                'effectBurn'           ,\
                'image'                ,\
                'key'                  ,\
                'maxRank'              ,\
                'name'                 ,\
                'range'                ,\
                'rangeBurn'            ,\
                'resource'             ,\
                'sanitizedDescription' ,\
                'sanitizedTooltip'     ,\
                'tooltip'              ,\
                'championId'            ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionSpellData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_spells('
        columns = []
        for key in keys:
            if   key in ['maxRank', 'championId']:
                columns.append(key + ' integer NOT NULL')
            else:
                columns.append(key + ' text NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(name, championId) )'
        return table_str


class LevelTipData(dict):
    def __init__(self, data, champion_id, spell_name):
        # data is a dict or tuple containing the following information:
        #  +--------+----------+-------+
        #  | Field  | Dict Key | Type  |
        #  +--------+----------+-------+
        #  | Effect | effect   | [str] |
        #  | Label  | label    | [str] |
        #  +--------+----------+-------+
        if type(data) == type({}):
            self.update(data)
            self['name'] = spell_name
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        db_data = [self[key] for key in self]
        db_data[0] = '|'.join(self['effect'])
        db_data[1] = '|'.join(self['label'])
        return tuple(db_data)

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_spell_level_tips VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_spell_level_tips SET \
                        effect=?     ,\
                        label=?      ,\
                        name=?       ,\
                        championId=?  \
                        WHERE championId=? AND name=?' ,\
                        self.getDbData() + (self['championId'], self['name']))
        conn.commit()
        conn.close()

    @staticmethod
    def getKeys():
        return ['effect'     ,\
                'label'      ,\
                'name'       ,\
                'championId'  ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = LevelTipData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_spell_level_tips('
        columns = []
        for key in keys:
            if   key in ['championId']:
                columns.append(key + ' integer NOT NULL')
            else:
                columns.append(key + ' text NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(name, championId) )'
        return table_str


class SpellVarsData(dict):
    def __init__(self, data, champion_id, spell_name):
        # data is a dict or tuple containing the following information:
        #  +--------------+-----------+---------+
        #  | Field        | Dict Key  | Type    |
        #  +--------------+-----------+---------+
        #  | Coefficients | coeff     | [float] |
        #  | Dyn          | dyn       | str     |
        #  | Key          | key       | str     |
        #  | Link         | link      | str     |
        #  | Ranks With   | ranksWith | str     |
        #  +--------------+-----------+---------+
        if type(data) == type({}):
            self.update(data)
            self['name'] = spell_name
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        db_data = [self[key] for key in self]
        db_data[0] = '|'.join([str(item) for item in self['coeff']])
        return tuple(db_data)

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_spell_vars VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_spell_vars SET \
                        coeff=?      ,\
                        dyn=?        ,\
                        key=?        ,\
                        link=?       ,\
                        ranksWith=?  ,\
                        name=?       ,\
                        championId=?  \
                        WHERE championId=? AND name=?' ,\
                        self.getDbData() + (self['championId'], self['name']))
        conn.commit()
        conn.close()

    @staticmethod
    def getKeys():
        return ['coeff'      ,\
                'dyn'        ,\
                'key'        ,\
                'link'       ,\
                'ranksWith'  ,\
                'name'       ,\
                'championId'  ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = SpellVarsData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_spell_vars('
        columns = []
        for key in keys:
            if   key in ['championId']:
                columns.append(key + ' integer NOT NULL')
            else:
                columns.append(key + ' text NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(name, championId) )'
        return table_str


class ChampionStatsData(dict):
    def __init__(self, data, champion_id):
        # data is a dict or tuple containing the following information:
        #  +-------------------------+----------------------+-------+
        #  | Field                   | Dict Key             | Type  |
        #  +-------------------------+----------------------+-------+
        #  | Armor                   | armor                | float |
        #  | Armor per Level         | armorperlevel        | float |
        #  | Attack Damage           | attackdamage         | float |
        #  | Attack Damage per Level | attackdamageperlevel | float |
        #  | Attack Range            | attackrange          | float |
        #  | Attack Speed Offset     | attackspeedoffset    | float |
        #  | Attack Speed per Level  | attackspeedperlevel  | float |
        #  | Crit Chance             | crit                 | float |
        #  | Crit Chance per Level   | critperlevel         | float |
        #  | Health                  | hp                   | float |
        #  | Health per Level        | hpperlevel           | float |
        #  | Health Regen            | hpregen              | float |
        #  | Health Regen per Level  | hpregenperlevel      | float |
        #  | Move Speed              | movespeed            | float |
        #  | Mana                    | mp                   | float |
        #  | Mana per Level          | mpperlevel           | float |
        #  | Mana Regen              | mpregen              | float |
        #  | Mana Regen per Level    | mpregenperlevel      | float |
        #  | Magic Resist            | spellblock           | float |
        #  | Magic Resist per Level  | spellblockperlevel   | float |
        #  +-------------------------+----------------------+-------+
        if type(data) == type({}):
            self.update(data)
            self['championId'] = champion_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    def write(self, db):
        data = self.getDbData()
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            insert_str = 'INSERT INTO champion_stats VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            c.execute('UPDATE champion_stats SET \
                        armor=?                ,\
                        armorperlevel=?        ,\
                        attackdamage=?         ,\
                        attackdamageperlevel=? ,\
                        attackrange=?          ,\
                        attackspeedoffset=?    ,\
                        attackspeedperlevel=?  ,\
                        crit=?                 ,\
                        critperlevel=?         ,\
                        hp=?                   ,\
                        hpperlevel=?           ,\
                        hpregen=?              ,\
                        hpregenperlevel=?      ,\
                        movespeed=?            ,\
                        mp=?                   ,\
                        mpperlevel=?           ,\
                        mpregen=?              ,\
                        mpregenperlevel=?      ,\
                        spellblock=?           ,\
                        spellblockperlevel=?   ,\
                        championId=?            \
                        WHERE championId=? AND name=?' ,\
                        self.getDbData() + (self['championId'], self['name']))
        conn.commit()
        conn.close()

    @staticmethod
    def getKeys():
        return ['armor'                ,\
                'armorperlevel'        ,\
                'attackdamage'         ,\
                'attackdamageperlevel' ,\
                'attackrange'          ,\
                'attackspeedoffset'    ,\
                'attackspeedperlevel'  ,\
                'crit'                 ,\
                'critperlevel'         ,\
                'hp'                   ,\
                'hpperlevel'           ,\
                'hpregen'              ,\
                'hpregenperlevel'      ,\
                'movespeed'            ,\
                'mp'                   ,\
                'mpperlevel'           ,\
                'mpregen'              ,\
                'mpregenperlevel'      ,\
                'spellblock'           ,\
                'spellblockperlevel'   ,\
                'championId'            ]

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        keys = ChampionStatsData.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS champion_stats('
        columns = []
        for key in keys:
            if key in ['championId']:
                columns.append(key + ' integer NOT NULL')
            else:
                columns.append(key + ' real NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(championId) )'
        return table_str


#----------------------------------------------------------------------------------------------------------#
# LoL Status Classes (LoLStatusApi):                                                                       #
#   LoLStatus                                                                                              #
#----------------------------------------------------------------------------------------------------------#
class LoLStatus(dict):
    def __init__(self, data):
        # data is a dict or tuple containing the following information:
        #  +-----------------+---------------+-----------+-------------+
        #  | Field           | Dict Key      | Tuple Key | Type        |
        #  +-----------------+---------------+-----------+-------------+
        #  | Region Name     | name          |     0     | str         |
        #  | Region Tag      | region_tag    |     1     | str         |
        #  | Hostname        | hostname      |     2     | str         |
        #  | Services        | services      |     3     | [status]    |
        #  | Slug            | slug          |     4     | str         |
        #  | Locales         | locales       |     5     | [str]       |
        #  +-----------------+---------------+-----------+-------------+
        if type(data) == type({}):
            for service in data['services']:
                service_name = service['name']
                self[service_name] = {}
                for key in data:
                    if key != 'services':
                        self[service_name][key] = data[key]
                for key in service:
                    if key != 'incidents':
                        self[service_name][key] = service[key]
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def __str__(self):
        out_strs  = ['Service:' + svc.ljust(7) + ' status:' + self[svc]['status'] for svc in self]
        return os.linesep.join(out_strs)

    def __repr__(self):
        return str(self)

    def getDbData(self, key):
        return (key                     ,\
                self[key]['region_tag'] ,\
                self[key]['hostname']   ,\
                self[key]['service']    ,\
                self[key]['slug']       ,\
                self[key]['locales']     )

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        return 'CREATE TABLE IF NOT EXISTS lol_status (\
                  name       text NOT NULL   ,\
                  region_tag text NOT NULL   ,\
                  hostname   text NOT NULL   ,\
                  service    text NOT NULL   ,\
                  slug       text NOT NULL   ,\
                  locales    text NOT NULL   ,\
                  UNIQUE(region_tag,service) )'


#----------------------------------------------------------------------------------------------------------#
# Summoner Classes (SummonerApi):                                                                          #
#   Summoner                                                                                               #
#----------------------------------------------------------------------------------------------------------#
class SummonerApiData(dict):
    def __init__(self, data):
        # data is a dict containing the following information:
        #  +-----------------+---------------+------+
        #  | Field           | Dict Key      | Type |
        #  +-----------------+---------------+------+
        #  | Summoner Level  | summonerLevel | int  |
        #  | Revision Date   | revisionDate  | str  |
        #  | Name            | name          | str  |
        #  | Profile Icon Id | profileIconId | int  |
        #  | ID              | id            | int  |
        #  +-----------------+---------------+------+
        keys = self.getKeys()
        self.update({key:None for key in keys})
        if type(data) == type({}):
            self.update(data)
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def getNameKey(self):
        return ''.join(self['name'].lower().split())

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()]) + (self.getNameKey(),)

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            c.execute('INSERT INTO summoners VALUES (?, ?, ?, ?, ?, ?)', self.getDbData())
        except sql.IntegrityError:
            c.execute('UPDATE summoners SET summonerLevel=?, revisionDate=?, name=?, profileIconId=?, id=?, nameKey=? \
                        WHERE nameKey=?' ,\
                        self.getDbData()+(self.getNameKey(),))
        conn.commit()
        conn.close()

    @staticmethod
    def getKeys():
        return ['summonerLevel', 'revisionDate', 'name', 'profileIconId', 'id']

    @staticmethod
    def getSqlTableFormatStr():
        # Table for summoner data
        return 'CREATE TABLE IF NOT EXISTS summoners (\
                  summonerLevel integer NOT NULL        ,\
                  revisionDate  text    NOT NULL        ,\
                  name          text    NOT NULL        ,\
                  profileIconId integer NOT NULL        ,\
                  id            integer NOT NULL        ,\
                  nameKey       text    NOT NULL        ,\
                  UNIQUE(nameKey)                       )'



#----------------------------------------------------------------------------------------------------------#
# Match History Classes (MatchHistoryApi):                                                                 #
#   PlayerHistory                                                                                          #
#   MatchSummary                                                                                           #
#   ParticipantIdentity                                                                                    #
#   Player                                                                                                 #
#   Participant                                                                                            #
#   Mastery                                                                                                #
#   Rune                                                                                                   #
#   ParticipantStats                                                                                       #
#   ParticipantTimeline                                                                                    #
#   ParticipantTimelineData                                                                                #
#----------------------------------------------------------------------------------------------------------#

# PlayerHistory doesn't have a table associated with it, it is a temporary container
#   for MatchSummary objects returned by the server.
class PlayerHistory(list):
    def __init__(self, matches, summoner_id):
        self.summoner_id = summoner_id
        # data is a list of MatchSummary objects
        if type(matches) == type([]):
            self += [MatchSummary(match, summoner_id) for match in matches]
        else:
            raise TypeError('Invalid input data. Type:', type(matches))

    def write(self, db):
        for match in self:
#            print('  Writing match:',match['matchId'])
            match.write(db)


class MatchSummary(dict):
    def __init__(self, data, summoner_id):
        # data is a dict containing the following information:
        # +------------------------+----------------------+-----------------------+
        # | Field                  | Dict Key             | Type                  |
        # +------------------------+----------------------+-----------------------+
        # | Map ID                 | mapId                | int                   |
        # | Match Creation Time    | matchCreation        | int                   |
        # | Match Duration         | matchDuration        | int                   |
        # | Match ID               | matchId              | int                   |
        # | Match Mode             | matchMode            | str                   |
        # | Match Type             | matchType            | str                   |
        # | Match Version          | matchVersion         | str                   |
        # | Participant Identities | participantIdentites | [ParticipantIdentity] |
        # | Participants           | participants         | [Participant]         |
        # | Platform ID            | platformId           | str                   |
        # | Queue Type             | queueType            | str                   |
        # | Region                 | region               | str                   |
        # | Season                 | season               | str                   |
        # +------------------------+----------------------+-----------------------+
        keys = self.getKeys()
        self.update({key:None for key in keys})
        if type(data) == type({}):
            self.update(data)
            self['participantIdentities'] = [ParticipantIdentity(item, self['matchId']) \
                                             for item in data['participantIdentities']   ]
            self['participants']          = [Participant(item, self['matchId'], summoner_id) for item in data['participants']]
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        try:
            data = self.getDbData()
            insert_str = 'INSERT INTO match_summaries VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            # We already have this match data, do nothing
            pass
#            print('    Match', self['matchId'], 'already in db')
        conn.commit()
        conn.close()
        [participant_identity.write(db) for participant_identity in self['participantIdentities']]
        [participant.write(db) for participant in self['participants']]

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys() if key not in ['participants', 'participantIdentities']])

    def __str__(self):
        out_str  = 'Map=' + str(self['mapId']) + ' Season=' + self['season'] + ' MatchId=' + str(self['matchId'])
        out_str += ' CreationTime=' + str(self['matchCreation']) + os.linesep
        for (participant, participant_identity) in zip(self['participants'], self['participantIdentities']):
            out_str += '    '  + participant_identity['player']['summonerName']
            out_str += ' - ' + str(participant['championId']).rjust(3) + ' ' + str(participant['stats']['winner'])
        return out_str

    def __repr__(self):
        return str(self)

    @staticmethod
    def getKeys():
        return ['mapId'       , 'matchCreation', 'matchDuration'        ,\
                'matchId'     , 'matchMode'    , 'matchType'            ,\
                'matchVersion', 'participants' , 'participantIdentities',\
                'platformId'  , 'queueType'    , 'region'               ,\
                'season'                                                 ]

    @staticmethod
    def getSqlTableFormatStr():
        # participant_ids is a key for lookups in the participant_identities table
        # participants is a key for lookups in the participants table
        return 'CREATE TABLE IF NOT EXISTS match_summaries (\
                  mapId         integer NOT NULL ,\
                  matchCreation integer NOT NULL ,\
                  matchDuration integer NOT NULL ,\
                  matchId       integer NOT NULL ,\
                  matchMode     text    NOT NULL ,\
                  matchType     text    NOT NULL ,\
                  matchVersion  text    NOT NULL ,\
                  platformId    text    NOT NULL ,\
                  queueType     text    NOT NULL ,\
                  region        text    NOT NULL ,\
                  season        text    NOT NULL ,\
                  PRIMARY KEY(matchId)           )'


class ParticipantIdentity(dict):
    def __init__(self, data, match_id):
        # data is a dict containing the following information:
        # +----------------+---------------+--------+
        # | Field          | Dict Key      | Type   |
        # +----------------+---------------+--------+
        # | Participant ID | participantId | int    |
        # | Player         | player        | Player |
        # +----------------+---------------+--------+
        keys = self.getKeys()
        self.update({key:None for key in keys})
        if type(data) == type({}):
            self.update(data)
            self['matchId'] = match_id
            self['player']  = Player(data['player'])
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        insert_str = 'INSERT INTO participant_identities VALUES (' + ', '.join(['?'] * len(data)) + ')'
        try:
            c.execute(insert_str, data)
        except sql.IntegrityError:
            pass
        conn.commit()
        conn.close()

    def getDbData(self):
        return [self['participantId'], self['player']['summonerId'], self['matchId']]

    @staticmethod
    def getKeys():
        return ['participantId', 'player', 'matchId']

    @staticmethod
    def getSqlTableFormatStr():
        return 'CREATE TABLE IF NOT EXISTS participant_identities (\
                  participantId integer NOT NULL ,\
                  summonerId    integer NOT NULL ,\
                  matchId       integer NOT NULL ,\
                  UNIQUE(summonerId, matchId)    )'


# Player has no table associated with it, the data here can be gleaned
#   from the summoners table with the exeption of the Match History URI
class Player(dict):
    def __init__(self, data):
        # data is a dict containing the following information:
        # +-------------------+-----------------+--------+
        # | Field             | Dict Key        | Type   |
        # +-------------------+-----------------+--------+
        # | Match History URI | matchHistoryUri | string |
        # | Profile Icon      | profileIcon     | int    |
        # | Summoner ID       | summonerId      | int    |
        # | Summoner Name     | summonerName    | string |
        # +-------------------+-----------------+--------+
        keys = ['matchHistoryUri', 'profileIcon', 'summonerId', 'summonerName']
        self.update({key:None for key in keys})
        if type(data) == type({}):
            self.update(data)
        else:
            raise TypeError('Invalid input data. Type:', type(data))


class Participant(dict):
    def __init__(self, data, match_id, summoner_id):
        # data is a dict containing the following information:
        # +------------------------------+---------------------------+---------------------+
        # | Field                        | Dict Key                  | Type                |
        # +------------------------------+---------------------------+---------------------+
        # | Champion ID                  | championId                | int                 |
        # | Highest Achieved Season Tier | highestAchievedSeasonTier | string              |
        # | Masteries                    | masteries                 | [Mastery]           |
        # | Participant ID               | participantId             | int                 |
        # | Runes                        | runes                     | [Rune]              |
        # | Spell 1 ID                   | spell2Id                  | int                 |
        # | Spell 2 ID                   | spell1Id                  | int                 |
        # | Stats                        | stats                     | ParticipantStats    |
        # | Team ID                      | teamId                    | int                 |
        # | Timeline                     | timeline                  | ParticipantTimeline |
        # +------------------------------+---------------------------+---------------------+
        keys = self.getKeys()
        self.update({key:None for key in keys})
        if type(data) == type({}):
            self.update(data)
            self['matchId'] = match_id
            self['summonerId'] = summoner_id
            if 'masteries' in data:
                self['masteries'] = [Mastery(item, self['matchId'], self['summonerId']) \
                                     for item in data['masteries']]
            if 'runes' in data:
                self['runes']     = [Rune(item, self['matchId'], self['summonerId'])    \
                                     for item in data['runes']]
            self['stats']     = ParticipantStats(data['stats'], self['matchId'], self['summonerId'])
            self['timeline']  = ParticipantTimeline(data['timeline'], self['matchId'], self['summonerId'])
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        insert_str = 'INSERT INTO participants VALUES (' + ', '.join(['?'] * len(data)) + ')'
        try:
            c.execute(insert_str, data)
        except sql.IntegrityError:
            conn.close()
            return
        conn.commit()
        conn.close()
        if self['masteries']:
            [mastery.write(db) for mastery in self['masteries']]
        if self['runes']:
            [rune.write(db)    for rune    in self['runes']    ]
        self['stats'].write(db)
        self['timeline'].write(db)

    def getDbData(self):
        keys = self.getKeys()
        keys.remove('masteries')
        keys.remove('runes')
        keys.remove('stats')
        keys.remove('timeline')
        return tuple([self[key] for key in keys])

    @staticmethod
    def getKeys():
        return ['championId'               ,\
                'highestAchievedSeasonTier',\
                'masteries'                ,\
                'summonerId'               ,\
                'runes'                    ,\
                'spell1Id'                 ,\
                'spell2Id'                 ,\
                'stats'                    ,\
                'teamId'                   ,\
                'timeline'                 ,\
                'matchId'                   ]

    @staticmethod
    def getSqlTableFormatStr():
        # Data looked up by match_id + summoner_id:
        #   Runes
        #   Masteries
        #   ParticipantStats
        #   ParticipantTimeline
        return 'CREATE TABLE IF NOT EXISTS participants      (\
                  championId                integer NOT NULL ,\
                  highestAchievedSeasonTier text    NOT NULL ,\
                  summonerId                integer NOT NULL ,\
                  spell1Id                  integer NOT NULL ,\
                  spell2Id                  integer NOT NULL ,\
                  teamId                    integer NOT NULL ,\
                  matchId                   integer NOT NULL ,\
                  UNIQUE(matchId, summonerId)                )'


class Mastery(dict):
    def __init__(self, data, match_id, summoner_id):
        # data is a dict containing the following information:
        # +--------------+-----------+------+
        # | Field        | Dict Key  | Type |
        # +--------------+-----------+------+
        # | Mastery ID   | masteryId | int  |
        # | Mastery Rank | rank      | int  |
        # +--------------+-----------+------+
        keys = self.getKeys()
        self.update({key:None for key in keys})
        if type(data) == type({}):
            self.update(data)
            self['matchId']    = match_id
            self['summonerId'] = summoner_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        insert_str = 'INSERT INTO masteries VALUES (' + ', '.join(['?'] * len(data)) + ')'
        c.execute(insert_str, data)
        conn.commit()
        conn.close()

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    @staticmethod
    def getKeys():
        return ['masteryId', 'rank', 'matchId', 'summonerId']

    @staticmethod
    def getSqlTableFormatStr():
        return 'CREATE TABLE IF NOT EXISTS masteries (\
                  masteryId  integer NOT NULL        ,\
                  rank       integer NOT NULL        ,\
                  matchId    integer NOT NULL        ,\
                  summonerId integer NOT NULL        ,\
                  UNIQUE(matchId, summonerId, masteryId, rank))'


class Rune(dict):
    def __init__(self, data, match_id, summoner_id):
        # data is a dict containing the following information:
        # +-----------+----------+------+
        # | Field     | Dict Key | Type |
        # +-----------+----------+------+
        # | Rune Rank | rank     | int  |
        # | Rune ID   | runeId   | int  |
        # +-----------+----------+------+
        keys = self.getKeys()
        self.update({key:None for key in keys})
        if type(data) == type({}):
            self.update(data)
            self['matchId']    = match_id
            self['summonerId'] = summoner_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        insert_str = 'INSERT INTO runes VALUES (' + ', '.join(['?'] * len(data)) + ')'
        c.execute(insert_str, data)
        conn.commit()
        conn.close()

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    @staticmethod
    def getKeys():
        return ['rank', 'runeId', 'matchId', 'summonerId']

    @staticmethod
    def getSqlTableFormatStr():
        return 'CREATE TABLE IF NOT EXISTS runes        (\
                  runeId     integer NOT NULL           ,\
                  rank       integer NOT NULL           ,\
                  matchId    integer NOT NULL           ,\
                  summonerId integer NOT NULL           )'


class ParticipantStats(dict):
    def __init__(self, data, match_id, summoner_id):
        # data is a dict containing the following information:
        # +-------------------------------------+---------------------------------+------+
        # | Field                               | Dict Key                        | Type |
        # +-------------------------------------+---------------------------------+------+
        # | Assists                             | assists                         | int  |
        # | Champion Level                      | champLevel                      | int  |
        # | Combat Player Score                 | combatPlayerScore               | int  |
        # | Deaths                              | deaths                          | int  |
        # | Double Kills                        | doubleKills                     | int  |
        # | First Blood Assist                  | firstBloodAssist                | bool |
        # | First Blood Kill                    | firstBloodKill                  | bool |
        # | First Inhibitor Assist              | firstInhibitorAssist            | bool |
        # | First Inhibitor Kill                | firstInhibitorKill              | bool |
        # | First Tower Assist                  | firstTowerAssist                | bool |
        # | First Tower Kill                    | firstTowerKill                  | bool |
        # | Gold Earned                         | goldEarned                      | int  |
        # | Gold Spent                          | goldSpent                       | int  |
        # | Inhibitor Kills                     | inhibitorKills                  | int  |
        # | Item 0 ID                           | item0                           | int  |
        # | Item 1 ID                           | item1                           | int  |
        # | Item 2 ID                           | item2                           | int  |
        # | Item 3 ID                           | item3                           | int  |
        # | Item 4 ID                           | item4                           | int  |
        # | Item 5 ID                           | item5                           | int  |
        # | Item 6 ID                           | item6                           | int  |
        # | Killing Sprees                      | killingSprees                   | int  |
        # | Kills                               | kills                           | int  |
        # | Largest Critical Strike             | largestCriticalStrike           | int  |
        # | Largest Killing Spree               | largestKillingSpree             | int  |
        # | Largest Multi Kill                  | largestMultiKill                | int  |
        # | Magic Damage Dealt                  | magicDamageDealt                | int  |
        # | Magic Damage Dealt To Champions     | magicDamageDealtToChampions     | int  |
        # | Magic Damage Taken                  | magicDamageTaken                | int  |
        # | Minions Killed                      | minionsKilled                   | int  |
        # | Neutral Minions Killed              | neutralMinionsKilled            | int  |
        # | Neutral Minions Killed Enemy Jungle | neutralMinionsKilledEnemyJungle | int  |
        # | Neutral Minions Killed Team Jungle  | neutralMinionsKilledTeamJungle  | int  |
        # | Node Captures                       | nodeCapture                     | int  |
        # | Node Capture Assists                | nodeCaptureAssist               | int  |
        # | Node Neutralizations                | nodeNeutralize                  | int  |
        # | Node Neutralization Assists         | nodeNeutralizeAssist            | int  |
        # | Objective Player Score              | objectivePlayerScore            | int  |
        # | Penta Kills                         | pentaKills                      | int  |
        # | Physical Damage Dealt               | physicalDamageDealt             | int  |
        # | Physical Damage Dealth To Champions | physicalDamageDealtToChampions  | int  |
        # | Physical Damage Taken               | physicalDamageTaken             | int  |
        # | Quadra Kills                        | quadraKills                     | int  |
        # | Sight Wards Bought In Game          | sightWardsBoughtInGame          | int  |
        # | Team Objectives Completed           | teamObjective                   | int  |
        # | Total Damage Dealt                  | totalDamageDealt                | int  |
        # | Total Damage Dealt To Champions     | totalDamageDealtToChampions     | int  |
        # | Total Damage Taken                  | totalDamageTaken                | int  |
        # | Total Healing Done                  | totalHeal                       | int  |
        # | Total Player Score                  | totalPlayerScore                | int  |
        # | Total Score Rank                    | totalScoreRank                  | int  |
        # | Total Time Crowd Control Dealt      | totalTimeCrowdControlDealt      | int  |
        # | Total Units Healed                  | totalUnitsHealed                | int  |
        # | Tower Kills                         | towerKills                      | int  |
        # | Triple Kills                        | tripleKills                     | int  |
        # | True Damage Dealt                   | trueDamageDealt                 | int  |
        # | True Damage Dealt To Champions      | trueDamageDealtToChampions      | int  |
        # | True Damage Taken                   | trueDamageTaken                 | int  |
        # | Unreal Kills                        | unrealKills                     | int  |
        # | Vision Wards Bought In Game         | visionWardsBoughtInGame         | int  |
        # | Wards Killed                        | wardsKilled                     | int  |
        # | Wards Placed                        | wardsPlaced                     | int  |
        # | Winner                              | winner                          | bool |
        # +-------------------------------------+---------------------------------+------+
        self.update({key:None for key in self.getKeys()})
        self['matchId'] = match_id
        self['summonerId'] = summoner_id
        if type(data) == type({}):
            self.update(data)
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        insert_str = 'INSERT INTO participant_stats VALUES (' + ', '.join(['?'] * len(data)) + ')'
        c.execute(insert_str, data)
        conn.commit()
        conn.close()

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    @staticmethod
    def getKeys():
        return ['matchId'                         ,\
                'summonerId'                      ,\
                'assists'                         ,\
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

    @staticmethod
    def getSqlTableFormatStr():
        # Take the dict keys from above and map it to the table keys
        keys = ParticipantStats.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS participant_stats('
        columns = []
        for key in keys:
            if   key in ['firstBloodAssist'   ,\
                         'firstBloodKill'     ,\
                         'firstIhibitorAssist',\
                         'firstInhibitorKill' ,\
                         'firstTowerAssist'   ,\
                         'firstTowerKill'     ,\
                         'winner'              ]:
                columns.append(key + ' bool NOT NULL')
            elif key in ['combatPlayerScore'       ,\
                         'nodeCapture'             ,\
                         'nodeCaptureAssist'       ,\
                         'nodeNeutralize'          ,\
                         'nodeNeutralizeAssist'    ,\
                         'objectivePlayerScore'    ,\
                         'teamObjectivesCompleted' ,\
                         'teamObjective'           ,\
                         'totalPlayerScore'        ,\
                         'totalScoreRank'           ]:
                columns.append(key + ' integer')
            else:
                columns.append(key + ' integer NOT NULL')
        table_str += ', '.join(columns) + ', UNIQUE(matchId, summonerId) )'
        return table_str


class ParticipantTimeline(dict): # TODO Apply this methodology to other classes. static getKeys
    def __init__(self, data, match_id, summoner_id):
        # data is a dict containing the following information:
        # +-------------------------------------------+---------------------------------+-------------------------+
        # | Field                                     | Dict Key                        | Type                    |
        # +-------------------------------------------+---------------------------------+-------------------------+
        # | Ancient Golem Assists Per Minute Counts   | ancientGolemAssistsPerMinCounts | ParticipantTimelineData |
        # | Ancient Golem Kills Per Minute Counts     | ancientGolemKillsPerMinCounts   | ParticipantTimelineData |
        # | Assisted Lane Deaths Per Minute Deltas    | assistedLaneDeathsPerMinDeltas  | ParticipantTimelineData |
        # | Assisted Lane Kills Per Minute Deltas     | assistedLaneKillsPerMinDeltas   | ParticipantTimelineData |
        # | Baron Assists Per Minute Counts           | baronAssistsPerMinCounts        | ParticipantTimelineData |
        # | Baron Kills Per Minute Counts             | baronKillsPerMinCounts          | ParticipantTimelineData |
        # | Creeps Per Minute Deltas                  | creepsPerMinDeltas              | ParticipantTimelineData |
        # | CS Difference Per Minute Deltas           | csDiffPerMinDeltas              | ParticipantTimelineData |
        # | Damage Taken Difference Per Minute Deltas | damageTakenDiffPerMinDeltas     | ParticipantTimelineData |
        # | Damage Taken Per Minute Deltas            | damageTakenPerMinDeltas         | ParticipantTimelineData |
        # | Dragon Assists Per Minute Counts          | dragonAssistsPerMinCounts       | ParticipantTimelineData |
        # | Dragon Kills Per Minute Counts            | dragonKillsPerMinCounts         | ParticipantTimelineData |
        # | Elder Lizard Assists Per Minute Counts    | elderLizardAssistsPerMinCounts  | ParticipantTimelineData |
        # | Elder Lizard Kills Per Minute Counts      | elderLizardKillsPerMinCounts    | ParticipantTimelineData |
        # | Gold Per Minute Deltas                    | goldPerMinDeltas                | ParticipantTimelineData |
        # | Inhibitor Assists Per Minute Counts       | inhibitorAssistsPerMinCounts    | ParticipantTimelineData |
        # | Inhibitor Kills Per Minute Counts         | inhibitorKillsPerMinCounts      | ParticipantTimelineData |
        # | Lane                                      | lane                            | str                     |
        # | Role                                      | role                            | str                     |
        # | Tower Assists Per Minute Counts           | towerAssistsPerMinCounts        | ParticipantTimelineData |
        # | Tower Kills Per Minute Counts             | towerKillsPerMinCounts          | ParticipantTimelineData |
        # | Tower Kills Per Minute Deltas             | towerKillsPerMinDeltas          | ParticipantTimelineData |
        # | Vilemaw Assists Per Minute Counts         | vilemawAssistsPerMinCounts      | ParticipantTimelineData |
        # | Vilemaw Kills Per Minute Counts           | vilemawKillsPerMinCounts        | ParticipantTimelineData |
        # | Wards Placed Per Minute Deltas            | wardsPerMinDeltas               | ParticipantTimelineData |
        # | Experience Difference Per Minute Deltas   | xpDiffPerMinDeltas              | ParticipantTimelineData |
        # | Experience Per Minute Deltas              | xpPerMinDeltas                  | ParticipantTimelineData |
        # +-------------------------------------------+---------------------------------+-------------------------+
        self.update({key:None for key in self.getKeys()})
        self['matchId'] = match_id
        self['summonerId'] = summoner_id
        if type(data) == type({}):
            expanded_data = {}
            for key in self.getKeys():
                if key not in ['lane','role']:
                    try:
                        if key.endswith('_0_10'):
                            d_key = key[:-5]
                            expanded_data[key] = data[d_key]['zeroToTen']
                        if key.endswith('_10_20'):
                            d_key = key[:-6]
                            expanded_data[key] = data[d_key]['tenToTwenty']
                        if key.endswith('_20_30'):
                            d_key = key[:-6]
                            expanded_data[key] = data[d_key]['twentyToThirty']
                        if key.endswith('_30_end'):
                            d_key = key[:-7]
                            expanded_data[key] = data[d_key]['thirtyToEnd']
                    except KeyError as err:
                        d_keys = ['ancientGolemAssistsPerMinCounts' ,\
                                  'ancientGolemKillsPerMinCounts'   ,\
                                  'assistedLaneDeathsPerMinDeltas'  ,\
                                  'assistedLaneKillsPerMinDeltas'   ,\
                                  'baronAssistsPerMinCounts'        ,\
                                  'baronKillsPerMinCounts'          ,\
                                  'creepsPerMinDeltas'              ,\
                                  'csDiffPerMinDeltas'              ,\
                                  'damageTakenDiffPerMinDeltas'     ,\
                                  'damageTakenPerMinDeltas'         ,\
                                  'dragonAssistsPerMinCounts'       ,\
                                  'dragonKillsPerMinCounts'         ,\
                                  'elderLizardAssistsPerMinCounts'  ,\
                                  'elderLizardKillsPerMinCounts'    ,\
                                  'goldPerMinDeltas'                ,\
                                  'inhibitorAssistsPerMinCounts'    ,\
                                  'inhibitorKillsPerMinCounts'      ,\
                                  'towerAssistsPerMinCounts'        ,\
                                  'towerKillsPerMinCounts'          ,\
                                  'towerKillsPerMinDeltas'          ,\
                                  'vilemawAssistsPerMinCounts'      ,\
                                  'vilemawKillsPerMinCounts'        ,\
                                  'wardsPerMinDeltas'               ,\
                                  'xpDiffPerMinDeltas'              ,\
                                  'xpPerMinDeltas'                  ,\
                                  'zeroToTen'                       ,\
                                  'tenToTwenty'                     ,\
                                  'twentyToThirty'                  ,\
                                  'thirtyToEnd'                      ]
                        if err.args[0] not in d_keys:
                            raise
                else:
                    expanded_data[key] = data[key]
            self.update(expanded_data)
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        insert_str = 'INSERT INTO participant_timelines VALUES (' + ', '.join(['?'] * len(data)) + ')'
        c.execute(insert_str, data)
        conn.commit()
        conn.close()

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    @staticmethod
    def getKeys():
        keys = ['ancientGolemAssistsPerMinCounts' ,\
                'ancientGolemKillsPerMinCounts'   ,\
                'assistedLaneDeathsPerMinDeltas'  ,\
                'assistedLaneKillsPerMinDeltas'   ,\
                'baronAssistsPerMinCounts'        ,\
                'baronKillsPerMinCounts'          ,\
                'creepsPerMinDeltas'              ,\
                'csDiffPerMinDeltas'              ,\
                'damageTakenDiffPerMinDeltas'     ,\
                'damageTakenPerMinDeltas'         ,\
                'dragonAssistsPerMinCounts'       ,\
                'dragonKillsPerMinCounts'         ,\
                'elderLizardAssistsPerMinCounts'  ,\
                'elderLizardKillsPerMinCounts'    ,\
                'goldPerMinDeltas'                ,\
                'inhibitorAssistsPerMinCounts'    ,\
                'inhibitorKillsPerMinCounts'      ,\
                'towerAssistsPerMinCounts'        ,\
                'towerKillsPerMinCounts'          ,\
                'towerKillsPerMinDeltas'          ,\
                'vilemawAssistsPerMinCounts'      ,\
                'vilemawKillsPerMinCounts'        ,\
                'wardsPerMinDeltas'               ,\
                'xpDiffPerMinDeltas'              ,\
                'xpPerMinDeltas'                   ]
        expanded_keys = ['matchId', 'summonerId', 'lane', 'role']
        expanded_key_sets = []
        expanded_key_sets = [[item + '_0_10', item + '_10_20', item + '_20_30', item + '_30_end'] for item in keys]
        for key_set in expanded_key_sets:
            expanded_keys += key_set
        return expanded_keys


    @staticmethod
    def getSqlTableFormatStr():
        # Take the dict keys from above and map it to the table keys
        keys = ParticipantTimeline.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS participant_timelines('
        columns = []
        for key in keys:
            if key in ['lane', 'role']:
                columns.append(key + ' text NOT NULL')
            elif key in ['matchId', 'summonerId']:
                columns.append(key + ' integer NOT NULL')
            else:
                columns.append(key + ' real')
        table_str += ', '.join(columns) + ', UNIQUE(matchId, summonerId) )'
        return table_str


#----------------------------------------------------------------------------------------------------------#
# Stats Classes (StatsApi):                                                                                #
#   PlayerStatsSummaryList                                                                                 #
#   PlayerStatSummary                                                                                      #
#   AggregatedStats                                                                                        #
#----------------------------------------------------------------------------------------------------------#

class PlayerStatsSummaryList(list):
    def __init__(self, data):
        # data is a dict containing the following information:
        # +-----------------------+---------------------+-------------------------+
        # | Field                 | Dict Key            | Type                    |
        # +-----------------------+---------------------+-------------------------+
        # | Player Stat Summaries | playerStatSummaries | [PlayerStatsSummaryDto] |
        # | Summoner ID           | summonerId          | int                     |
        # +-----------------------+---------------------+-------------------------+
        if type(data) == type({}):
            self.summoner_id = data['summonerId']
            self += [PlayerStatSummary(summary, data['summonerId']) for summary in data['playerStatSummaries']]
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        [summary.write(db) for summary in self]

    def __str__(self):
        out_strs = ['Summoner ID: ' + str(self.summoner_id)]
        for summary in self:
            if summary['losses']:
                out_strs.append(summary['playerStatSummaryType'] + ' win/loss: ' + str(summary['wins']) + '/' + str(summary['losses']))
            else:
                out_strs.append(summary['playerStatSummaryType'] + ' wins: ' + str(summary['wins']))
        return (os.linesep + '  ').join(out_strs)

    def __repr__(self):
        return str(self)


class PlayerStatSummary(dict):
    def __init__(self, data, summoner_id):
        # data is a dict containing the following information:
        # +--------------------------+-----------------------+--------------------+
        # | Field                    | Dict Key              | Type               |
        # +--------------------------+-----------------------+--------------------+
        # | Aggregated Stats         | aggregatedStats       | AggregatedStatsDto |
        # | Losses                   | losses                | int                |
        # | Modify Date              | modifyDate            | float              |
        # | Player Stat Summary Type | playerStatSummaryType | str                |
        # | Wins                     | wins                  | int                |
        # +--------------------------+-----------------------+--------------------+
        self.update({key:None for key in self.getKeys()})
        if type(data) == type({}):
            self.update(data)
            self['summonerId'] = summoner_id
            self['aggregatedStats'] = AggregatedStats(data['aggregatedStats'], summoner_id, self['playerStatSummaryType'])
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        try:
            insert_str = 'INSERT INTO player_stat_summaries VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            update_str = 'UPDATE player_stat_summaries SET '
            updates = [key + '=?' for key in self.getKeys()]
            update_str += ', '.join(updates) + ' WHERE summonerId=? AND playerStatSummaryType=?'
            c.execute(update_str             ,\
                       self.getDbData() +\
                      (self['summonerId'], self['playerStatSummaryType']) )
        conn.commit()
        conn.close()
        self['aggregatedStats'].write(db)

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    @staticmethod
    def getKeys():
        return ['losses'                ,\
                'modifyDate'            ,\
                'playerStatSummaryType' ,\
                'wins'                  ,\
                'summonerId'             ]

    @staticmethod
    def getSqlTableFormatStr():
        keys      = PlayerStatSummary.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS player_stat_summaries('
        columns   = []
        for key in keys:
            if   key in ['playerStatSummaryType']:
                columns.append(key + ' text NOT NULL')
            elif key in ['losses']:
                columns.append(key + ' integer')
            elif key in ['modifyDate']:
                columns.append(key + ' real NOT NULL')
            else:
                columns.append(key + ' integer NOT NULL')
        return table_str + ', '.join(columns) + ', UNIQUE(summonerId, playerStatSummaryType) )'


class AggregatedStats(dict):
    def __init__(self, data, summoner_id, player_stat_summary_type):
        # data is a dict containing the following information:
        # +---------------------------------+-----------------------------+------+
        # | Field                           | Dict Key                    | Type |
        # +---------------------------------+-----------------------------+------+
        # | Average Assists                 | averageAssists              | int  |
        # | Average Champions Killed        | averageChampionsKilled      | int  |
        # | Average Combat Player Score     | averageCombatPlayerScore    | int  |
        # | Average Nodes Captured          | averageNodeCapture          | int  |
        # | Average Node Capture Assists    | averageNodeCaptureAssist    | int  |
        # | Average Nodes Neutralized       | averageNodeNeutralize       | int  |
        # | Average Node Neutralize Assists | averageNodeNeutralizeAssist | int  |
        # | Average Number of Deaths        | averageNumDeaths            | int  |
        # | Average Objective Player Score  | averageObjectivePlayerScore | int  |
        # | Average Team Objective          | averageTeamObjective        | int  |
        # | Average Total Player Score      | averageTotalPlayerScore     | int  |
        # | Bot Games Played                | botGamesPlayed              | int  |
        # | Killing Spree                   | killingSpree                | int  |
        # | Max Assists                     | maxAssists                  | int  |
        # | Max Champions Killed            | maxChampionsKilled          | int  |
        # | Max Combat Player Score         | maxCombatPlayerScore        | int  |
        # | Max Largest Critical Strike     | maxLargestCriticalStrike    | int  |
        # | Max Largest Killing Spree       | maxLargestKillingSpree      | int  |
        # | Max Nodes Captured              | maxNodeCapture              | int  |
        # | Max Node Capture Assists        | maxNodeCaptureAssist        | int  |
        # | Max Nodes Neutralized           | maxNodeNeutralize           | int  |
        # | Max Node Neutralize Assists     | maxNodeNeutralizeAssist     | int  |
        # | Max Number of Deaths            | maxNumDeaths                | int  |
        # | Max Objective Player Score      | maxObjectivePlayerScore     | int  |
        # | Max Team Objectives             | maxTeamObjective            | int  |
        # | Max Time Played                 | maxTimePlayed               | int  |
        # | Max Time Spent Living           | maxTimeSpentLiving          | int  |
        # | Max Total Player Score          | maxTotalPlayerScore         | int  |
        # | Most Champion Kills Per Session | mostChampionKillsPerSession | int  |
        # | Most Spells Cast                | mostSpellsCast              | int  |
        # | Normal Games Played             | normalGamesPlayed           | int  |
        # | Ranked Premade Games Played     | rankedPremadeGamesPlayed    | int  |
        # | Ranked Solo Games Played        | rankedSoloGamesPlayed       | int  |
        # | Total Assists                   | totalAssists                | int  |
        # | Total Champion Kills            | totalChampionKills          | int  |
        # | Total Damage Dealt              | totalDamageDealt            | int  |
        # | Total Damage Taken              | totalDamageTaken            | int  |
        # | Total Deaths Per Session        | totalDeathsPerSession       | int  |
        # | Total Double Kills              | totalDoubleKills            | int  |
        # | Total First Blood               | totalFirstBlood             | int  |
        # | Total Gold Earned               | totalGoldEarned             | int  |
        # | Total Heal                      | totalHeal                   | int  |
        # | Total Magic Damage Dealt        | totalMagicDamageDealt       | int  |
        # | Total Minion Kills              | totalMinionKills            | int  |
        # | Total Neutral Minions Killed    | totalNeutralMinionsKilled   | int  |
        # | Total Nodes Captured            | totalNodeCapture            | int  |
        # | Total Nodes Neutralized         | totalNodeNeutralize         | int  |
        # | Total Penta Kills               | totalPentaKills             | int  |
        # | Total Physical Damage Dealt     | totalPhysicalDamageDealt    | int  |
        # | Total Quadra Kills              | totalQuadraKills            | int  |
        # | Total Sessions Lost             | totalSessionsLost           | int  |
        # | Total Sessions Played           | totalSessionsPlayed         | int  |
        # | Total Sessions Won              | totalSessionsWon            | int  |
        # | Total Triple Kills              | totalTripleKills            | int  |
        # | Total Turrets Killed            | totalTurretsKilled          | int  |
        # | Total Unreal Kills              | totalUnrealKills            | int  |
        # +---------------------------------+-----------------------------+------+
        self.update({key:None for key in self.getKeys()})
        if type(data) == type({}):
            self.update(data)
            self['playerStatSummaryType']  = player_stat_summary_type
            self['summonerId'] = summoner_id
        else:
            raise TypeError('Invalid input data. Type:', type(data))

    def write(self, db):
        conn = sql.connect(db)
        c    = conn.cursor()
        data = self.getDbData()
        try:
            insert_str = 'INSERT INTO player_aggregate_stats VALUES (' + ', '.join(['?'] * len(data)) + ')'
            c.execute(insert_str, data)
        except sql.IntegrityError:
            update_str = 'UPDATE player_aggregate_stats SET '
            updates = [key + '=?' for key in self.getKeys()]
            update_str += ', '.join(updates) + ' WHERE summonerId=? AND playerStatSummaryType=?'
            c.execute(update_str             ,\
                       self.getDbData() +\
                      (self['summonerId'], self['playerStatSummaryType']) )
        conn.commit()
        conn.close()

    def getDbData(self):
        return tuple([self[key] for key in self.getKeys()])

    @staticmethod
    def getKeys():
        return ['averageAssists'              ,\
                'averageChampionsKilled'      ,\
                'averageCombatPlayerScore'    ,\
                'averageNodeCapture'          ,\
                'averageNodeCaptureAssist'    ,\
                'averageNodeNeutralize'       ,\
                'averageNodeNeutralizeAssist' ,\
                'averageNumDeaths'            ,\
                'averageObjectivePlayerScore' ,\
                'averageTeamObjective'        ,\
                'averageTotalPlayerScore'     ,\
                'botGamesPlayed'              ,\
                'killingSpree'                ,\
                'maxAssists'                  ,\
                'maxChampionsKilled'          ,\
                'maxCombatPlayerScore'        ,\
                'maxLargestCriticalStrike'    ,\
                'maxLargestKillingSpree'      ,\
                'maxNodeCapture'              ,\
                'maxNodeCaptureAssist'        ,\
                'maxNodeNeutralize'           ,\
                'maxNodeNeutralizeAssist'     ,\
                'maxNumDeaths'                ,\
                'maxObjectivePlayerScore'     ,\
                'maxTeamObjective'            ,\
                'maxTimePlayed'               ,\
                'maxTimeSpentLiving'          ,\
                'maxTotalPlayerScore'         ,\
                'mostChampionKillsPerSession' ,\
                'mostSpellsCast'              ,\
                'normalGamesPlayed'           ,\
                'rankedPremadeGamesPlayed'    ,\
                'rankedSoloGamesPlayed'       ,\
                'totalAssists'                ,\
                'totalChampionKills'          ,\
                'totalDamageDealt'            ,\
                'totalDamageTaken'            ,\
                'totalDeathsPerSession'       ,\
                'totalDoubleKills'            ,\
                'totalFirstBlood'             ,\
                'totalGoldEarned'             ,\
                'totalHeal'                   ,\
                'totalMagicDamageDealt'       ,\
                'totalMinionKills'            ,\
                'totalNeutralMinionsKilled'   ,\
                'totalNodeCapture'            ,\
                'totalNodeNeutralize'         ,\
                'totalPentaKills'             ,\
                'totalPhysicalDamageDealt'    ,\
                'totalQuadraKills'            ,\
                'totalSessionsLost'           ,\
                'totalSessionsPlayed'         ,\
                'totalSessionsWon'            ,\
                'totalTripleKills'            ,\
                'totalTurretsKilled'          ,\
                'totalUnrealKills'            ,\
                'playerStatSummaryType'       ,\
                'summonerId'                   ]

    @staticmethod
    def getSqlTableFormatStr():
        keys      = AggregatedStats.getKeys()
        table_str = 'CREATE TABLE IF NOT EXISTS player_aggregate_stats('
        columns   = []
        for key in keys:
            if key in ['summonerId']:
                columns.append(key + ' integer NOT NULL')
            elif key in ['queueType']:
                columns.append(key + ' text NOT NULL')
            else:
                columns.append(key + ' integer')
        table_str += ', '.join(columns) + ', UNIQUE(summonerId, playerStatSummaryType) )'
        return table_str

