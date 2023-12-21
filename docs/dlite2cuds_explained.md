Explanation of the implementation of the DLite to CUDS conversion
===================================================================

Remark: This description correspond to the version December 2023 of the cuds2dlite.py

## Assumptions

### Case 1: Only DataProperty

The main assumption is that the DLite properties correspond to CUDS data properties and that there is no relation ($ref) included in the data model.
The possible semantic description of the properties is lost in the conversion (unless specifically added in the list of relations to transfer) as well as the unit.

### Case 2: Properties defined as class

The main assumption is that each of the instance properties are associated to class that are represented in the cuds ontology and so the properties are represented by object properties.
It corresponds to the expectation of DLite properties and offers a more semantic conversion but does not cover properly the properties like range used in some CMCL examples.

### Unicity of uuid

As explain below, the code is reusing the uuid from CUDS for the DLite instance.
We assume that there is no previously existing instance with that uuid.

## Case 1

### Initialization

The CUDS instance is created directly with the values.
The initialization of the values not specified in the dictionary of properties is according to Simphony rule: ?? 

### Mapping

In case 1, the data is contained in DataProperty therefore the mapping is between a DLite property and a DataProperty.

### Value transfer

The CUDS instance is created with the iri equal to the namespace + uuid from the DLite instance.
It allows to keep data consistent when converting back and forth between DLite and CUDS representation. But it does not imply synchronization.

The CUDS instance is created also from a dictionary of properties.
The dictionary of properties is build from the values of the properties mapped to the cuds class attributes (data properties).

The values that are not mapped are ignored.
The unit information is lost.
Matching type test or conversion is not implemented.

### Relation transfer

The relations connecting the current cuds instance is subject of is copied as a triple of string into a collection of relations.

The stored relations are recovered using cuds_instance.relationships_iter which return all the relations ?? 

### Entity creation

The creation of the entity is based on the same principle with the extraction of the list of data properties.
The label is taken from the data poperty label (skos:prefLabel).
The type is fetch from the data property description.
The unit and description are empty as it is usually not defined (according to the available examples).

