# Python CDP
#### Currently supports CDP [r1179426][2] (Chrome 117).

Python CDP Generator (shortened to PyCDP) is a library that provides
Python wrappers for the types, commands, and events specified in the [Chrome
DevTools Protocol][1].  

The Chrome DevTools Protocol provides for remote control of a web browser by
sending JSON messages over a WebSocket. That JSON format is described by a
machine-readable specification. This specification is used to automatically
generate the classes and methods found in this library.

## Installation
You can install this library as a dependency on your project with:
```
pip install git+https://github.com/HMaker/python-cdp.git@latest
```
Change the git tag `@latest` if you need another version. To install for development, clone this
repository, install [Poetry][5] package manager and run `poetry install` to install dependencies.

## Usage
If all you want is automate Chrome right now, PyCDP includes a low-level client for asyncio and twisted:
```python
import asyncio
from pycdp import cdp
from pycdp.browser import ChromeLauncher
from pycdp.asyncio import connect_cdp

async def main():
    chrome = ChromeLauncher(
        binary='/usr/bin/google-chrome', # linux path
        args=['--remote-debugging-port=9222', '--incognito']
    )
    # ChromeLauncher.launch() is blocking, run it on a background thread
    await asyncio.get_running_loop().run_in_executor(None, chrome.launch)
    conn = await connect_cdp('http://localhost:9222')
    target_id = await conn.execute(cdp.target.create_target('about:blank'))
    target_session = await conn.connect_session(target_id)
    await target_session.execute(cdp.page.enable())
    # you may use "async for target_session.listen()" to listen multiple events, here we listen just a single event.
    with target_session.safe_wait_for(cdp.page.DomContentEventFired) as navigation:
        await target_session.execute(cdp.page.navigate('https://chromedevtools.github.io/devtools-protocol/'))
        await navigation
    dom = await target_session.execute(cdp.dom.get_document())
    node = await target_session.execute(cdp.dom.query_selector(dom.node_id, 'p'))
    js_node = await target_session.execute(cdp.dom.resolve_node(node))
    print((await target_session.execute(cdp.runtime.call_function_on('function() {return this.innerText;}', js_node.object_id, return_by_value=True)))[0].value)
    await target_session.execute(cdp.page.close())
    await conn.close()
    await asyncio.get_running_loop().run_in_executor(None, chrome.kill)

asyncio.run(main())
```
the twisted client requires [twisted][6] and [autobahn][7] packages:
```python
from twisted.python.log import err
from twisted.internet import reactor, defer, threads
from pycdp import cdp
from pycdp.browser import ChromeLauncher
from pycdp.twisted import connect_cdp

async def main():
    chrome = ChromeLauncher(
        binary='C:\Program Files\Google\Chrome\Application\chrome.exe', # windows path
        args=['--remote-debugging-port=9222', '--incognito']
    )
    await threads.deferToThread(chrome.launch)
    conn = await connect_cdp('http://localhost:9222', reactor)
    target_id = await conn.execute(cdp.target.create_target('about:blank'))
    target_session = await conn.connect_session(target_id)
    await target_session.execute(cdp.page.enable())
    await target_session.execute(cdp.page.navigate('https://chromedevtools.github.io/devtools-protocol/'))
    async with target_session.wait_for(cdp.page.DomContentEventFired):
        dom = await target_session.execute(cdp.dom.get_document())
        node = await target_session.execute(cdp.dom.query_selector(dom.node_id, 'p'))
        js_node = await target_session.execute(cdp.dom.resolve_node(node))
        print((await target_session.execute(cdp.runtime.call_function_on('function() {return this.innerText;}', js_node.object_id, return_by_value=True)))[0].value)
    await target_session.execute(cdp.page.close())
    await conn.close()
    await threads.deferToThread(chrome.kill)

def main_error(failure):
    err(failure)
    reactor.stop()

d = defer.ensureDeferred(main())
d.addErrback(main_error)
d.addCallback(lambda *args: reactor.stop())
reactor.run()
```

You also can use just the built-in CDP type wrappers with `import pycdp.cdp` on your own client implementation. If you want to try a different CDP version you can build new type wrappers with `cdpgen` command:
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

JSON files for the CDP spec can be found at https://github.com/ChromeDevTools/devtools-protocol/tree/master/json
```
Example:
```sh
cdpgen --browser-protocol browser_protocol.json --js-protocol js_protocol.json --output /tmp/cdp
```
You can then include the `/tmp/cdp` package in your project and import it like the builtin CDP types.  

### Updating built-in CDP wrappers
The `update-cdp.sh` script generates the builtin CDP wrappers, the `pycdp.cdp` package, by automatically fetching CDP protocol specifications from the [ChromeDevTools][8] repostitory.

**To generate types for the latest version:**
```shell
./update-cdp.sh
```
**To generate types for a specific version, you must provide full commit hash:**
```shell
./update-cdp.sh 4dd6c67776f43f75bc9b19f09618c151621c6ed9
```
P.S. Don't forget to make it executable by running `chmod +x update-cdp.sh`

## Implementation of a CDP client
The `pycdp.cdp` package follows same structure of CDP domains, each domain is a Python module and each command a function in that module.

Each function is a generator with a single yield which is a Python dict, on the CDP wire format,
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

[1]: https://chromedevtools.github.io/devtools-protocol/
[2]: https://github.com/ChromeDevTools/devtools-protocol/tree/39e36261937bf39dced789dd7ff19df6933d56d8
[3]: docs/getting_started.rst
[4]: https://github.com/hyperiongray/trio-chrome-devtools-protocol
[5]: https://python-poetry.org/docs/
[6]: https://pypi.org/project/Twisted/
[7]: https://pypi.org/project/autobahn/
[8]: https://github.com/ChromeDevTools/devtools-protocol
