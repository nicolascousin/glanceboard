# Quote catalog

`fetch_quotes.py` retrieves free quotes from ZenQuotes and, when available, Quotable. It stores only the quote text and an internal theme in `quotes.json`, then copies the catalog to the web public assets.

Refresh the catalog with:

```sh
python3 quotes/fetch_quotes.py
```

The generator is resilient to an unavailable source: it uses whichever source responds and stops without replacing the existing catalog if none responds.
