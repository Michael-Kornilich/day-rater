Data flow inbound:

* POST "Commit to the DB" request to record the information
* GET "Analyze" request from the facade to launch the data analysis script (async obviously)
* Receives the results from the analyser
* Calls the APIs as a background task

Data flow outbound:

* Calls the data analyser script
* Packages and calls the commit request to the db through the handler
* Routes data from data-analyser to the facade
