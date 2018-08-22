# surface
Surface is part of the Enigma node software stack. The Surface component is responsible for operations that are outside of SGX and acting as a bridge between the outside world and the "Core" component.

## Getting Started


### Prerequisites

This project does things with the Enigma smart contract. To run the tests, the 
smart contract must be deployed. At the time of writing, the Enigma contract is
in the `coin-mixer-poc` project.

### Installing

1. Clone the `coin-mixer-poc` project in the same parent folder as the
 surface project.
    ```
    git clone git@github.com:enigmampc/surface.git 
    git clone git@github.com:enigmampc/coin-mixer-poc.git
    ```
    
2. Run the development console.
    ```
    sudo npm install -g truffle
    cd coin-mixer-poc/dapp
    truffle develop
    ```
    This should create a blockchain on port 9545. Please note the first account address and passphrase.

3. Inside truffle, compile and migrate the smart contracts.
    ```
    truffle> compile
    truffle> migrate
    truffle> test ./test/enigma-utils.js
    ```
    The last line in the console should say `8 passing`.  Do not exit the console, open another terminal window
    for the next commands.

4. Edit the `src/config.py` file to match your environment. Use the accounts and
    passphrase noted in step #2. 
    
5. Create a python virtual environment.
    ```
    cd ..
    cd surface
    virtualenv --python=/usr/local/Cellar/python3/3.6.4_2/bin/python3 python3
    source python3/bin/activate
    pip install -r etc/requirements.txt
    ```


## Running in simulation mode 
Simply pass the flag: 

```
--simulation
```
## Running the tests

To run all tests:

```
cd src/tests
pytest
```

## Deployment

TBD 

## Built With

TBD

## Contributing

TBD 

## Versioning

TBD 

## Authors

* **Enigma Team** - [enigma](https://enigma.co/)

## License

Surface is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a [copy](LICENSE) of the GNU Affero General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
