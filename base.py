'''
中国象棋棋谱文件基础信息
'''


def linetonums():
    '下划线字符串对应数字字符元组 列表'
    return [('_' * i, str(i)) for i in range(9, 0, -1)]
    

def xmlindent(elem, islast=False, level=0):
    'Get pretty look 取得漂亮的外观'
    def __isblank(text):
        return not text or not text.expandtabs(4).strip()

    def __addblank(text):
        return '{}{}'.format(text.expandtabs(4).strip(), tabstr)

    def __cuttab(tail, islast):
        return tail[:-1] if islast else tail

    tabstr = '\n' + level * '\t'
    if len(elem):
        elem.text = '{}\t'.format(
            tabstr if __isblank(elem.text) else __addblank(elem.text))
    for n, e in enumerate(elem):
        xmlindent(e, bool(len(elem) - 1 == n), level + 1)
    elem.tail = __cuttab(
        tabstr if __isblank(elem.tail) else __addblank(elem.tail), islast)

        
initdbsql = '''
    BEGIN;
    CREATE TABLE IF NOT EXISTS manual(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dirname TEXT,
                filename TEXT,
                content TEXT);
    CREATE TABLE IF NOT EXISTS chessmanual(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dirname TEXT NOT NULL,
                filename TEXT NOT NULL,
                remark TEXT,
                Author TEXT,
                Black TEXT,
                BlackTeam TEXT,
                Date TEXT,
                ECCO TEXT,
                Event TEXT,
                FEN TEXT,
                Format TEXT,
                Game TEXT,
                Opening TEXT,
                PlayType TEXT,
                RMKWriter TEXT,
                Red TEXT,
                RedTeam TEXT,
                Result TEXT,
                Round TEXT,
                Site TEXT,
                Title TEXT,
                Variation TEXT,
                Version TEXT);
    CREATE TABLE IF NOT EXISTS moves(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manid INTEGER NOT NULL,
                previd INTEGER NOT NULL,
                stepno INTEGER NOT NULL,
                coordstr TEXT NOT NULL,
                remark TEXT);
    CREATE TABLE IF NOT EXISTS relation(
                ancid INTEGER NOT NULL,                
                movid INTEGER NOT NULL);
    CREATE INDEX IF NOT EXISTS movid_index ON relation (movid); --非常重要！
    CREATE TRIGGER IF NOT EXISTS insert_manual  
        BEFORE INSERT
        ON manual
        WHEN (SELECT id FROM manual 
            WHERE dirname=new.dirname AND filename=new.filename) NOTNULL
        BEGIN
            DELETE FROM manual WHERE dirname=new.dirname AND filename=new.filename;
        END;
    CREATE TRIGGER IF NOT EXISTS insert_chessmanual  
        BEFORE INSERT
        ON chessmanual
        WHEN (SELECT id FROM chessmanual 
            WHERE dirname=new.dirname AND filename=new.filename) NOTNULL
        BEGIN
            DELETE FROM chessmanual WHERE dirname=new.dirname AND filename=new.filename;
        END;
    CREATE TRIGGER IF NOT EXISTS insert_moves
        AFTER INSERT
        ON moves
        BEGIN
            INSERT INTO relation SELECT ancid, new.id FROM relation WHERE movid=new.previd;
            INSERT INTO relation VALUES (new.id, new.id);
        END;
    CREATE TRIGGER IF NOT EXISTS delete_moves
        AFTER DELETE
        ON moves
        WHEN (SELECT movid FROM relation WHERE ancid=new.id) NOTNULL 
        BEGIN
            DELETE FROM moves WHERE id in (SELECT movid FROM relation WHERE ancid=new.id);
            DELETE FROM relation WHERE ancid in (SELECT movid FROM relation
                            WHERE ancid=new.id);
        END;
    '''
    

    
hastable = '''
    SELECT count(*) FROM sqlite_master
        WHERE type="table" AND name ="chessmanual"
    '''
#cur.execute(base.hastable)
#if cur.fetchone()[0] < 1:  # 全部sql语句调试好后再启用

insertmanual = '''
    INSERT INTO manual VALUES (?, ?, ?, ?)
    '''
insertinfo = '''
    INSERT INTO chessmanual VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    '''
insertmove = '''
    INSERT INTO moves VALUES (?, ?, ?, ?, ?, ?)
    '''
getlastmanid = '''
    SELECT seq FROM sqlite_sequence WHERE name="chessmanual"
    '''
getlastmovid = '''
    SELECT seq FROM sqlite_sequence WHERE name="moves"
    '''

    
#                