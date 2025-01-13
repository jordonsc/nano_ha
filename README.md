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
        title: My Nanoleaf Light
        addr: <IP_ADDRESS>
        token: <AUTH_TOKEN>

Colour Modes
------------
I've hardcoded the lights to only support "brightness" colour mode. For light systems like Nanoleaf, this is actually
the wrong approach as they should be using RBG, colour temp, etc - but a flaw in the design for Home Assistant is when
a light system is using an "effect" like you'd typically do with Nanoleaf, it provides no option to simply change the
brightness without including a colour/temp value, too.

As I, personally, only want to change the brightness and on/off state via automation, this is perfect for me. If you
need to use this stop-gap integration but need colour support, drop me a message and I can help out.
