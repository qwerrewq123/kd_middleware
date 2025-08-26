class PushSql:
    def __init__(self):
        self.select_query = """select a.idx from simbizlocal.alram_event a where a.PUSH_YN = 'N'"""
        self.fcm_query = """
        INSERT INTO simbiz.tb_cm_fcm 
        (
            UID,
            TITLE,
            CONTENT,
            TRANSYN,
            CREATEDATE,
            CREATEUSER,
            READYN
        )
        SELECT 
          c.USER_ID as UID,
          '알람 발생' as TITLE,
          CONCAT(a.START_TIME, ' ', a.TAG_DESC, ' ', b.ALRAM_MEMO, ' IDX:', a.idx) as CONTENT,
          'N' as TRANSYN, 
          NOW() as CREATEDATE, 
          c.USER_ID as CREATEUSER, 
          'N' as READYN 
        FROM simbizlocal.alram_event a
        LEFT JOIN (
          SELECT 
            a.ALRAM_CD, a.ALRAM_NM, a.ALRAM_MEMO, b.TAG_NAME, b.TAG_DESC
          FROM simbizlocal.alram_code a
          LEFT JOIN simbizlocal.alram_point_set b ON a.ALRAM_CD = b.ALRAM_CD
        ) b ON a.TAG_DESC = b.TAG_DESC
        LEFT JOIN simbizlocal.alram_user c ON b.ALRAM_CD = c.ALRAM_CD
        LEFT JOIN (
          SELECT ValueTagName, pushyn 
          FROM simbizlocal.evsvgtable_read 
          GROUP BY ValueTagName
        ) d ON a.TAG_NAME = d.ValueTagName 
        LEFT JOIN simbizlocal.usermaster u ON u.USER_ID = c.USER_ID
        WHERE 
          a.CHECK_YN = 'N' 
          AND u.USEYN = 'Y' 
          AND a.PUSH_YN = 'N' 
          AND b.ALRAM_CD IS NOT NULL
          AND (
            (DAYOFWEEK(NOW()) = 1 AND c.NOT_DAY LIKE '%%일%%')
            OR (DAYOFWEEK(NOW()) = 2 AND c.NOT_DAY LIKE '%%월%%')
            OR (DAYOFWEEK(NOW()) = 3 AND c.NOT_DAY LIKE '%%화%%')
            OR (DAYOFWEEK(NOW()) = 4 AND c.NOT_DAY LIKE '%%수%%')
            OR (DAYOFWEEK(NOW()) = 5 AND c.NOT_DAY LIKE '%%목%%')
            OR (DAYOFWEEK(NOW()) = 6 AND c.NOT_DAY LIKE '%%금%%')
            OR (DAYOFWEEK(NOW()) = 7 AND c.NOT_DAY LIKE '%%토%%')
          )
          AND (
            TIME_FORMAT(NOW(), '%%H:%%i') BETWEEN 
            CONCAT(LPAD(c.START_H, 2, '0'), ':', LPAD(c.START_M, 2, '0'))
            AND 
            CONCAT(LPAD(c.END_H, 2, '0'), ':', LPAD(c.END_M, 2, '0'))
          )
          AND d.pushyn = 'Y';
        """
        self.fcm_select_query = """
            select
        a.*
        from
        (
        select a.*, b.TOKEN, b.IOS
        ,(select FCMYN from simbiz.tb_cm_companyinfo limit 1) AS FCMYN
        from simbiz.tb_cm_fcm a
        inner join simbiz.tb_cm_usermaster b on a.UID = b.UID
        where b.TOKEN != 'NO_TOKEN' and b.TOKEN is not null and a.TRANSYN = 'N'
        ) a
        where a.FCMYN = 'N'
        """
        self.alarm_event_update_query = """
        update simbizlocal.alram_event set push_yn = 'Y' where idx = %s
        """
