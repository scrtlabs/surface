import urllib.parse
import base64


def decode_response(res):
    # the report is the body of the response
    report = res.text.encode('utf-8')

    # Parse the signature from the header
    sig = res.headers['x-iasreport-signature']

    # Decode it from base64
    sig = base64.b64decode(sig)

    # Parse the certs from the header.
    intelcerts = urllib.parse.unquote(
        res.headers['x-iasreport-signing-certificate'])
    # split into a list of 2 chained certificates.
    intelcerts = intelcerts.split('-----END CERTIFICATE-----')
    # The first one is the one that signed the report
    report_cert = intelcerts[0] + '-----END CERTIFICATE-----'
    # The second one is the CA that signed the first certificate, and it's the one on Intel's website.
    # report_ca = intelcerts[1] + '-----END CERTIFICATE-----'
    # Remove the "\n" at the start of the sig
    # report_ca = report_ca[1:]
    return report, sig, report_cert
