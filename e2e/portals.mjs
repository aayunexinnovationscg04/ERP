// Where each portal lives. Default: the production subdomains.
// LOCAL=1 targets the Vite dev servers instead (see deploy/README.md).
const LOCAL_ORIGINS = {
  dealer: 'http://127.0.0.1:5173',
  pilot: 'http://127.0.0.1:5174',
  admin: 'http://127.0.0.1:5175',
};

export const origin = (app) =>
  process.env.LOCAL ? LOCAL_ORIGINS[app] : `https://${app}.aayunexinnovations.com`;

// portalUrl('dealer', '/alerts') -> https://dealer.aayunexinnovations.com/alerts
export const portalUrl = (app, route = '/') => origin(app) + route;

// The "choose your portal" landing page.
export const LANDING = process.env.LANDING || 'https://erp.aayunexinnovations.com/';
