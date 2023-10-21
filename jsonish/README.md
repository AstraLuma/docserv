# jsonish

A utility for returning structured data (JSON) without DRF.

Supports content negotiation and HTML.

Supports the following serializations:

- JSON
- msgpack (requires `msgpack`)
- YAML (requires `yaml`)

TODO: Support django serialization and free-form data

## Error Views

To get jsonish's content negotiation on error views, add this to `urls.py`:

```
handler400 = 'jsonish.views.error_400'
handler403 = 'jsonish.views.error_403'
handler404 = 'jsonish.views.error_404'
handler500 = 'jsonish.views.error_500'
```

If you want to use the default error templates, make sure that `jsonish` is in `INSTALLED_APPS`.
