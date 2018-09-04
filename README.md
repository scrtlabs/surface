# surface
Surface is part of the Enigma node software stack. The Surface component is responsible for operations that are outside of SGX and acting as a bridge between the outside world and the "Core" component.

## Getting Started

Surface is a component of the Enigma network. To run surface, refer to the deployment instructions for the [Enigma Docker Network](https://github.com/enigmampc/enigma-docker-network).

## Running in simulation mode 
Simply pass the flag: 

```
--simulation
```

## Running the tests

This project depends on the Enigma smart contract. To run the tests, the 
[Enigma smart contract](https://github.com/enigmampc/enigma-contract) must be deployed, and the configuration in he ``src/config.py`` file needs to match your environment (accounts and passphrase from truffle).

Create a python virtual environment.
```
cd ..
cd surface
virtualenv --python=/usr/local/Cellar/python3/3.6.4_2/bin/python3 python3
source python3/bin/activate
pip install -r etc/requirements.txt
```

To run all tests:

```
cd src/tests
pytest
```

## Deployment

Refer to the documentation of the [Enigma Docker Network](https://github.com/enigmampc/enigma-docker-network).

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
