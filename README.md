# PyCDP
Up to date fork of [python-chrome-devtools-protocol][1]. Currently supports CDP [r970581][2] (Chrome 97).

## Description
Python Chrome DevTools Protocol (shortened to PyCDP) is a library that provides
Python wrappers for the types, commands, and events specified in the [Chrome
DevTools Protocol](https://github.com/ChromeDevTools/devtools-protocol/).

The Chrome DevTools Protocol provides for remote control of a web browser by
sending JSON messages over a WebSocket. That JSON format is described by a
machine-readable specification. This specification is used to automatically
generate the classes and methods found in this library.

You could write a CDP client by connecting a WebSocket and then sending JSON
objects, but this would be tedious and error-prone: the Python interpreter would
not catch any typos in your JSON objects, and you wouldn't get autocomplete for
any parts of the JSON data structure. By providing a set of native Python
wrappers, this project makes it easier and faster to write CDP client code.

**This library does not perform any I/O!** In order to maximize
flexibility, this library does not actually handle any network I/O, such as
opening a socket or negotiating a WebSocket protocol. Instead, that
responsibility is left to higher-level libraries, for example
[trio-chrome-devtools-protocol](https://github.com/hyperiongray/trio-chrome-devtools-protocol).

[1]: https://github.com/HyperionGray/python-chrome-devtools-protocol
[2]: https://github.com/ChromeDevTools/devtools-protocol/tree/1b1e643d77dacc9568b5acc1efdeaec19c048a27