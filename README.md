# Spotifyplayer app

## Set up an app in Spotify's developer dashboard

1) Go to [Spotify's Developer Site](https://developer.spotify.com)
2) Log in
3) Navigate to: _your profile_ >> _Dashboard_ >> _Create app_
4) App name can be whatever you want (e.g. ```SpotiFly```)
5) List any description you want, this part is not important
6) Redirect URI: ```http://127.0.0.1:6969/oauth_callback```
7) Create app and copy `Client ID` and `Client secret`

## Set environment variables

Place Client ID and Client secret into an ```.env``` file in the root directory with the structure:

``` markdown
CLIENT_ID = <Client Id from Spotify>
CLIENT_SECRET = <Client Secret from Spotify>
```

An [example](.env_example) is provided for ease of use.

## Run the app

### uv

Run as a desktop app:

``` terminal
uv run flet run
```

Run as a web app:

``` terminal
uv run flet run --web
```

### Poetry

Install dependencies from `pyproject.toml`:

``` terminal
poetry install
```

Run as a desktop app:

``` terminal
poetry run flet run
```

Run as a web app:

``` terminal
poetry run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/getting-started/).

## Build the app

### Android

``` terminal
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

``` terminal
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

``` terminal
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

``` terminal
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

``` terminal
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).
