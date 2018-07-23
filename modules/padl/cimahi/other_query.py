MSSQL_PROC_NAME = 'SP_NTB'
TPL_SQL_TRANSACTION = """DECLARE @out varchar(50);
EXEC [dbo].[{proc_name}] {params}, @out OUT;
SELECT @out AS hasil;
{commit}"""

def list2str(d):
    r = []
    for v in d:
        s = "'" + v + "'"
        r.append(s)
    return ','.join(r)
 
def mssql_proc(DBSession, params, need_commit=False, debug=False):
    commit = need_commit and 'COMMIT;' or ''
    sql = TPL_SQL_TRANSACTION.format(
            proc_name=MSSQL_PROC_NAME, params=params, commit=commit)
    if debug:
        print(sql)
    return DBSession.execute(sql)


class Query(object):
    def __init__(self, DBSession, bank_id, debug=False):
        self.DBSession = DBSession
        self.bank_id = bank_id
        self.debug = debug

    def transaction(self, number, method='1', need_commit=False):
        proc_input = list2str([method, self.bank_id, number])
        #proc_input = ','.join([method, self.bank_id, number])
        self.log_info('MS-SQL procedure execute %s %s' % (MSSQL_PROC_NAME,
            proc_input))
        q = mssql_proc(self.DBSession, proc_input, need_commit, self.debug)
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
