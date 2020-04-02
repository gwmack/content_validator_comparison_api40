# Looker Content Cleanup

Compare the output of content validator runs in production and development mode. Additional broken content in development mode will be outputted to a csv file. Use this script to test whether LookML changes will result in new broken content.

### Prerequisites

These scripts rely on the new Looker [Python SDK](https://github.com/looker-open-source/sdk-codegen/tree/master/python), which requires Python 3.7+.

Additional required Python dependencies can be found requirements.txt, and can be installed with `pip`.

### Getting started

* Clone this repo, and configure a file called `looker.ini` in the same directory as the two Python scripts. Follow the instructions [here](https://github.com/looker-open-source/sdk-codegen/tree/master/python#configuring-the-sdk) for more detail on how to structure the `.ini` file. The docs also describe how to use environment variables for API authentication if you so prefer.
* Install all Python dependencies in `requirements.txt`

### Usage

Run `python content_validator_comparison.py` to compare broken content in production and development mode (whatever branch you currently default to when you enter dev mode). Broken content that only exists in your dev branch will be outputted into a csv file.

An important thing to be aware of is that this across all projects, so you'll want to make sure that your dev branches are all up to date. That is, enter each project you have access to and "Pull from Production"

