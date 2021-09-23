# Vendomatic Backend

Web Backend application developed for testing a beverage vending machine.

## Setup

### Local development

In order set up and run the project for local development, you can use Docker, and run the following command:

`docker-compose up -d --build`

which uses the `docker-compose.yml` file as a source of configuration.

You must also define a `.env.dev` file. You can build one based upon the `.env.template` file located in this repository.

### Production

In order to set up the production environment, you can use the following command:

`docker-compose -f docker-compose.prod.yml up -d --build`

which uses the `docker-compose.prod.yml` file as a source of configuration, and sets up an nginx instance.

You must also define a `.env.prod` file. You can build one based upon the `.env.template` file located in this repository.

Also, a `.env.prod.db` file must be present in order to define the database credentials data. You can build one based upon the `.env.db.template` file located in this repository.
