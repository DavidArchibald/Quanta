Secrets
=======

This folder contains all of the secret files.

* `token.txt` — The bot's token from [your app](https://discordapp.com/developers/applications/me) 
* `dbInfo.json` — A file containing the database information and credentials. It looks for json with the keys `dbname`, `user`, and `password`, and the values expected for the postgres server. Optionally there is `hostname`, set it to "localhost" if you are testing it locally or a special hostname.