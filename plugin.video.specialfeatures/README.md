# plugin.video.specialfeatures

[![](https://img.shields.io/badge/supports-kodi%2017%20|%2018-blue.svg)](https://forum.kodi.tv/showthread.php?tid=327042) [![GitHub release](https://img.shields.io/github/release/kasamedia/plugin.video.specialfeatures.svg)](https://github.com/kasamedia/plugin.video.specialfeatures/releases/latest) [![GitHub tag](https://img.shields.io/github/tag/kasamedia/plugin.video.specialfeatures.svg)](https://github.com/kasamedia/plugin.video.specialfeatures/releases) [![license](https://img.shields.io/github/license/kasamedia/plugin.video.specialfeatures.svg)](https://github.com/kasamedia/plugin.video.specialfeatures/blob/master/LICENSE)

### Welcome!

Special Features is inspired by the upcoming Blu-ray features being introduced in Kodi 18. Given a properly structured 'Extras' directory, this addon will present all of the bonus videos, discs and alternate versions of the movies and tv shows in your library.

## Setup

For Special Features to properly detect your extras, you wll need to create an 'Extras' folder in the root folder of each video that you want to add special features to.

eg.
```
    The Pirates of the Caribbean\
                                  >BDMV
                                  >CERTIFICATE
                                  >Extras
                                  >poster.jpg
                                  >fanart.jpg
```

This Extras folder can contain individual video clips, or full Blu-ray or DVD rips.

```
    The Pirates of the Caribbean\Extras\
                                        >Theactrical Trailer.mkv/mp4/ etc
                                        >3D Verison\BDMV\index.bdmv
                                        >Bonus Disc\VIDEO_TS\VIDEO_TS.IFO
```

## Accessing Special Features

There are currently two ways to access Special Features. The 'builtin' method is to simply access the 'Special Features' addon directly. If any special features are available, they will be presented in a video list.

The following skins currently provide official support for Special Features:

- [x] AppTV
- [x] Andromeda
- [x] Black Glass Nova
- [x] Chroma
- [x] Nebula
- [x] Rapier

While the long-term goal is to see every skin supporting Special Features natively, for now patches are available for many of the official skins in the [skin xml](https://github.com/kasamedia/plugin.video.specialfeatures/tree/master/resources/skin%20xml/) directory. The following skins are currently supported, with more being added as time permits:

- [x] Aeon Nox Silvo
- [x] Amber
- [x] Arctic Zephyr
- [x] Bello 6
- [x] Box
- [x] Confluence
- [x] Eminence 2
- [x] Estuary
- [x] FTV
- [x] Fuse Neue

If you use one of these skins, you can add a handy button to video info pages for videos with Special Features by overwriting the files in your skin folder with the supplied patches. Don't see a patch for your favorite skin? Feel free to request it (or submit it yourself)!

### Context Menu Access

Originally, Special Features were accessed through a context menu entry. This method was dropped to prevent adding to the existing clutter of context menus and in the hopes of providing a more intuitive, streamlined solution. However, given that patches are not available for all themes, the context menu is back as a togglable option.

## Recommended Advanced User Settings

Without tweaking your [advanced settings](https://kodi.wiki/view/advancedsettings.xml), you will end up with all of your extras being unceremoniously dumped into your media library. To prevent this, it is recommended that you add the following block to your `advancedsettings.xml` file. The Advanced Settings file is not created by default, so you will likely have to add it yourself.

```
<advancedsettings>
    <video>
        <!-- VideoExtras: Section Start -->
        <excludefromscan action="append">
            <regexp>/Extras/</regexp>
            <regexp>[\\/]Extras[\\/]</regexp>
        </excludefromscan>
        <excludetvshowsfromscan action="append">
            <regexp>/Extras/</regexp>
            <regexp>[\\/]Extras[\\/]</regexp>
        </excludetvshowsfromscan>
        <!-- VideoExtras: Section End -->
    </video>
</advancedsettings>
```

### MySQL Server Support

The optional SQL database option has been tested on MySQL 5.7 and MariaDB 10.2.

Assuming you already have MySQL setup and running, simply go to addon settings MySQL tab and fill in your information. It's as simple as that!

## Getting Support

We recommend all users with support questions comment on our [forum thread](https://forum.kodi.tv/showthread.php?tid=327042). GitHub is used for core development only, and is not the place to seek help or report non-developer issues.

## Contributions

Anyone is welcome to contribute to Special Features. Please read the [guidelines for contributing](https://github.com/evolvetv/plugin.video.specialfeatures/blob/master/CONTRIBUTING.md) to this repository.

There are various ways you can contribute:

1. Raise an [Issue](https://github.com/evolvetv/plugin.video.specialfeatures/issues) on GitHub
2. Send us a Pull Request with your bug fixes and/or new features
