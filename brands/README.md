# Brand icons

These icons need to be submitted to the [home-assistant/brands](https://github.com/home-assistant/brands) repository for the **ChaChing Panel** integration icon to appear in Home Assistant.

## How to submit (one-off, after this PR is merged the icon shows for everyone)

1. Fork `https://github.com/home-assistant/brands`.
2. In your fork, create the directory `custom_integrations/chaching_panel/`.
3. Copy these 4 files into that directory:
   - `icon.png` (256×256)
   - `icon@2x.png` (512×512)
   - `logo.png`
   - `logo@2x.png`
4. Open a Pull Request titled `Add ChaChing Panel`.
5. Wait for review (usually <1 week). When merged, HA will fetch the icon automatically — no need to release a new integration version.

## Files

| File         | Size    | Usage                              |
|--------------|---------|------------------------------------|
| icon.png     | 256×256 | Default integration icon           |
| icon@2x.png  | 512×512 | Retina/HiDPI integration icon      |
| logo.png     | ≤256    | Wider brand logo (optional)        |
| logo@2x.png  | ≤512    | Retina brand logo (optional)       |
