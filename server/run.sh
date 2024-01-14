#!/bin/sh

gunicorn -w 1 main:main
