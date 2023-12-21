Explanation of the implementation of the DLite to CUDS conversion
===================================================================

Remark: This description correspond to the version December 2023 of the cuds2dlite.py

## Assumptions

### Case 1: Only DataProperty

The main assumption is that the DLite properties correspond to CUDS data properties and that there is no relation ($ref) included in the data model.
The possible semantic description as class of the properties is lost in the conversion (unless specifically added in the list of relations to transfer) as well as the unit and description.

### Case 2: Properties defined as class

The main assumption is that each of the instance properties are associated to class that are represented in the cuds ontology and so the properties are represented by object properties.
It corresponds to the expectation of DLite properties and offers a more semantic conversion but does not cover properly the properties like range used in some CMCL examples.

### Unicity of uuid

As explain below, the code is reusing the uuid from CUDS for the DLite instance.
We assume that there is no previously existing instance with that uuid.

## Case 1

### Initialization

The CUDS instance is created directly with the values.
The initialization of the values not specified in the dictionary of properties is according to Simphony rule: it will fail if not all attributes are provided.

The cuds class needs to be defined in the ontology.

### Mapping

In case 1, the data is contained in DataProperty therefore the mapping is between a DLite property and a DataProperty.
The entity needs also to be mapped to a cuds class.

### Value transfer

The CUDS instance is created with the iri equal to the namespace + uuid from the DLite instance.
It allows to keep data consistent when converting back and forth between DLite and CUDS representation. But it does not imply synchronization.

The CUDS instance is created also from a dictionary of properties.
The dictionary of properties is build from the values of the properties mapped to the cuds class attributes (data properties).

The values that are not mapped are ignored but do not lead to failure as the mapped property is not part of the attribute of the cuds class.
The unit information and description are lost.
Matching type test or conversion is not implemented.

### Relation transfer

After the creation of the cuds instance, the relations stored in the associated collection are processed.
All relations outside ["_is-a", "_has-meta", "_has-uuid"] are tentatively added.

The procedure checks that both the subject and object are part of the cuds (https://www.simphony-osp.eu/entity#<uuid>). If not part, the relation is ignored.

This approach imposes that relations are treated at the end so that the instances newly created are found.
