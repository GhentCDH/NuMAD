import { KnexPgAdapter } from "@kottster/server";
import { getEnvOrThrow } from "@kottster/common";
import knex from "knex";

const DATABASE_URL = getEnvOrThrow('DATABASE_URL');

const client = knex({
  client: "pg",
  connection: {
    connectionString: DATABASE_URL,
    ssl: false,
  },
  searchPath: ["public"],
});

export default new KnexPgAdapter(client);

