# Protocols for communication inside the Boreas Project #

## About this document ##
This document details the communication between the different components of the Boreas System. It is aimed to be a precise description of the communication, so that there is no doubt as to how the communication should be done.

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

Please don't hesitate to add a comment/issue if anything is unclear, you disagree with something or you want to know why something is the way it is. While the document itself MUST be in English, comments MAY be made in Norwegian.

Since this is an iterative and agile project, this document and the protocols are subject to changes and additions.
## Changelog ##

* 24th February 2016: Created this document
* 1st March 2016: Changed from custom format to using HTTP.

## To do ##

* Add examples at the end of the document.
* Define and describe the API of `CarAPI` (that is, communication between clients (including web server) and the `CarAPI`), preferable in a separate document.

## CarDataStream → CarCommunicator: Data about the car state ##

The `CarDataStream` will transmit information about the state of the car to the `CarCommunicator`.

### Connection details ###
The communication MUST occur through HTTP, with `Content-Type` set to `application/json`.  
`CarDataStream` MUST send this data every 10 second or more often, but it SHOULD send it every second.  
`CarCommunicator` SHOULD listen on port 34444, and `CarDataStream` MUST send to port 34444 if no other port is specified.

### Request format ###
The request MUST be an HTTP POST request, with the following JSON as POST data. The JSON matches the [OpenFX Message Format](https://github.com/openxc/openxc-message-format#commands) in a sense, but it is still different because 1) there's no timestamp data (the data is assumed to be fresh, current data), 2) there's no metadata and 3) there's no duplicate data for the same signal name. Instead, the JSON looks like this:

```json
{
  "<signal name>": "<signal value>",
  "<signal name>": "<signal value>",
  ...
}
```
In other words, the signal name is the name of the property and the signal value is the value of that property. See the [OpenFX Message Format](https://github.com/openxc/openxc-message-format#official-signals) for a list of signal names and their allowed values.  
Note that duplicate signal names MUST NOT appear in the JSON. Instead, the most recent value should be used for any signal name.

### Response ###
`CarCommunicator` MUST acknowledge the request with status code 200, or with another appropriate status code in case of error.


## CarCommunicator → CarControl: Controlling the car ##

The `CarCommunicator` uses this protocol to set the temperature and state of the air condition. It may also query `CarControl` for the current settings for the air condition.

### Connection details ###
The communication MUST occur through HTTP.  
There is no restriction as to how often communication takes place.  
`CarControl` SHOULD listen on port 34445, and CarCommunicator MUST send to port 34445 if no other port is specified.
### Request format ###
There are two types of requests:
* `set` - change the target temperature or turn the air condition on/off.
* `status` - get the current target temperature and state of the air condition.
Those are separated by using different URIs, namely set/ and status/. The JSON data is embedded as POST data.

### Response format ###

#### Set ####

`CarControl` MUST acknowledge this request with HTTP status code 200 if everything went OK, or with the appropiate status code if an error occured.

#### Status ####
`CarControl` MUST respond with HTTP status code 200 with the JSON data as the page body, or with the appropiate status code in case of error.
### JSON format ###

This format is used by the set request, and the status response. The JSON consists of one object with the following properties:

* `enabled` - True if the air condition is currently active, false otherwise.
* `temperature` - Target temperature in degrees Celcius, expressed as a double.
 
When using the set request, one of the properties CAN be omitted. If omitted, that property will remain unchanged. When the `CarControl` responds to a status-message, it MUST include all properties.

```json
{ "enabled":"<true/false>", "temperature":"<temperature_value>"}
```


## CarCommunicator → CarAPI: Telling the proxy the state of the car and fetching data from the proxy ##
This is probably the most complex part of the protocols. Not only must the Raspberry Pi update the server about the car's current levels and state, it must also get back any requests the user has made, for example "start heating the car".

It is difficult to initiate contact with the Raspberry Pi from the Internet, since its IP address is unknown and may change and it may sit behind proxies and routers that mask its IP address (to conserve IP4-addresses). Therefore, we use polling, in which the Raspberry Pi will send new, fresh data to the CarAPI server, and in return it will get any new messages from CarAPI's queue. 
### Communication details ###
The communication MUST occur through HTTP.  
The `CarCommunicator` MUST update the `CarAPI` every 90 seconds or less. As long as we use polling, it SHOULD do this every 30 seconds or less. There SHOULD BE 10 seconds between each update, though.  
`CarAPI` SHOULD listen on port `34446`, and `CarCommunicator` MUST send to port `34446` if no other port is specified.

### Request details ###
There are two different types of messages that the `CarCommunicator` can send to the `CarAPI`:
* `status` - new data about the car state
* `error` - information about an error that has occured

In return, the `CarAPI` responds with messages for the `CarCommunicator`.

#### status ####
The status request MUST be made as a POST request to the URI `/status/`. The POST data MUST be JSON. The JSON format is equal to the [OpenXC Messaging Format](https://github.com/openxc/openxc-message-format#trace-file-format), except the JSON objects are contained in a list (not separated by newlines alone). Thus, it differs from the data sent from `CarDataStream` in that duplicate signal names are allowed, since they have a timestamp. The timestamp represents the time at which the CarCommunicator received that data. 

Additional signal types are allowed: the current state of the things that CarAPI can control. This means that `AC_enabled` and `AC_temperature` is sent together with the rest of the car data.
```json
[

{"name":"<signal_name>", "value":"<signal_value>",   
"timestamp":"<time>"},
...

]
```
#### error ####
The error request MUST be made as a POST request to the URI `/error/`. The POST data MUST be JSON following the following format:
##### JSON format #####
Consist of one object, with the following properties:
* `errno` - unsigned int, error number, used to give a user friendly message to the user.
* `message` - string, detailed error message intended for developers. It SHOULD give as specific data as possible about the possible cause.
```json
{"errno":"<code>", "message":"<message>"}
```
##### Error numbers #####

| errno  | Type of error |
| ------- | --------- |
| 0 | Unknown error |
| 1 | Communication error with CarControl | 
| 2 | Other error relating to CarControl |
| 3 | No data from CarDataStream since last update |
| 4 | Error inside CarCommunicator |
| 5 | Wrong format/error relating to CarDataStream |
| 6 | The car battery level is too low for the AC to be turned on |
| 7 | The car battery level has dropped to a critical limit |


### Response format ###
This might also be called the third message type, and is sent as response from `CarAPI` to `CarCommunicator` whenever `CarCommunicator` sends anything to `CarAPI`.

As usual, the status code MUST be 200 if everything went okay, or the appropiate status code in case of error. If the status code is 200, then the response body MUST be JSON in the following format:

The root is a list. It MAY contain zero, one or multiple objects. If it contains zero objects, the JSON MAY be omitted (resulting in a Content-Length of zero bytes). 
Each of those objects have two properties:
* `type`: name of this message
* `value`: this message's value

#### Example ####
```json
[
	{"type": "AC_enabled", "value": true},
	{"type": "AC_temperature", "value": 22.5}
]
```

#### Message types and their values ####

| Type | Value | Explanation |
| ---- | ---- | ---- |
| `AC_enabled` | boolean | True if the AC is to be turned on; false if the AC is to be turned off |
| `AC_temperature` | double | The target temperature in degrees Celcius, which the AC should work towards. |



