Secrets
=======

This folder contains all of the secret files, each have their own instructions

* `token.txt` — The bot's token from [your app](https://discordapp.com/developers/applications/me), select your bot from the list(or create one), and then copy the token from the app's bot user.
* `dbInfo.json` — A file containing your database's information and credentials. It looks for json with the keys `dbname`, `user`, and `password`, and the values expected for the postgres server. Optionally there is `hostname`, set it to "localhost" if you are testing it locally or a special hostname.