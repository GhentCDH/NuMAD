import { KnexPgAdapter } from "@kottster/server";
import knex from "knex";

/**
 * Replace the following with your connection options.
 * Learn more at https://knexjs.org/guide/#configuration-options
 */
const client = knex({
  client: "pg",
  connection: {
    connectionString: "postgresql://numad:numad@db:5432/numad",
    ssl: false,
  },
  searchPath: ["public"],
});

export default new KnexPgAdapter(client);

