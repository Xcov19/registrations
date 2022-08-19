#!/bin/bash

if [ "$ENV" == "test" ];
then
  python3 -m poetry run hypercorn -k uvloop --bind="0.0.0.0:${LOCAL_PORT}" --debug --reload registrations.infrastructure.adapters.api.app:app
else
  python3 -m poetry run hypercorn -k uvloop --bind="0.0.0.0:${LOCAL_PORT}" --reload registrations.infrastructure.adapters.api.app:app
fi;
