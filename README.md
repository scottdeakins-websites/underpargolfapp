# Under Par Performance Golf — website

Static site for underpargolfapp.com, deployed by Netlify from `main` (publishes `public/`).

## Editing
- Pages: `src/content/pages/*.md` · Blog posts: `src/content/posts/*.md`
- Styles: `src/assets/style.css`
- Rebuild after any change: `pip install markdown pyyaml && python3 src/build.py`, then commit `public/` too.

## Sign-up link
Every "Start" button goes to `/pages/join-today`. The sign-up button on that page uses `SIGNUP_URL`
at the top of `src/build.py` — currently a placeholder email link. Swap in the Mighty Forms sign-up URL and rebuild.

## SEO
- Old Shopify URLs are kept (`/pages/...`, `/blogs/<topic>/<post>`), so rankings carry over when the domain moves.
- `public/_redirects`: posts not migrated yet send visitors to their topic page (302).
- Each page has its own title/description, canonical URL, JSON-LD (Organization, Service at $39, BlogPosting, FAQ, breadcrumbs), plus sitemap.xml and robots.txt.

## To do
- Swap in the Mighty Forms sign-up URL (`SIGNUP_URL`)
- Migrate the remaining 56 blog posts
- Move privacy policy and terms off Shopify before the domain switches
- Point underpargolfapp.com at Netlify, then resubmit sitemap in Search Console
