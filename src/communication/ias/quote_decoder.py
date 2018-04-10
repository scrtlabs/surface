import base64
import binascii


class Quote(object):

    def __init__(self, quote):
        try:
            quote_bytes = base64.b64decode(quote)
            print(len(quote_bytes))
        except binascii.Error:
            quote_bytes = quote

        self.body = _Body(quote_bytes)
        self.report_body = _ReportBody(quote_bytes)
        self.signature_len = quote_bytes[432:436]
        self.signature = quote_bytes[436:]


class _Body(object):

    def __init__(self, quote):
        try:
            quote_bytes = base64.b64decode(quote)
        except binascii.Error:
            quote_bytes = quote

        self.version = quote_bytes[0:2]
        self.signature_type = quote_bytes[2:4]
        self.gid = quote_bytes[4:8]
        self.isv_svn_qe = quote_bytes[8:10]
        self.isv_svn_pce = quote_bytes[10:12]
        self.reserved = quote_bytes[12:16]
        self.basename = quote_bytes[16:48]


class _ReportBody(object):

    def __init__(self, quote):
        try:
            quote_bytes = base64.b64decode(quote)
        except binascii.Error:
            quote_bytes = quote
        self.cpusvn = quote_bytes[48:64]
        self.misc_select = quote_bytes[64:68]
        self.reserved_68 = quote_bytes[68:96]
        self.attributes = quote_bytes[96:112]
        self.mr_enclave = quote_bytes[112:144]
        self.reserved_144 = quote_bytes[144:176]
        self.mr_signer = quote_bytes[176:208]
        self.isv_prod_id = quote_bytes[2304:306]
        self.isv_SVN = quote_bytes[306:308]
        self.reserved_308 = quote_bytes[308:368]
        self.report_data = quote_bytes[368:432]


isvEnclaveQuoteBody = '''AgAAAM0LAAAGAAUAAAAAABYB+Vw5ueowf+qruQGtw+6/4XvNUSdcc8LqIanvG9qRAgb//wEBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAIGdkKKUpaKZVCtSUA9nc6C5QZBHnpDun3Neu50eDEl2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADmErAJmr/gDxSmWSY1CQFMHeugyk3piROWmu+owmjSzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADz/xrNJbdc925MpCExmRUftkGTu8UkMCST04dEcIwDcgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'''

a = Quote(isvEnclaveQuoteBody)
print(a)
print(a.signature_len)
print(len(a.signature))
print(a.body.basename)
# print(a.version)
pass

