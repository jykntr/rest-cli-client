rest-cli-client
===============
Overview
--------
A Python based command line REST client that makes saved REST requests and substitute values for variables that are defined in profiles or passed in as command line arguments.

Setup
-----
1. Copy the sample restcli.conf file to one of the following locations:
 * The directory pointed to by the RESTCLI_CONF environment variable
 * The current directory you will be running the command from
 * Your users home directory

2. Edit the restcli.conf file to setup any requests/profiles you'd like to use

Examples
--------
1. Run `restcli.py` with no arguments to get a list of requests

        #restcli.py
        usage: restcli.py [-h] {httpbinput,httpbinvars,httpbin} ...
        restcli.py: error: too few arguments
        #



        #restcli.py -h
        usage: restcli.py [-h] {httpbinput,httpbinvars,httpbin} ...

        optional arguments:
          -h, --help            show this help message and exit

        Requests:
          {httpbinput,httpbinvars,httpbin}
                                The request to execute
        #

2. Run `restcli.py {profilename} -h` to get information on the saved request

        #restcli.py httpbinvars -h
        usage: restcli.py httpbinvars [-h] [--profile {testprofile} | --no-profile]
                                      [--proxy protocol:host:port]
                                      [--verify | --no-verify]
                                      headervar paramvar

        Request name: httpbinvars
          Method    : get
          Headers   : myheader1: {{headervar}}, myheader2: myvalue2
          URL       : http://httpbin.org/get
          Parameters: myparam1={{paramvar}}, myparam2=paramvalue2
          Body      :

        optional arguments:
          -h, --help            show this help message and exit

        Profiles:
          Indicates which profile to use, if any, for variable substitution

          --profile {testprofile}, -p {testprofile}
                                The name of the profile to use for variable
                                substitution
          --no-profile          No profile will be used for variable substitution

        Options:
          Options to use when making HTTP requests

          --proxy protocol:host:port
                                Maps a protocol to a proxy. For example:
                                "http:proxy.url.com:8080". Multiple proxies can be
                                defined for different protocols.
          --verify              Verify SSL certificates.
          --no-verify           Do not verify SSL certificates.

        Required variable arguments:
          Variables that have no default value in the active profile (none)

          headervar
          paramvar

3. Actually make the `httpbinvars` request, notice that `{{headervar}}` and `{{paramvar}}` in the request are substituted with `value1` and `value2`.

        #restcli.py httpbinvars value1 value2
        {
          "url": "http://httpbin.org/get?myparam2=paramvalue2&myparam1=value2",
          "headers": {
            "Accept-Encoding": "gzip, deflate, compress",
            "Myheader2": "myvalue2",
            "X-Bluecoat-Via": "0159f16513239b9a",
            "Myheader1": "value1",
            "Host": "httpbin.org",
            "Accept": "*/*",
            "User-Agent": "python-requests/1.2.3 CPython/2.7.3 Windows/7",
            "Connection": "close",
            "Cache-Control": "max-stale=0"
          },
          "args": {
            "myparam2": "paramvalue2",
            "myparam1": "value2"
          },
          "origin": "152.219.153.75"
        }
        #

