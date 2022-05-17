# ETM scenario tools

This repository contains a Python tool to create and update scenarios in the [Energy Transition Model](https://pro.energytransitionmodel.com/) (ETM) and export scenario outcomes using an [API](https://docs.energytransitionmodel.com/api/intro). The tool can be operated by altering CSV input files. No coding experience is required.

The full documentation of all features of the `scenario-tools` and how to use them is available on the [ETM docs](https://docs.energytransitionmodel.com/main/scenario-tools/introduction).

### Installing

Make sure you have [Python 3](https://www.python.org/downloads/) installed. Then, install all required libraries by opening a terminal window in the `scenario-tools` folder (or navigate to this folder in the terminal using `cd "path/to/scenario-tools folder"`).

It is recommended (but not required) that you use [`pipenv`](https://pipenv.pypa.io/en/latest/) for running these tools. When using `pipenv`
it will create a virtual environment for you. A virtual environment helps with keeping the libaries you install here separate of your global libraries (in
other words your `scenario-tools` will be in a stable and isolated environment and are thus less likely to break when updating things elswhere on your computer)
and this one comes with some nice shortcuts for running the tools.

You can instal `pipenv` with `pip` or `pip3` if you don't have it installed yet.
```
pip3 install pipenv
```

Then you can create a new environment and install all the libraries in one go by running:
```
pipenv install
```


Alternatively, if you do **not** want to use `pipenv` you can also install the requirements globally by running:
```
pip3 install -r requirements.txt
```


### Questions and remarks

If you have any questions and/or remarks, you may reach out to us by:

* Creating an [issue](https://github.com/quintel/scenario-tools/issues) on this repository and assign one of the Quintel members, e.g.:
  * [Roos de Kok](https://www.github.com/redekok)
  * [Nora Schinkel](https://www.github.com/noracato)
* Sending an e-mail to [info@quintel.com](mailto:info@quintel.com)
