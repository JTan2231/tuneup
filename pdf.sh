#!/bin/bash

pdflatex -interaction=nonstopmode resume.tex
mkdir temp
mv resume* temp
mv temp/resume.pdf .
rm -r temp
