const base = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Internal link with the deploy base path, e.g. url('/sme/') -> '/ipo-update/sme/'. */
export function url(path = '/'): string {
  return `${base}${path.startsWith('/') ? path : `/${path}`}`;
}
