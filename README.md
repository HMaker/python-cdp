# Python CDP
Python CDP Generator (shortened to PyCDP) is a library that provides
Python wrappers for the types, commands, and events specified in the [Chrome
DevTools Protocol][1]. Currently supports CDP [r970581][2] (Chrome 97).

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
[trio-chrome-devtools-protocol][4].

## Installation
You can install this library as a dependency on your project with:
```
pip install git+https://github.com/HMaker/python-cdp.git@1.0.0
```
Change the git tag `@1.0.0` if you need another version. To install for development, clone this
repository, install [Poetry][5] package manager and run `poetry install` to install dependencies.

## Usage
You can install this package as a dependency to use the builtin CDP types with `import cdp`, but if you want to try a different CDP version you can build new wrappers with `cdpgen` command:
```
usage: cdpgen <arguments>

Generate Python types for the Chrome Devtools Protocol (CDP) specification.

optional arguments:
  -h, --help            show this help message and exit
  --browser-protocol BROWSER_PROTOCOL
                        JSON file for the browser protocol
  --js-protocol JS_PROTOCOL
                        JSON file for the javascript protocol
  --output OUTPUT       output path for the generated Python modules

JSON files for the CDP spec can be found at https://github.com/ChromeDevTools/devtools-protocol
```
Example:
```sh
cdpgen --browser-protocol browser_protocol.json --js-protocol js_protocol.json --output /tmp/cdp
```
You can then include the `/tmp/cdp` package in your project and import it like the builtin CDP types.

## Implementation of a CDP client
The `cdp` package follows same structure of CDP domains, each domain is a Python class and each command
a method of that class.

Each method is a generator function with a single yield which is a Python dict, on the CDP wire format,
containing the message that should be sent to the browser, on resumption the generator receives the message from browser:
```python
import cdp

# Get all CDP targets
command = cdp.target.get_targets() # this is a generator
raw_cdp_request = next(command) # receive the yield
raw_cdp_response = send_cdp_request(raw_cdp_request) # you implement send_cdp_request, raw_cdp_request is the JSON object that should be sent to browser
try:
    command.send(raw_cdp_response) # send the response to the generator where raw_cdp_response is the JSON object received from browser, it will raise StopIteration
    raise RuntimeError("the generator didnt exit!") # this shouldnt happen
except StopIteration as result:
    response = result.value # the parsed response to Target.get_targets() command
print(response)
```
For implementation details check out the [docs][3].

<br>
<hr>
PyCDP is licensed under the MIT License.
<hr>

[1]: https://github.com/ChromeDevTools/devtools-protocol/
[2]: https://github.com/ChromeDevTools/devtools-protocol/tree/1b1e643d77dacc9568b5acc1efdeaec19c048a27
[3]: docs/getting_started.rst
[4]: https://github.com/hyperiongray/trio-chrome-devtools-protocol
[5]: https://python-poetry.org/docs/
