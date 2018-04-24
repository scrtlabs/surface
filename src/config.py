import os

basepath = os.path.dirname(__file__)

# Test config
TEST_URL = 'http://localhost:9545'
CONTRACT_PATH = os.path.join(
    basepath, '..', 'coin-mixer-poc', 'dapp', 'build', 'contracts',
    'Enigma.json'
)
ACCOUNTS = [
    '0x627306090abab3a6e1400e9345bc60c78a8bef57'
]
PASSPHRASE = 'candy maple cake sugar pudding cream honey rich smooth crumble sweet treat'
