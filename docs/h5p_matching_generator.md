# Matching H5P Generator

The API exposes a simple HTML utility that turns a two-column table of terms and definitions into a downloadable `H5P.Matching` package.

## How to use

1. Start the FastAPI app (e.g. `uvicorn app.main:app --reload`).
2. Open [`/api/h5p/matching/generator`](http://localhost:8000/api/h5p/matching/generator) in a browser.
3. Enter an activity title and optional instructions.
4. Paste your term/definition table. The parser accepts:
   - CSV rows (`Term,Definition`)
   - Tab-separated rows (copying from spreadsheets)
   - Markdown tables
5. Submit the form to download a ready-to-import `*.h5p` file.

The generated package bundles `H5P.Matching` and its dependencies so it can be uploaded to any H5P-compatible platform.

## Required library assets

The generator copies library assets from `app/static/h5p_libraries`. The `H5P.Matching-1.0` directory must contain compiled files referenced in `library.json` (for example `dist/h5p-matching.js` and `dist/h5p-matching.css`). If they are missing, the generator will return an error like:

```
Library H5P.Matching is missing built assets (dist/h5p-matching.js, dist/h5p-matching.css).
Run `npm install && npm run build` in the library directory to compile them.
```

Compile the assets once with:

```bash
cd app/static/h5p_libraries/H5P.Matching-1.0
npm install
npm run build
```

> **Note:** `node-sass` may not ship prebuilt binaries for the latest Node releases. If the build fails, install/run with an LTS version of Node.js (v18 or v20) before reattempting the commands above.

