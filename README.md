# Anime Recommendations

## Description

Fetch and store data from your anime list on [Anilist](https://anilist.co/).

## Data

The file with the data for all anime and media is too big for GitHub (134MB, subject to change).

You can access it on [GoogleDrive](https://drive.google.com/file/d/1A72uneEd4O5ypBTo13yGXRAtOgOgzPFZ/view?usp=sharing).

You need to save the file on the '_data_' folder under the name of '_media.json_'

## Running

### Usage:

```
/bin/python3 main.py <username> <arguments>
```

Example:

```
/bin/python3 main.py dummy_user --manga --display
```

### Arguments

- **--fetch-user** : Fetch user data even if list is already stored.
- **--fetch-media** : Continue fetching media data.
- **--display-media** : Display media data on file "display_media.json".
- **--update** : Update media data. (NOT IMPLEMENTED)
