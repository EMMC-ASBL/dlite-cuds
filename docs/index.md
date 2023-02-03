# DLite2CUDS

## Restrictions on the input CUDS when converting to DLite DataModel

The implementations has some severe restrictions for now:

* An individual can only be an rdf:type of one class (i.e. it cannot be for instance both an rdf:type :Human and rdf:type Mother)

* All individuals of the same type must have the exact same properties defined.

Restrictions on Dlite Models etc:

* Three things are needed: Entity of interest (e.g. the DataModel), collection with data, collection with mappings.

* Not only properties must be mapped, but also the concepts/entities themselves.

* Only single value data are supported (dimensionality in Dlite DataModel not yet implemented)


An OTEAPI Plugin with OTE strategies.

Further reading:

- [OTEAPI Core Documentation](https://emmc-asbl.github.io/oteapi-core)
- [OTEAPI Services Documentation](https://emmc-asbl.github.io/oteapi-services)

## Test the plugin

There are two ways of testing this plugin: unit testing or end-to-end testing.

### Unit tests

To run the unit tests, checking that all the Python code functionality works as intended, one needs to first install the development requirements:

```shell
cd /path/to/dlite-cuds
pip install -U -e .[dev]
```

Then one can run the tests through the [pytest](https://pytest.org) framework:

```shell
pytest
```

### End-to-end testing

Here, end-to-end means using [OTElib](https://github.com/EMMC-ASBL/otelib) to initialize an OTEClient pointing at a running REST API service, similar to the one created by [OTEAPI Services](https://github.com/EMMC-ASBL/oteapi-services), and setting up a pipeline that utilizes the strategies from this plugin.

In order to test this locally, one requires [Docker Compose](https://github.com/docker/compose).
Then, one can setup a local REST API service that includes this plugin and test it with the following commands:

```shell
docker-compose -f docker-compose.yml pull  # Download the latest container images
docker-compose -f docker-compose.yml up  # Run the services
```

This will start the service and take over the terminal, printing log messages from all the services started through the [`docker-compose.yml`](https://github.com/EMMC-ASBL/dlite-cuds/blob/main/docker-compose.yml) file.
If one instead wishes to keep that terminal available, or only show the logs relevant for the `oteapi` service, one can do:

```shell
docker-compose -f docker-compose.yml up -d  # Run the services detached

# Show logs and give back terminal
docker logs dlite-cuds-oteapi-1

# Show logs and follow them live
docker logs -f dlite-cuds-oteapi-1
```

Now, one can instantiate an `otelib.OTEClient` with `"http://localhost:8080"` (or using the `PORT` environment variable value instead of `8080` if it has been set) and test the strategies by supplying the correct configuration values.

Note, remember to update [`setup.cfg`](https://github.com/EMMC-ASBL/dlite-cuds/blob/main/setup.cfg) to list the plugin strategies - otherwise they will not be findable by the OTEAPI service.

## License and copyright

DLite2CUDS is released under the [MIT license](LICENSE.md) with copyright &copy; SINTEF.

## Acknowledgment

DLite2CUDS has been created via the [cookiecutter](https://cookiecutter.readthedocs.io/) [template for OTEAPI plugins](https://github.com/EMMC-ASBL/oteapi-plugin-template).

DLite2CUDS has been supported by the following projects:

- **OntoTrans** (2020-2024) that receives funding from the European Union’s Horizon 2020 Research and Innovation Programme, under Grant Agreement n. 862136.

- **VIPCOAT** (2021-2025) receives funding from the European Union’s Horizon 2020 Research and Innovation Programme - DT-NMBP-11-2020 Open Innovation Platform for Materials Modelling, under Grant Agreement no: 952903.

- **OpenModel** (2021-2025) receives funding from the European Union’s Horizon 2020 Research and Innovation Programme - DT-NMBP-11-2020 Open Innovation Platform for Materials Modelling, under Grant Agreement no: 953167.
