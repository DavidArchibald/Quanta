Quanta
======

A Discord Bot for multiple purpose usage. Currently in development and getting the barebones setup.

However if you want to contribute to the development, or run your own version(why?) use the following steps.

1. Setup a virtual environment(if you want it), using `virtualenv venv` is ideal, because `venv` is in `.gitignore`.

2. This step is optional because it will fallback to simply using "?" as the prefix otherwise. You will need a postgres server.

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

6. Lastly running `python -m src.main` in the directory Quanta should run it.
