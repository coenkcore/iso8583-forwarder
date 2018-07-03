MSSQL_PROC_NAME = 'SP_NTB'

def mssql_proc(DBSession, params, need_commit=False):
    commit = need_commit and 'COMMIT;' or ''
    sql = """
        SET NOCOUNT ON;
        DECLARE @return_value int;
        DECLARE @out1 varchar(50);
        EXEC @return_value=[dbo].[{proc_name}] {params}, @out1 OUT;
        SELECT @return_value AS other_1, @out1 AS other_2;
        SET NOCOUNT OFF;
        {commit}
        """.format(proc_name=MSSQL_PROC_NAME, params=params, commit=commit)
    return DBSession.execute(sql)


class Query(object):
    def __init__(self, DBSession, bank_id):
        self.DBSession = DBSession
        self.bank_id = bank_id

    def transaction(self, number, method='1', need_commit=False):
        proc_input = ','.join([method, self.bank_id, number])
        self.log_info('MS-SQL procedure execute %s %s' % (MSSQL_PROC_NAME,
            proc_input))
        q = mssql_proc(self.DBSession, proc_input, need_commit)
        inv = q.fetchone()
        self.log_info('MS-SQL procedure result %s' % dict(inv))
        return inv

    def inquiry(self, invoice_id):
        return self.transaction(invoice_id)

    def payment(self, invoice_id):
        return self.transaction(invoice_id, '2', True)

    def reversal(self, ntp):
        return self.transaction(ntp, '3', True)

    def log_info(self, s):
        print(s)
