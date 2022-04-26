# voltalis-cli

A python client for the [voltalis API](https://myvoltalis.com/).

This package is NOT maintained by voltalis.

The myvoltalis application is slow, and it offers basic functionalities. Voltalis appliances can not be integrated with common domotic solutions (HomeAssistant, HomeKit, Google Home). This client may constitute an example about how to interface with the API.

## install

```sh
pip install voltalis-cli
```

## run

```sh
# executes the scenario "end-user clicking on all the menus of the myvoltalis web app"
python -m voltalis.cli login password
```
