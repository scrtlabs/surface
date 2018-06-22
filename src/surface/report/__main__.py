import requests
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import urllib.parse
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import cryptography
import OpenSSL
import pickle


examplegid = '00000bcd'
ourgid = '00000aca'

url = 'https://test-as.sgx.trustedservices.intel.com:443/attestation/sgx/v2'
myssl = ('sgx/client.crt', 'sgx/client.key')

PICKLED_RESPONSE = b'\x80\x03crequests.models\nResponse\nq\x00)\x81q\x01}q\x02(X\x08\x00\x00\x00_contentq\x03B\xcf\x02\x00\x00{"id":"306286860802364519834752506973858673005","timestamp":"2018-06-12T17:10:19.129261","isvEnclaveQuoteStatus":"OK","isvEnclaveQuoteBody":"AgAAANoKAAAHAAYAAAAAABYB+Vw5ueowf+qruQGtw+72HPtcKCz63mlimVbjqbE5BAT/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAKXBP5WZBuLjmngKZ8zzQ2A00leTJBcp9oYT2CDXSNHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD1xnnferKFHD2uvYqTXdDA8iZ22kCD5xw7h38CMfOngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8G0ljp2XaOXVtOPvA5tngv93F4PXnPFqA6ZnYt5BGhhPYTqeilJHAoMpungy+sJPzQDOLm3hiqQ34tUBCfn2p"}q\x04X\x0b\x00\x00\x00status_codeq\x05K\xc8X\x07\x00\x00\x00headersq\x06crequests.structures\nCaseInsensitiveDict\nq\x07)\x81q\x08}q\tX\x06\x00\x00\x00_storeq\nccollections\nOrderedDict\nq\x0b)Rq\x0c(X\n\x00\x00\x00request-idq\rX\n\x00\x00\x00request-idq\x0eX \x00\x00\x00ac42a04936e34c00ae78c223b68b1530q\x0f\x86q\x10X\x04\x00\x00\x00dateq\x11X\x04\x00\x00\x00dateq\x12X\x1d\x00\x00\x00Tue, 12 Jun 2018 17:10:19 GMTq\x13\x86q\x14X\x0c\x00\x00\x00content-typeq\x15X\x0c\x00\x00\x00content-typeq\x16X\x10\x00\x00\x00application/jsonq\x17\x86q\x18X\x0e\x00\x00\x00content-lengthq\x19X\x0e\x00\x00\x00content-lengthq\x1aX\x03\x00\x00\x00719q\x1b\x86q\x1cX\x15\x00\x00\x00x-iasreport-signatureq\x1dX\x15\x00\x00\x00x-iasreport-signatureq\x1eXX\x01\x00\x00NoqbsZG1VSxTmA82JpsFrxJ6zUxSKm6a90U0uBwdfZCXtFcDYDtnE57Ix31MXt7YZwCrlH6eQpsYyAFpwovggga1UCi4wiunOvqu0TNOeOlsDBxpCFZHDlCapGY0p16XasXX/wa6CfmH5nAgwsJFugnZvrhzrnsZvOSf5jHm14LzoB4C75XvfcMvE75N5Lm2lY4bWnY0nixSKgFThZqCb/E1TxKzeh+kK3rAPuZOCYdFOzp0u6tl1UCTgBuna+SLoW5/6Dn8iiGb/9qprRXCOgUutsmoEQIYMCLB+Y/mYfUVS8YKDqaEL7ZMyyQDIKuck/mYbkyiSiuFmzBeGNwrmQ==q\x1f\x86q X\x1f\x00\x00\x00x-iasreport-signing-certificateq!X\x1f\x00\x00\x00x-iasreport-signing-certificateq"X\xb6\x0e\x00\x00-----BEGIN%20CERTIFICATE-----%0AMIIEoTCCAwmgAwIBAgIJANEHdl0yo7CWMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV%0ABAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV%0ABAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0%0AYXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwHhcNMTYxMTIyMDkzNjU4WhcNMjYxMTIw%0AMDkzNjU4WjB7MQswCQYDVQQGEwJVUzELMAkGA1UECAwCQ0ExFDASBgNVBAcMC1Nh%0AbnRhIENsYXJhMRowGAYDVQQKDBFJbnRlbCBDb3Jwb3JhdGlvbjEtMCsGA1UEAwwk%0ASW50ZWwgU0dYIEF0dGVzdGF0aW9uIFJlcG9ydCBTaWduaW5nMIIBIjANBgkqhkiG%0A9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqXot4OZuphR8nudFrAFiaGxxkgma/Es/BA%2Bt%0AbeCTUR106AL1ENcWA4FX3K%2BE9BBL0/7X5rj5nIgX/R/1ubhkKWw9gfqPG3KeAtId%0Acv/uTO1yXv50vqaPvE1CRChvzdS/ZEBqQ5oVvLTPZ3VEicQjlytKgN9cLnxbwtuv%0ALUK7eyRPfJW/ksddOzP8VBBniolYnRCD2jrMRZ8nBM2ZWYwnXnwYeOAHV%2BW9tOhA%0AImwRwKF/95yAsVwd21ryHMJBcGH70qLagZ7Ttyt%2B%2BqO/6%2BKAXJuKwZqjRlEtSEz8%0AgZQeFfVYgcwSfo96oSMAzVr7V0L6HSDLRnpb6xxmbPdqNol4tQIDAQABo4GkMIGh%0AMB8GA1UdIwQYMBaAFHhDe3amfrzQr35CN%2Bs1fDuHAVE8MA4GA1UdDwEB/wQEAwIG%0AwDAMBgNVHRMBAf8EAjAAMGAGA1UdHwRZMFcwVaBToFGGT2h0dHA6Ly90cnVzdGVk%0Ac2VydmljZXMuaW50ZWwuY29tL2NvbnRlbnQvQ1JML1NHWC9BdHRlc3RhdGlvblJl%0AcG9ydFNpZ25pbmdDQS5jcmwwDQYJKoZIhvcNAQELBQADggGBAGcIthtcK9IVRz4r%0ARq%2BZKE%2B7k50/OxUsmW8aavOzKb0iCx07YQ9rzi5nU73tME2yGRLzhSViFs/LpFa9%0AlpQL6JL1aQwmDR74TxYGBAIi5f4I5TJoCCEqRHz91kpG6Uvyn2tLmnIdJbPE4vYv%0AWLrtXXfFBSSPD4Afn7%2B3/XUggAlc7oCTizOfbbtOFlYA4g5KcYgS1J2ZAeMQqbUd%0AZseZCcaZZZn65tdqee8UXZlDvx0%2BNdO0LR%2B5pFy%2BjuM0wWbu59MvzcmTXbjsi7HY%0A6zd53Yq5K244fwFHRQ8eOB0IWB%2B4PfM7FeAApZvlfqlKOlLcZL2uyVmzRkyR5yW7%0A2uo9mehX44CiPJ2fse9Y6eQtcfEhMPkmHXI01sN%2BKwPbpA39%2BxOsStjhP9N1Y1a2%0AtQAVo%2ByVgLgV2Hws73Fc0o3wC78qPEA%2Bv2aRs/Be3ZFDgDyghc/1fgU%2B7C%2BP6kbq%0Ad4poyb6IW8KCJbxfMJvkordNOgOUUxndPHEi/tb/U7uLjLOgPA%3D%3D%0A-----END%20CERTIFICATE-----%0A-----BEGIN%20CERTIFICATE-----%0AMIIFSzCCA7OgAwIBAgIJANEHdl0yo7CUMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV%0ABAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV%0ABAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0%0AYXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwIBcNMTYxMTE0MTUzNzMxWhgPMjA0OTEy%0AMzEyMzU5NTlaMH4xCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwL%0AU2FudGEgQ2xhcmExGjAYBgNVBAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQD%0ADCdJbnRlbCBTR1ggQXR0ZXN0YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwggGiMA0G%0ACSqGSIb3DQEBAQUAA4IBjwAwggGKAoIBgQCfPGR%2BtXc8u1EtJzLA10Feu1Wg%2Bp7e%0ALmSRmeaCHbkQ1TF3Nwl3RmpqXkeGzNLd69QUnWovYyVSndEMyYc3sHecGgfinEeh%0ArgBJSEdsSJ9FpaFdesjsxqzGRa20PYdnnfWcCTvFoulpbFR4VBuXnnVLVzkUvlXT%0AL/TAnd8nIZk0zZkFJ7P5LtePvykkar7LcSQO85wtcQe0R1Raf/sQ6wYKaKmFgCGe%0ANpEJUmg4ktal4qgIAxk%2BQHUxQE42sxViN5mqglB0QJdUot/o9a/V/mMeH8KvOAiQ%0AbyinkNndn%2BBgk5sSV5DFgF0DffVqmVMblt5p3jPtImzBIH0QQrXJq39AT8cRwP5H%0AafuVeLHcDsRp6hol4P%2BZFIhu8mmbI1u0hH3W/0C2BuYXB5PC%2B5izFFh/nP0lc2Lf%0A6rELO9LZdnOhpL1ExFOq9H/B8tPQ84T3Sgb4nAifDabNt/zu6MmCGo5U8lwEFtGM%0ARoOaX4AS%2B909x00lYnmtwsDVWv9vBiJCXRsCAwEAAaOByTCBxjBgBgNVHR8EWTBX%0AMFWgU6BRhk9odHRwOi8vdHJ1c3RlZHNlcnZpY2VzLmludGVsLmNvbS9jb250ZW50%0AL0NSTC9TR1gvQXR0ZXN0YXRpb25SZXBvcnRTaWduaW5nQ0EuY3JsMB0GA1UdDgQW%0ABBR4Q3t2pn680K9%2BQjfrNXw7hwFRPDAfBgNVHSMEGDAWgBR4Q3t2pn680K9%2BQjfr%0ANXw7hwFRPDAOBgNVHQ8BAf8EBAMCAQYwEgYDVR0TAQH/BAgwBgEB/wIBADANBgkq%0AhkiG9w0BAQsFAAOCAYEAeF8tYMXICvQqeXYQITkV2oLJsp6J4JAqJabHWxYJHGir%0AIEqucRiJSSx%2BHjIJEUVaj8E0QjEud6Y5lNmXlcjqRXaCPOqK0eGRz6hi%2BripMtPZ%0AsFNaBwLQVV905SDjAzDzNIDnrcnXyB4gcDFCvwDFKKgLRjOB/WAqgscDUoGq5ZVi%0AzLUzTqiQPmULAQaB9c6Oti6snEFJiCQ67JLyW/E83/frzCmO5Ru6WjU4tmsmy8Ra%0AUd4APK0wZTGtfPXU7w%2BIBdG5Ez0kE1qzxGQaL4gINJ1zMyleDnbuS8UicjJijvqA%0A152Sq049ESDz%2B1rRGc2NVEqh1KaGXmtXvqxXcTB%2BLjy5Bw2ke0v8iGngFBPqCTVB%0A3op5KBG3RjbF6RRSzwzuWfL7QErNC8WEy5yDVARzTA5%2BxmBc388v9Dm21HGfcC8O%0ADD%2BgT9sSpssq0ascmvH49MOgjt1yoysLtdCtJW/9FZpoOypaHx0R%2BmJTLwPXVMrv%0ADaVzWh5aiEx%2BidkSGMnX%0A-----END%20CERTIFICATE-----%0Aq#\x86q$X\n\x00\x00\x00connectionq%X\n\x00\x00\x00Connectionq&X\n\x00\x00\x00keep-aliveq\'\x86q(usbX\x03\x00\x00\x00urlq)XK\x00\x00\x00https://test-as.sgx.trustedservices.intel.com:443/attestation/sgx/v2/reportq*X\x07\x00\x00\x00historyq+]q,X\x08\x00\x00\x00encodingq-NX\x06\x00\x00\x00reasonq.X\x02\x00\x00\x00OKq/X\x07\x00\x00\x00cookiesq0crequests.cookies\nRequestsCookieJar\nq1)\x81q2}q3(X\x07\x00\x00\x00_policyq4chttp.cookiejar\nDefaultCookiePolicy\nq5)\x81q6}q7(X\x08\x00\x00\x00netscapeq8\x88X\x07\x00\x00\x00rfc2965q9\x89X\x13\x00\x00\x00rfc2109_as_netscapeq:NX\x0c\x00\x00\x00hide_cookie2q;\x89X\r\x00\x00\x00strict_domainq<\x89X\x1b\x00\x00\x00strict_rfc2965_unverifiableq=\x88X\x16\x00\x00\x00strict_ns_unverifiableq>\x89X\x10\x00\x00\x00strict_ns_domainq?K\x00X\x1c\x00\x00\x00strict_ns_set_initial_dollarq@\x89X\x12\x00\x00\x00strict_ns_set_pathqA\x89X\x10\x00\x00\x00_blocked_domainsqB)X\x10\x00\x00\x00_allowed_domainsqCNX\x04\x00\x00\x00_nowqDJ{\xfe\x1f[ubX\x08\x00\x00\x00_cookiesqE}qFhDJ{\xfe\x1f[ubX\x07\x00\x00\x00elapsedqGcdatetime\ntimedelta\nqHK\x00K\x01Jf\xb5\x06\x00\x87qIRqJX\x07\x00\x00\x00requestqKcrequests.models\nPreparedRequest\nqL)\x81qM}qN(X\x06\x00\x00\x00methodqOX\x04\x00\x00\x00POSTqPh)h*h\x06h\x07)\x81qQ}qRh\nh\x0b)RqS(X\n\x00\x00\x00user-agentqTX\n\x00\x00\x00User-AgentqUX\x16\x00\x00\x00python-requests/2.18.4qV\x86qWX\x0f\x00\x00\x00accept-encodingqXX\x0f\x00\x00\x00Accept-EncodingqYX\r\x00\x00\x00gzip, deflateqZ\x86q[X\x06\x00\x00\x00acceptq\\X\x06\x00\x00\x00Acceptq]X\x03\x00\x00\x00*/*q^\x86q_X\n\x00\x00\x00connectionq`X\n\x00\x00\x00ConnectionqaX\n\x00\x00\x00keep-aliveqb\x86qcX\x0e\x00\x00\x00content-lengthqdX\x0e\x00\x00\x00Content-LengthqeX\x04\x00\x00\x001511qf\x86qgX\x0c\x00\x00\x00content-typeqhX\x0c\x00\x00\x00Content-TypeqiX\x10\x00\x00\x00application/jsonqj\x86qkusbhEh1)\x81ql}qm(h4h5)\x81qn}qo(h8\x88h9\x89h:Nh;\x89h<\x89h=\x88h>\x89h?K\x00h@\x89hA\x89hB)hCNhDJy\xfe\x1f[ubhE}qphDJy\xfe\x1f[ubX\x04\x00\x00\x00bodyqqB\xe7\x05\x00\x00{"isvEnclaveQuote": "AgAAANoKAAAHAAYAAAAAABYB+Vw5ueowf+qruQGtw+72HPtcKCz63mlimVbjqbE5BAT/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAKXBP5WZBuLjmngKZ8zzQ2A00leTJBcp9oYT2CDXSNHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD1xnnferKFHD2uvYqTXdDA8iZ22kCD5xw7h38CMfOngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8G0ljp2XaOXVtOPvA5tngv93F4PXnPFqA6ZnYt5BGhhPYTqeilJHAoMpungy+sJPzQDOLm3hiqQ34tUBCfn2pqAIAACCRKNGZN2ZUUY22tjhHxxgvFYiPPDCVBxYk5IWlV+4PpTvDYca8SfCiYD4Kua3A2it1Hiq3hdPtctCfKWda/wAX8S59cqYFxIoqnJnS/hMcYfFV3vAUoHgnZIYCkA/T7bAYbjTIRlyO3lmeOU09nx0s2koakT5HevmacWOUeJj+ZEbkPbR766mqULdS4FTC3ZwWZeu13ia2/0oPnUzAraNP7DJMIVOyy+ge5G9N1W7FkZu1jVuBQOLcypZEhr951lbHdEYoYeoL3uXLGquC5pS8c8MJ86CZIFjStUcw0iE/N8QZBd9JJ5rEAcxlbfySoSGQEJeeVtPOj4GavFyR7DytVyBzqlEUZ8g5JsUW84nOqZ7ZlGZckNtZ5HZoFkI0mSO74+e57UHg1TG76GgBAABklbQGvktq8pI3wZC38hw6TVjH+yqwgi3YGw5dUSMo/NBHMcK/uPraR/0ipsA0WLgoRyGVTdDmUJagCqYbrgBtwm8Tz84ul4FXMb/JKG2O+djr9DTcRuIWRqFqWbRVQKvgGwdkGXDDYGmPpRWGqYXmAFNTUQgp5m/ZDdryjGTboIiQt/J6/4aNNZki98EgpHjmLXKwj4hCZSlbQbVz78w4XP9Faj3JEBTLz15w/jLy+UkAjHu3yn6B9za4/ypdDeY1Kv4MfN+/zIOLXRwr7ta7XYhBF4r0lxvwfXaPo7rkV/letzO4R97FrQvlPfqBgrlxdhLkwIbJNXl5CWPGpKQDTFva/+MQjK3EgdHqkbODO7WSy0P48L7gUGRv9ZjwkcpW41PeEQmt7neJYrtDd2BeY2TFnDDTnx+VP7Mg2iBZPrBiSj0WcjK9bltPm7VeHNTyw2g8q5PVxV1jDZlLS2vmCo/tL08h3vcNShrfzHm32r4JXAXERxeC"}qrX\x05\x00\x00\x00hooksqs}qtX\x08\x00\x00\x00responsequ]qvsX\x0e\x00\x00\x00_body_positionqwNubub.'

QOUTE = "AgAAANoKAAAHAAYAAAAAABYB+Vw5ueowf+qruQGtw+72HPtcKCz63mlimVbjqbE5BAT/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAKXBP5WZBuLjmngKZ8zzQ2A00leTJBcp9oYT2CDXSNHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD1xnnferKFHD2uvYqTXdDA8iZ22kCD5xw7h38CMfOngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8G0ljp2XaOXVtOPvA5tngv93F4PXnPFqA6ZnYt5BGhhPYTqeilJHAoMpungy+sJPzQDOLm3hiqQ34tUBCfn2pqAIAACCRKNGZN2ZUUY22tjhHxxgvFYiPPDCVBxYk5IWlV+4PpTvDYca8SfCiYD4Kua3A2it1Hiq3hdPtctCfKWda/wAX8S59cqYFxIoqnJnS/hMcYfFV3vAUoHgnZIYCkA/T7bAYbjTIRlyO3lmeOU09nx0s2koakT5HevmacWOUeJj+ZEbkPbR766mqULdS4FTC3ZwWZeu13ia2/0oPnUzAraNP7DJMIVOyy+ge5G9N1W7FkZu1jVuBQOLcypZEhr951lbHdEYoYeoL3uXLGquC5pS8c8MJ86CZIFjStUcw0iE/N8QZBd9JJ5rEAcxlbfySoSGQEJeeVtPOj4GavFyR7DytVyBzqlEUZ8g5JsUW84nOqZ7ZlGZckNtZ5HZoFkI0mSO74+e57UHg1TG76GgBAABklbQGvktq8pI3wZC38hw6TVjH+yqwgi3YGw5dUSMo/NBHMcK/uPraR/0ipsA0WLgoRyGVTdDmUJagCqYbrgBtwm8Tz84ul4FXMb/JKG2O+djr9DTcRuIWRqFqWbRVQKvgGwdkGXDDYGmPpRWGqYXmAFNTUQgp5m/ZDdryjGTboIiQt/J6/4aNNZki98EgpHjmLXKwj4hCZSlbQbVz78w4XP9Faj3JEBTLz15w/jLy+UkAjHu3yn6B9za4/ypdDeY1Kv4MfN+/zIOLXRwr7ta7XYhBF4r0lxvwfXaPo7rkV/letzO4R97FrQvlPfqBgrlxdhLkwIbJNXl5CWPGpKQDTFva/+MQjK3EgdHqkbODO7WSy0P48L7gUGRv9ZjwkcpW41PeEQmt7neJYrtDd2BeY2TFnDDTnx+VP7Mg2iBZPrBiSj0WcjK9bltPm7VeHNTyw2g8q5PVxV1jDZlLS2vmCo/tL08h3vcNShrfzHm32r4JXAXERxeC"


def decode_response(res):
    # the report is the body of the response
    report = res.text.encode('utf-8')

    # Parse the signature from the header
    sig = res.headers['x-iasreport-signature']

    # Decode it from base64
    sig = base64.b64decode(sig)

    # Parse the certs from the header.
    intelcerts = urllib.parse.unquote(res.headers['x-iasreport-signing-certificate'])
    # split into a list of 2 chained certificates.
    intelcerts = intelcerts.split('-----END CERTIFICATE-----')
    # The first one is the one that signed the report
    report_cert = intelcerts[0] + '-----END CERTIFICATE-----'
    # The second one is the CA that signed the first certificate, and it's the one on Intel's website.
    report_ca = intelcerts[1] + '-----END CERTIFICATE-----'
    # Remove the "\n" at the start of the sig
    report_ca = report_ca[1:]
    return report, sig, report_cert, report_ca


def verify_certs(report, sig, report_cert, report_ca):

    # Load the report_cert into a x509 object
    x509cert = x509.load_pem_x509_certificate(report_cert.encode('ascii'), default_backend())
    # Verify that the signature is correct on the report and is really signed by this x509
    try:
        x509cert.public_key().verify(
            sig,
            report,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except cryptography.exceptions.InvalidSignature:
        return False

    # Loaded the report_cert into a different crypto library
    x509cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, report_cert.encode('ascii'))
    # Verify that it works here too.
    try:
        OpenSSL.crypto.verify(x509cert, sig, report, 'sha256')

    except OpenSSL.crypto.Error:
        return False

    # Load the publicly known cert from intel and remove the "\n" at the end
    with open("./AttestationReportSigningCACert.pem", "r") as myfile:
        ca_file = ''.join(myfile.readlines())[:-1]

    if ca_file != report_ca:
        return False

    return True

def serialize_report(report, sig, report_cert, report_ca):
    """
    Serialize the report for storage on the blockchain

    :param report:
    :param sig:
    :param report_cert:
    :param report_ca:
    :return:
    """
def main(pickle_res=None):
    # if pickle_res is None:
    #     body = {'isvEnclaveQuote': QUOTE}
    #     response = requests.post(url + '/report', json=body, cert=myssl)
    # else:
    #     response = pickle.loads(pickle_res)
    response = pickle.loads(pickle_res)
    if response.status_code == 400:
        exit()
    # Print the whole response - Doesn't work with pickle -> Look at the end of the file
    # data = dump.dump_all(response)
    # print(data.decode('utf-8'))

    report, sig, report_cert, report_ca = decode_response(response)

    if verify_certs(report, sig, report_cert, report_ca):
        print('YAY')
    else:
        print("NOO")


# main()

# This is for mocking, so you won't need the ceritificates and quote.
main(PICKLED_RESPONSE)

# this is an explanation of the variables used:
"""
        { 
        Report: *REPORT_JSON*,
        report_cert: *PEM string of the signing certificate*,
        ca_cert: *PEM string of the CA of the signing certificate*,
        sig: Signature of the whole Report made with the report_cert
        }
"""


# This is how a raw response looks like:
"""
< POST /attestation/sgx/v2/report HTTP/1.1
< Host: test-as.sgx.trustedservices.intel.com:443
< User-Agent: python-requests/2.18.4
< Accept-Encoding: gzip, deflate
< Accept: */*
< Connection: keep-alive
< Content-Length: 1511
< Content-Type: application/json
< 
< {"isvEnclaveQuote": "AgAAANoKAAAHAAYAAAAAABYB+Vw5ueowf+qruQGtw+72HPtcKCz63mlimVbjqbE5BAT/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAKXBP5WZBuLjmngKZ8zzQ2A00leTJBcp9oYT2CDXSNHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD1xnnferKFHD2uvYqTXdDA8iZ22kCD5xw7h38CMfOngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8G0ljp2XaOXVtOPvA5tngv93F4PXnPFqA6ZnYt5BGhhPYTqeilJHAoMpungy+sJPzQDOLm3hiqQ34tUBCfn2pqAIAACCRKNGZN2ZUUY22tjhHxxgvFYiPPDCVBxYk5IWlV+4PpTvDYca8SfCiYD4Kua3A2it1Hiq3hdPtctCfKWda/wAX8S59cqYFxIoqnJnS/hMcYfFV3vAUoHgnZIYCkA/T7bAYbjTIRlyO3lmeOU09nx0s2koakT5HevmacWOUeJj+ZEbkPbR766mqULdS4FTC3ZwWZeu13ia2/0oPnUzAraNP7DJMIVOyy+ge5G9N1W7FkZu1jVuBQOLcypZEhr951lbHdEYoYeoL3uXLGquC5pS8c8MJ86CZIFjStUcw0iE/N8QZBd9JJ5rEAcxlbfySoSGQEJeeVtPOj4GavFyR7DytVyBzqlEUZ8g5JsUW84nOqZ7ZlGZckNtZ5HZoFkI0mSO74+e57UHg1TG76GgBAABklbQGvktq8pI3wZC38hw6TVjH+yqwgi3YGw5dUSMo/NBHMcK/uPraR/0ipsA0WLgoRyGVTdDmUJagCqYbrgBtwm8Tz84ul4FXMb/JKG2O+djr9DTcRuIWRqFqWbRVQKvgGwdkGXDDYGmPpRWGqYXmAFNTUQgp5m/ZDdryjGTboIiQt/J6/4aNNZki98EgpHjmLXKwj4hCZSlbQbVz78w4XP9Faj3JEBTLz15w/jLy+UkAjHu3yn6B9za4/ypdDeY1Kv4MfN+/zIOLXRwr7ta7XYhBF4r0lxvwfXaPo7rkV/letzO4R97FrQvlPfqBgrlxdhLkwIbJNXl5CWPGpKQDTFva/+MQjK3EgdHqkbODO7WSy0P48L7gUGRv9ZjwkcpW41PeEQmt7neJYrtDd2BeY2TFnDDTnx+VP7Mg2iBZPrBiSj0WcjK9bltPm7VeHNTyw2g8q5PVxV1jDZlLS2vmCo/tL08h3vcNShrfzHm32r4JXAXERxeC"}
> HTTP/1.1 200 OK
> request-id: 13ac4876b790491d885d66e58e8af5a4
> date: Tue, 12 Jun 2018 16:27:25 GMT
> content-type: application/json
> content-length: 718
> x-iasreport-signature: YezIPuOaATzll1G9RK8OM9EdtNiufwJYOUi2TkUayrozyN4VInwKlmvOqZhTOcuABX0SYZOtuNH+11Nqn66KWj1wVnAbR2DOMwEYqCNlG3XbsveMmJ1ImwKKjn5ifflsOXMI3hBxEFy78gvBJ8ysJQgirRroCV7yAmE+YbbTvG6GiTflx4Gj4w2KdCPpZiaeiDYV9+bQBLo/kPH3Ui4LASdTypeUdcRJ0QnEpqz5vDjaH7mVrYEghY+5DWihqjlOJ45ajwdDwuVB1jJs0vrUWhRPVn9ycl3DV/qAHmpwSOylPzBFuZb9G9W3lPTgdgceoMsG0yLmShmrjjEH6PsmDQ==
> x-iasreport-signing-certificate: -----BEGIN%20CERTIFICATE-----%0AMIIEoTCCAwmgAwIBAgIJANEHdl0yo7CWMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV%0ABAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV%0ABAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0%0AYXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwHhcNMTYxMTIyMDkzNjU4WhcNMjYxMTIw%0AMDkzNjU4WjB7MQswCQYDVQQGEwJVUzELMAkGA1UECAwCQ0ExFDASBgNVBAcMC1Nh%0AbnRhIENsYXJhMRowGAYDVQQKDBFJbnRlbCBDb3Jwb3JhdGlvbjEtMCsGA1UEAwwk%0ASW50ZWwgU0dYIEF0dGVzdGF0aW9uIFJlcG9ydCBTaWduaW5nMIIBIjANBgkqhkiG%0A9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqXot4OZuphR8nudFrAFiaGxxkgma/Es/BA%2Bt%0AbeCTUR106AL1ENcWA4FX3K%2BE9BBL0/7X5rj5nIgX/R/1ubhkKWw9gfqPG3KeAtId%0Acv/uTO1yXv50vqaPvE1CRChvzdS/ZEBqQ5oVvLTPZ3VEicQjlytKgN9cLnxbwtuv%0ALUK7eyRPfJW/ksddOzP8VBBniolYnRCD2jrMRZ8nBM2ZWYwnXnwYeOAHV%2BW9tOhA%0AImwRwKF/95yAsVwd21ryHMJBcGH70qLagZ7Ttyt%2B%2BqO/6%2BKAXJuKwZqjRlEtSEz8%0AgZQeFfVYgcwSfo96oSMAzVr7V0L6HSDLRnpb6xxmbPdqNol4tQIDAQABo4GkMIGh%0AMB8GA1UdIwQYMBaAFHhDe3amfrzQr35CN%2Bs1fDuHAVE8MA4GA1UdDwEB/wQEAwIG%0AwDAMBgNVHRMBAf8EAjAAMGAGA1UdHwRZMFcwVaBToFGGT2h0dHA6Ly90cnVzdGVk%0Ac2VydmljZXMuaW50ZWwuY29tL2NvbnRlbnQvQ1JML1NHWC9BdHRlc3RhdGlvblJl%0AcG9ydFNpZ25pbmdDQS5jcmwwDQYJKoZIhvcNAQELBQADggGBAGcIthtcK9IVRz4r%0ARq%2BZKE%2B7k50/OxUsmW8aavOzKb0iCx07YQ9rzi5nU73tME2yGRLzhSViFs/LpFa9%0AlpQL6JL1aQwmDR74TxYGBAIi5f4I5TJoCCEqRHz91kpG6Uvyn2tLmnIdJbPE4vYv%0AWLrtXXfFBSSPD4Afn7%2B3/XUggAlc7oCTizOfbbtOFlYA4g5KcYgS1J2ZAeMQqbUd%0AZseZCcaZZZn65tdqee8UXZlDvx0%2BNdO0LR%2B5pFy%2BjuM0wWbu59MvzcmTXbjsi7HY%0A6zd53Yq5K244fwFHRQ8eOB0IWB%2B4PfM7FeAApZvlfqlKOlLcZL2uyVmzRkyR5yW7%0A2uo9mehX44CiPJ2fse9Y6eQtcfEhMPkmHXI01sN%2BKwPbpA39%2BxOsStjhP9N1Y1a2%0AtQAVo%2ByVgLgV2Hws73Fc0o3wC78qPEA%2Bv2aRs/Be3ZFDgDyghc/1fgU%2B7C%2BP6kbq%0Ad4poyb6IW8KCJbxfMJvkordNOgOUUxndPHEi/tb/U7uLjLOgPA%3D%3D%0A-----END%20CERTIFICATE-----%0A-----BEGIN%20CERTIFICATE-----%0AMIIFSzCCA7OgAwIBAgIJANEHdl0yo7CUMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV%0ABAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV%0ABAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0%0AYXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwIBcNMTYxMTE0MTUzNzMxWhgPMjA0OTEy%0AMzEyMzU5NTlaMH4xCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwL%0AU2FudGEgQ2xhcmExGjAYBgNVBAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQD%0ADCdJbnRlbCBTR1ggQXR0ZXN0YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwggGiMA0G%0ACSqGSIb3DQEBAQUAA4IBjwAwggGKAoIBgQCfPGR%2BtXc8u1EtJzLA10Feu1Wg%2Bp7e%0ALmSRmeaCHbkQ1TF3Nwl3RmpqXkeGzNLd69QUnWovYyVSndEMyYc3sHecGgfinEeh%0ArgBJSEdsSJ9FpaFdesjsxqzGRa20PYdnnfWcCTvFoulpbFR4VBuXnnVLVzkUvlXT%0AL/TAnd8nIZk0zZkFJ7P5LtePvykkar7LcSQO85wtcQe0R1Raf/sQ6wYKaKmFgCGe%0ANpEJUmg4ktal4qgIAxk%2BQHUxQE42sxViN5mqglB0QJdUot/o9a/V/mMeH8KvOAiQ%0AbyinkNndn%2BBgk5sSV5DFgF0DffVqmVMblt5p3jPtImzBIH0QQrXJq39AT8cRwP5H%0AafuVeLHcDsRp6hol4P%2BZFIhu8mmbI1u0hH3W/0C2BuYXB5PC%2B5izFFh/nP0lc2Lf%0A6rELO9LZdnOhpL1ExFOq9H/B8tPQ84T3Sgb4nAifDabNt/zu6MmCGo5U8lwEFtGM%0ARoOaX4AS%2B909x00lYnmtwsDVWv9vBiJCXRsCAwEAAaOByTCBxjBgBgNVHR8EWTBX%0AMFWgU6BRhk9odHRwOi8vdHJ1c3RlZHNlcnZpY2VzLmludGVsLmNvbS9jb250ZW50%0AL0NSTC9TR1gvQXR0ZXN0YXRpb25SZXBvcnRTaWduaW5nQ0EuY3JsMB0GA1UdDgQW%0ABBR4Q3t2pn680K9%2BQjfrNXw7hwFRPDAfBgNVHSMEGDAWgBR4Q3t2pn680K9%2BQjfr%0ANXw7hwFRPDAOBgNVHQ8BAf8EBAMCAQYwEgYDVR0TAQH/BAgwBgEB/wIBADANBgkq%0AhkiG9w0BAQsFAAOCAYEAeF8tYMXICvQqeXYQITkV2oLJsp6J4JAqJabHWxYJHGir%0AIEqucRiJSSx%2BHjIJEUVaj8E0QjEud6Y5lNmXlcjqRXaCPOqK0eGRz6hi%2BripMtPZ%0AsFNaBwLQVV905SDjAzDzNIDnrcnXyB4gcDFCvwDFKKgLRjOB/WAqgscDUoGq5ZVi%0AzLUzTqiQPmULAQaB9c6Oti6snEFJiCQ67JLyW/E83/frzCmO5Ru6WjU4tmsmy8Ra%0AUd4APK0wZTGtfPXU7w%2BIBdG5Ez0kE1qzxGQaL4gINJ1zMyleDnbuS8UicjJijvqA%0A152Sq049ESDz%2B1rRGc2NVEqh1KaGXmtXvqxXcTB%2BLjy5Bw2ke0v8iGngFBPqCTVB%0A3op5KBG3RjbF6RRSzwzuWfL7QErNC8WEy5yDVARzTA5%2BxmBc388v9Dm21HGfcC8O%0ADD%2BgT9sSpssq0ascmvH49MOgjt1yoysLtdCtJW/9FZpoOypaHx0R%2BmJTLwPXVMrv%0ADaVzWh5aiEx%2BidkSGMnX%0A-----END%20CERTIFICATE-----%0A
> Connection: keep-alive
> 
{"id":"17799798407803378780815025067996530252","timestamp":"2018-06-12T16:27:25.080278","isvEnclaveQuoteStatus":"OK","isvEnclaveQuoteBody":"AgAAANoKAAAHAAYAAAAAABYB+Vw5ueowf+qruQGtw+72HPtcKCz63mlimVbjqbE5BAT/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAKXBP5WZBuLjmngKZ8zzQ2A00leTJBcp9oYT2CDXSNHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD1xnnferKFHD2uvYqTXdDA8iZ22kCD5xw7h38CMfOngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8G0ljp2XaOXVtOPvA5tngv93F4PXnPFqA6ZnYt5BGhhPYTqeilJHAoMpungy+sJPzQDOLm3hiqQ34tUBCfn2p"}


"""