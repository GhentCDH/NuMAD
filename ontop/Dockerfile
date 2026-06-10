FROM ontop/ontop:5.5.0

# Bake the ontop configuration (mappings, ontology, properties) into the image.
# The JDBC driver is intentionally left out and mounted at runtime.
COPY input/mapping.ttl /opt/ontop/input/mapping.ttl
COPY input/ontology.ttl /opt/ontop/input/ontology.ttl
COPY input/ontop.properties /opt/ontop/input/ontop.properties
