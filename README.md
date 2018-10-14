Quanta
======

A Discord Bot for multiple purpose usage. Currently in development and getting the barebones setup.

However if you want to contribute to the development, or run your own version(why?) use the following steps.

1. Setup a virtual environment(if you want it), using `virtualenv venv` is ideal, because `venv` is in `.gitignore`.

2. Run `python setup.py install`, there is a chance that `psycopg2` will not install because of bad PyPi support, or `discord.py` having problems installing the rewrite version. Basically I am bad at dependencies and making this work well.

3. This step is optional because it will fallback to simply using "?" as the prefix otherwise. However if you want to, setup a postgres server if you do not have one to use already, how to do so is outside the scope of setting up Quanta.

    * Create a table named `prefixes` used to store the prefixes.

        The exact command I used was:
        ```SQL
        CREATE TABLE prefixes (
            snowflake text PRIMARY KEY NOT NULL,
            prefix varchar(32)
        );
        ```
4. Another optional step, setting up Redis. Simply install Redis and run `redis-server` in the same directory as the bot before running it. The convention that Quanta follows is `type:id` where type is something such as `message`, `channel` or similar and the id is typically a snowflake.

5. All of these things require credentials, along with the actual bot account, so follow the instructions in `README.md` from secrets folder to setup the needed secret credentials.

6. Lastly running `python -m src.main` in the directory Quanta should explode with random errors if you've done something wrong(That's a future thing probably), or I've done this README wrong.
