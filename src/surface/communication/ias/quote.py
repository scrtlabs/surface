import base64
import binascii
import OpenSSL
import json
import requests


class Quote(object):

    def __init__(self, quote=None, response_report=None):
        """
        Gets a decoded verified quote or a report + signatures and certificates.
        Assuming the Enigma Node returns the quote as a json like the following:
        { report: *REPORT_JSON*,
          certificate: *PEM string of the signing certificate*,
          ca: *PEM string of the CA of the signing certificate*,
          signature: Signature of the whole Report made with the report_cert,
          validate: bool: Was the signature validated in the Attestation Service}
        :param quote: either a quote(base64 or bytes), or a full report(json) to be verified with intel.
        :type quote: str / bytes
        :param response_report: a json response from the Enigma node.
        :type response_report: dict
        """
        if quote is not None:
            try:
                quote_bytes = base64.b64decode(quote)
            except binascii.Error:
                quote_bytes = quote

            if len(quote_bytes) == 432:
                print(quote_bytes.hex())
                self._build_quote(quote_bytes)
            else:
                raise RuntimeError

        else:
            if self.verify_report(response_report):
                response_report['report'] = json.loads(
                    response_report['report'])
                data = base64.b64decode(
                    response_report['report']['isvEnclaveQuoteBody'])
                self._build_quote(data)
                object.__setattr__(self, 'report', response_report['report'])
                object.__setattr__(self, 'sig', response_report['signature'])
                object.__setattr__(self, 'cert',
                                   response_report['certificate'])

    def _build_quote(self, quote_bytes):
        object.__setattr__(self, 'quote_bytes', quote_bytes)
        object.__setattr__(self, 'body', _Body(quote_bytes))
        object.__setattr__(self, 'report_body', _ReportBody(quote_bytes))
        object.__setattr__(self, 'signature_len', quote_bytes[432:436])
        object.__setattr__(self, 'signature', quote_bytes[436:])

    @classmethod
    def from_enigma_proxy(cls, encrypted_quote,
                          server='http://127.0.0.1:5000/api'):
        body = {
            'jsonrpc': '2.0',
            'method': 'validate',
            'params': {
                'quote': encrypted_quote
            },
            'id': '1'
        }
        try:
            response = requests.post(server, json=body)
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Couldn't connect to the server: ", server)
        if response.status_code != 200:
            raise ValueError("Couldn't verify the quote, HTTP code: ",
                             response.status_code)

        result = response.json()['result']
        if result['validate'] != 'True':
            raise ValueError("The server failed to verify Intel's signature")

        if not cls.verify_report(result):
            raise ValueError("Failed self verifying Intel's signature")
        return cls(response_report=result)

    @classmethod
    def verify_report(cls, response_report):
        report_cert = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM,
            response_report['certificate'].encode('ascii'))
        ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                                  response_report['ca'])
        trusted_store = OpenSSL.crypto.X509Store()
        trusted_store.add_cert(ca_cert)
        store_context = OpenSSL.crypto.X509StoreContext(trusted_store,
                                                        report_cert)
        try:
            store_context.verify_certificate()
        except OpenSSL.crypto.X509StoreContextError:
            return False
        # Check if signature is bytes or hex(hex from the enigma server)
        try:
            sig = binascii.unhexlify(response_report['signature'])
        except binascii.Error:
            if len(response_report['signature']) == 256:
                sig = response_report['signature']
            else:
                raise ValueError("The Signature is invalid: ",
                                 response_report['signature'])
        try:
            OpenSSL.crypto.verify(report_cert, sig,
                                  response_report['report'],
                                  'sha256')
        except OpenSSL.crypto.Error:
            return False
        return True

    def serialize(self):
        report = json.dumps(self.report, separators=(',', ':'))
        sig = bytes.fromhex(self.sig)
        cert = self.cert
        return report, sig, cert

    def __setattr__(self, key, value):
        raise ImmutableException(
            'This object is immutable, the attributes cannot be changed')


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
        raise ImmutableException(
            'This object is immutable, the attributes cannot be changed')


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
        raise ImmutableException(
            'This object is immutable, the attributes cannot be changed')


class ImmutableException(Exception):
    pass
