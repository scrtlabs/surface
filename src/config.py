import os

basepath = os.path.dirname(__file__)

# Test config
PROVIDER_URL = 'http://localhost:9545'
CONTRACT_PATH = os.path.join(
    basepath, '..', '..', 'coin-mixer-poc', 'dapp', 'build', 'contracts',
    'Enigma.json'
)
