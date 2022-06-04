#!/usr/bin/env bash

echo "Create index patterns"
curl -XPOST 'http://localhost:5601/api/saved_objects/index-pattern/animals_idx' \
    -H 'kbn-xsrf: nevergonnagiveyouup' \
    -H 'Content-Type: application/json' \
    -d '{"attributes":{"title":"animals*","timeFieldName":"EVENT_TIMESTAMP"}}'


