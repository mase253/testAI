#!/bin/bash
curl -X POST "http://127.0.0.1:8000/query"   -H "Content-Type: application/json"  -d "{\"query\": \"Examples for taxable remunerations in kind\"}"