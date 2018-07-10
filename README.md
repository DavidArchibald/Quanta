Quanta
======

A Discord Bot for multiple purpose usage. Currently in developement and getting the barebones setup.

However if you want to contribute to the development, or run your own version(why?) use the following steps.

1. Setup a virtual enviornment(if you want it), using `virtualenv venv` is ideal, because `venv` is in `.gitignore`.

2. Run `python setup.py install`, there is a chance that `psycopg2` will not install because of bad PyPi support, or `discord.py` having problems installing the rewrite version. Basically I am bad at dependencies and making this work well.

3. If you do not have a postgres server, create one, how to do so is outside the scope of setting up Quanta.

    * Create a table named `prefixes` used to store the prefixes at the channel level.

        The exact command I used was:
        ```SQL
        CREATE TABLE testy (
            serverid text PRIMARY KEY NOT NULL,
            prefix varchar(32)
        );
        ```
    * Create a table named `no_prefix` used for channels that opt out of prefixes. It's seperate to allow turning it back on, and also because no prefix is not natively supported.

        The command I used for this was:
        ```SQL
        CREATE TABLE prefixes (
            serverid text PRIMARY KEY NOT NULL,
            channels text[],
            globalhasprefix boolean
        );
        ```

4. All of these things require credentials, along with the actual bot account, so follow the instructions in `ReadMe.md` from secrets folder to setup the needed secret credentials.

5. Lastly running `python -m src.main` in the directory Quanta should explode with random errors if you've done something wrong(That's a future thing probably), or I've done this README wrong.
