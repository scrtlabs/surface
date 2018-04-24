import os

basepath = os.path.dirname(__file__)

# Test config
TEST_URL = 'http://localhost:9545'
CONTRACT_PATH = os.path.join(
    basepath, '..', '..', 'coin-mixer-poc', 'dapp', 'build', 'contracts',
    'Enigma.json'
)
ACCOUNTS = [
    '0x627306090abab3a6e1400e9345bc60c78a8bef57'
]
KEYS = [
    'c87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3'
]
PASSPHRASE = 'candy maple cake sugar pudding cream honey rich smooth crumble sweet treat'
