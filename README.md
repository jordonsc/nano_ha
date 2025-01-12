Nanoleaf Home Assistant Integration
===================================
While Home Assistant offers native support for Nanoleaf, it has a connection bug that causes Nanoleaf devices to
appear offline and has not been maintained for many years. The purpose of this custom integration is to create a simple
but reliable alternative until such time as official support is in a better place.

This is a minimalistic custom component that uses the Nanoleaf API to connect directly to the devices. You must first
acquire an auth token from the device, then add the device to your `configuration.yaml` file.

Generating an Auth Token
------------------------
Determine the IP address of your Nanoleaf device and set it to use a static IP address on your router. Once you have 
the IP address, press and hold the power button on the device for 5 seconds and then run the following command:

    ./src/gen_token <IP_ADDRESS>

An auth token will be returned.

Adding the device to Home Assistant
-----------------------------------
Add the following to your `configuration.yaml` file:

    light:
      - platform: nano_ha
        addr: <IP_ADDRESS>
        token: <AUTH_TOKEN>