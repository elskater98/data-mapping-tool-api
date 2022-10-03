# [YARRRML](https://rml.io/yarrrml/)
## [YARRRML Parser](https://hub.docker.com/r/rmlio/yarrrml-parser)
    docker pull rmlio/yarrrml-parser

    docker run --rm -it -v $(pwd)/:/data rmlio/yarrrml-parser:latest -i /data/input.yml -o /data/mapping.ttl

## [RML Mapper](https://hub.docker.com/r/rmlio/rmlmapper-java)
    docker pull rmlio/rmlmapper-java

    docker run --rm -v $(pwd)/:/data rmlio/rmlmapper-java  -m mapping.ttl -o /data/out.rdf

    java -jar rmlmapper-5.0.0-r362-all.jar -m mapping.ttl -o out.ttl