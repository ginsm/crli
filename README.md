# crly

A streamlink wrapper that allows you to easily watch and track crunchyroll series.



 
## Install
Run `install.sh` -- this script will install this package via `pip`.



 
## Configuration
Configuration is done via [streamlink](https://streamlink.github.io/latest/cli.html).

Here's a basic configuration to get started:

```
crunchyroll-username=<email>
crunchyroll-password=<password>
player=/usr/bin/vlc
default-stream=best
```

Click this [link](https://streamlink.github.io/latest/cli.html#plugin-specific-configuration-file) to find where you should create your configuration file. Replace `pluginname` with `crunchyroll` whilst creaitng the file, i.e. `config.crunchyroll`.


 
## Commands

```
Usage:
  crly [--help | --version] [options]

Options:
  -s, --show <name>        Select a show
  -e, --episode <number>   Select an episode (default: oldest ep)
  -p, --play               Play the selected episode
  -a, --autoplay           Autoplay episodes (default: false)
  -n, --next               Select the next episode
  -i, --info               Print information about the show
  -t, --track              Begin tracking a show
  -u, --updates            Check tracked shows for updates
  -d, --debug              Print debug information
  -h, --help               Print this help screen
  -v, --version            Print the current version
```