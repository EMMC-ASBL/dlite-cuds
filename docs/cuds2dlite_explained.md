Explanation of the implementation of the CUDS to DLite conversion
===================================================================

Remark: This description correspond to the version December 2023 of the cuds2dlite.py

## Assumptions

### Case 1: Only DataProperty

The main assumption is that the CUDS instances are made of only data properties and then related with each other.
The DLite instances build on that model have only properties with values, no reference to other instances.
The additional relations contained in the CUDS are grouped in a collection.

The data properties are not defined as class and do not follow the DLite schematic that impose a unit. The unit will then remain empty.

### Case 2: Properties defined as class

The main assumption is that each of the instances have properties defined as object property with reference to a class that has data properties: type, value, unit.
It corresponds to the expectation of DLite properties and offers a more semantic conversion but does not cover properly the properties like range used in some CMCL examples.

### Unicity of uuid

As explain below, the code is reusing the uuid from CUDS for the DLite instance.
We assume that there is no previously existing instance with that uuid.


## Case 1

### Initialization

The DLite instance is initialized with default values but the uuid is imposed and taken from the uuid of the CUDS instance. It allows to keep data consistent when converting back and forth between DLite and CUDS representation. But it does not imply synchronization.

The default initialization is potentially a problem in the case of an uncomplete CUDS.
Then some values of the DLite instance would not come from the CUDS.
A solution (not implemented) could be to set the equivalent of a NaN for all non specified value.

### Mapping

In case 1, the data is contained in DataProperty therefore the MapsTo relation is between a DLite property and a DataProperty.
There is also a MapsTo relation between the entity uri and the cuds class.

```
["http://onto-ns.com/meta/0.1/TypeOne#dpOne", "http://emmo.info/domain-mappings#mapsTo", "http://www.osp-core.com/ex#dpOne"]
```

### Value transfer

As there is no indication on the units, the value transfer is direct.
The DLite instance value is set as the DataProperty value.
The type is specified in the rdfs:range in the cuds ontology and could be checked prior to setting the value (not implemented).

All the data properties that are not mapped to the instance properties are lost.

### Relation transfer

The relations connecting the current cuds instance is subject of is copied as a triple of string into a collection of relations.

The stored relations are recovered using cuds_instance.relationships_iter which return all the relations where the subject is the cuds instance and the predictate is anything relating two cuds classes. 

### Entity creation

The creation of the entity is based on the same principle with the extraction of the list of data properties.
The label is taken from the data poperty label (not the skos:prefLabel defined in the ontology but the label taken from the IRI).
The type is fetch from the data property description.
The unit and description are empty as it is usually not defined (according to the available examples).

