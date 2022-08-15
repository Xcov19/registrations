#!/bin/bash

python3 -m poetry run hypercorn -k uvloop --bind="0.0.0.0:8080" --debug --reload registrations.infrastructure.adapters.api.app:app
