Secrets
=======

This folder contains all of the secret configuration information in `config.yaml`
It's in the following format

```yaml
bot_info:
  token: "string"

database_info:
  database: "string",
  user: "string",
  password: "string",
  host: "string"

redis:
  address: "string",
  password: Optional["string"]


wolphram-alpha:
  app-id: "string"
````

If any section is omitted(besides `bot_info`) it should gracefully degrade.
