import { createApp, createIdentityProvider } from '@kottster/server';
import schema from '../../kottster-app.json';

/* 
 * For security, consider moving the secret data to environment variables.
 * See https://kottster.app/docs/deploying#before-you-deploy
 */
export const app = createApp({
  schema,
  secretKey: 'ZFACFdbog4YEu5wrYLcPu2Ryb4H2rtcv',
  kottsterApiToken: 'CApT2iAvx3ztzy0BuMYikUZHstYLSjl5',

  /*
   * The identity provider configuration.
   * See https://kottster.app/docs/app-configuration/identity-provider
   */
  identityProvider: createIdentityProvider('sqlite', {
    fileName: 'app.db',

    passwordHashAlgorithm: 'bcrypt',
    jwtSecretSalt: 'Bdg4k7LkGRB5OKMK',
    
    /* The root admin user credentials */
    rootUsername: 'admin',
    rootPassword: 'admin',
  }),
});