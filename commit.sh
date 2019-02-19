#!/bin/bash 
comments=$1
git add .
git commit -m "$comments"
git push 
