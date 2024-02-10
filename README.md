# Anime Recommendations

## Description

Get animanga recommendations based on the your anime list fetched from [Anilist](https://anilist.co/).

## Data

### Media File

The file with the data for all media is too big for GitHub (134MB, subject to change).

You can access it on [GoogleDrive](https://drive.google.com/file/d/1A72uneEd4O5ypBTo13yGXRAtOgOgzPFZ/view?usp=sharing).

You need to save the file on the '_data_' folder under the name of '_media.json_'

## Preferences

## Recommendations

## Running

### Usage:

```
/bin/python3 main.py <username> <arguments>
```

Example:

```
/bin/python3 main.py dummy_user --display-media --recommendations 20
```

### Arguments

- **--fetch-user** : Fetch user data even if list is already stored.
- **--fetch-media** : Continue fetching media data.
- **--display-media** : Display media data on file _display_media.json_.
- **--update** : Update media data. (NOT IMPLEMENTED)
- **--preferences** : Output dictionary with user preferences
- **--recommendations \<size\>** : Output array of size <size> sorted by the most recommendation score
