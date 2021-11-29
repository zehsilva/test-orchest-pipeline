#!/bin/bash

# Install any dependencies you have in this shell script.

# install python 3.8 
source /opt/conda/etc/profile.d/conda.sh

# Hack to move bootscript
sudo mv /orchest/bootscript.sh /orchest/bootscript-original.sh
printf '#!/usr/bin/env bash\n\nsource /opt/conda/etc/profile.d/conda.sh && conda activate py38 && source /orchest/bootscript-original.sh' >> /tmp/bootscript.sh
sudo mv /tmp/bootscript.sh /orchest/bootscript.sh
sudo chmod ugo+x /orchest/bootscript.sh

# Set up Python 3.8 environment
conda create -n py38 python=3.8 future
conda activate py38

# Install Orchest dependencies
cd /orchest/services/base-images/runnable-shared/runner
pip install -r requirements.txt

# Install project dependencies
pip install -r https://raw.githubusercontent.com/snowflakedb/snowflake-connector-python/v2.6.0/tested_requirements/requirements_38.reqs
pip install diepvries snowflake-connector-python==2.6.0


# E.g. pip install tensorflow
pip install pyclarify pandas salesforce-merlion matplotlib requests

