## Dependency: The only dependency is Python 3.5.2 + and python3 in the command prompt/terminal should invoke the Python3 interpreter

## Running the application:

1. python3 socket_server.py <<PORT_NUMBER>> e.g. python3 socket_server.py 9092
2. Sample client: python3 socket_client.py <<PORT_NUMBER>> e.g. python3 socket_client.py 9092

This client can be written in any language and just needs to listen to the same port as where the server is sending the
records



## Details of response

Response is sent once every 1/6th of a second
The response format is the below JSON
{
"timestamp" -> The timestamp when the response was generated
"rates" -> A list of rate objects where each rate has the below structure
{
 "currency" -> The name of the currency
 "rate" -> The current exchange rate at that moment for 1 unit of the currency to INR
}
}


## Sample Json 

Refer attached file(sample_response.json) in the zip 

