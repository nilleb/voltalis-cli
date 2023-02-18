# voltalis-cli

A python client for the [myvoltalis](https://myvoltalis.com/) API.

This package is NOT maintained by voltalis. (Please don't sue me)

The myvoltalis application (was) slow, and it offers basic functionalities. Voltalis appliances by default can not be integrated with common domotic solutions (HomeAssistant, HomeKit, Google Home, ..).

This client provides an example about how to interface with the API.

## install

```sh
pip install voltalis-cli
```

## run

```sh
# executes the scenario "end-user clicking on all the menus of the myvoltalis web app"
python -m voltalis.cli login password
```
