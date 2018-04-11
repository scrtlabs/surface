import base64
import binascii
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class Quote(object):


    def __init__(self, quote=None, response_report=None):
        """
        Gets a decoded verified quote or a report + signatures and certificates.
        Assuming the Enigma Node returns the quote as a json like the following:
        { Report: *REPORT_JSON*,
        report_cert: *PEM string of the signing certificate*,
        ca_cert: *PEM string of the CA of the signing certificate*,
        sig: Signature of the whole Report made with the report_cert }
        :param quote: either a quote(base64 or bytes), or a full report(json) to be verified with intel.
        :type quote: str / bytes
        :param response_report: a json response from the Enigma node.
        :type response_report: dict
        """
        try:
            quote_bytes = base64.b64decode(quote)
        except binascii.Error:
            quote_bytes = quote

        if len(quote_bytes) == 432:
            self._build_quote(quote_bytes)

        else:
            if self.verify_report(response_report):
                self._build_quote(response_report['Report']['isvEnclaveQuoteBody'])

    def _build_quote(self, quote_bytes):
        object.__setattr__(self, 'quote_bytes', quote_bytes)
        object.__setattr__(self, 'body', _Body(quote_bytes))
        object.__setattr__(self, 'report_body', _ReportBody(quote_bytes))
        object.__setattr__(self, 'signature_len', quote_bytes[432:436])
        object.__setattr__(self, 'signature', quote_bytes[436:])

    @classmethod
    def verify_report(cls, response_report, certs):
        report_cert = x509.load_pem_x509_certificate(response_report['report_cert'], default_backend())
        # TODO: verify the chain of trust, from report_cert -> ca_cert -> Intel-cert -> (Trusted Root?)

    def __setattr__(self, key, value):
        raise ImmutableException('This object is immutable, the attributes cannot be changed')


class _Body(object):

    def __init__(self, quote_bytes):

        object.__setattr__(self, 'version', quote_bytes[0:2])
        object.__setattr__(self, 'signature_type', quote_bytes[2:4])
        object.__setattr__(self, 'gid', quote_bytes[4:8])
        object.__setattr__(self, 'isv_svn_qe', quote_bytes[8:10])
        object.__setattr__(self, 'isv_svn_pce', quote_bytes[10:12])
        object.__setattr__(self, 'reserved', quote_bytes[12:16])
        object.__setattr__(self, 'basename', quote_bytes[16:48])

    def __setattr__(self, key, value):
        raise ImmutableException('This object is immutable, the attributes cannot be changed')


class _ReportBody(object):

    def __init__(self, quote_bytes):

        object.__setattr__(self, 'cpusvn', quote_bytes[48:64])
        object.__setattr__(self, 'misc_select', quote_bytes[64:68])
        object.__setattr__(self, 'reserved', quote_bytes[68:96])
        object.__setattr__(self, 'attributes', quote_bytes[96:112])
        object.__setattr__(self, 'mr_enclave', quote_bytes[112:144])
        object.__setattr__(self, 'reserved2', quote_bytes[144:176])
        object.__setattr__(self, 'mr_signer', quote_bytes[176:208])
        object.__setattr__(self, 'reserved3', quote_bytes[208:304])
        object.__setattr__(self, 'isv_prod_id', quote_bytes[304:306])
        object.__setattr__(self, 'isv_SVN', quote_bytes[306:308])
        object.__setattr__(self, 'reserved4', quote_bytes[308:368])
        object.__setattr__(self, 'report_data', quote_bytes[368:432])

    def __setattr__(self, key, value):
        raise ImmutableException('This object is immutable, the attributes cannot be changed')


class ImmutableException(Exception):
    pass


isvEnclaveQuoteBody = '''AgAAAM0LAAAGAAUAAAAAABYB+Vw5ueowf+qruQGtw+6/4XvNUSdcc8LqIanvG9qRAgb//wEBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAIGdkKKUpaKZVCtSUA9nc6C5QZBHnpDun3Neu50eDEl2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADmErAJmr/gDxSmWSY1CQFMHeugyk3piROWmu+owmjSzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADz/xrNJbdc925MpCExmRUftkGTu8UkMCST04dEcIwDcgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'''

a = Quote(isvEnclaveQuoteBody)
a = Quote()
print(a)
print(a.signature_len)
print(len(a.signature))
a.report_body.reserved = 5
print(a.body.basename)
# print(a.version)
pass

