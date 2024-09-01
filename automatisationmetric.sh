#!/bin/bash

# Fichier de récuperation des métriques 
python test_metrics_bandwith.py
python test_metrics_billing.py
python test_metrics_cpu.py
python test_metrics_ram.py