# [YARRRML](https://rml.io/yarrrml/)
## [YARRRML Parser](https://hub.docker.com/r/rmlio/yarrrml-parser)
    docker pull rmlio/yarrrml-parser

    docker run --rm -it -v $(pwd)/resources:/data rmlio/yarrrml-parser:latest -i /data/test.yarrr.yml -o mapping.ttl

## [RML Mapper](https://hub.docker.com/r/rmlio/rmlmapper-java)
    docker pull rmlio/rmlmapper-java

    docker run --rm -v $(pwd)/resources:/data rmlio/rmlmapper -m mapping.ttl -o out.rdf