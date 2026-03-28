#!/bin/bash
curl -X POST "http://127.0.0.1:8000/ingest" -H "Content-Type: application/json" -d  "{\"file_path\": \"./finazamt.pdf\"}"