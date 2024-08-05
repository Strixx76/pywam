# pywam

[![PyPi Downloads][pypibadge]][pypilink]

pywam is an fast and lightweight python asyncio library without external dependencies for communicating with Samsung Wireless Audio (R) speakers (WAM). It was developed to be used for integrating the speakers in Home Assistant.

## Features

- Control Samsung Multiroom speakers.
- Keep track of the state of Samsung Multiroom speakers.

## Installation

```bash
pip install pywam
```

## Usage

Set the speaker volume to 50% with python context manager:

```python
from pywam.speaker import Speaker

async with Speaker('192.168.1.100') as speaker:
    speaker.set_volume(50)
```

Example of controlling media playback:

```python
# Play
await speaker.cmd_play()
# Pause
await speaker.cmd_pause()
# Shuffle mode
await speaker.set_shuffle(True)
```

Get notifications about speakers state:

```python
from pywam.speaker import Speaker

def state_receiver(event):
    print(event)

speaker = Speaker('192.168.1.150')
speaker.events.register_subscriber(state_receiver, 2)
speaker.connect()
speaker.update()
```

## Contribute

- Issue Tracker: https://github.com/Strixx76/pywam/issues
- Source Code: https://github.com/Strixx76/pywam

## Style guide

PEP8 and Google styled PEP257.
But none of them is strictly enforced.

## License

The project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Disclaimer Notice

I have tested all functions in this library on all of my Samsung Multiroom speakers, and the worst that has happened is that speakers froze when receiving faulty calls, and needed a hard reset.
But I CAN’T guarantee that your speaker is compatible with this library, and you can’t hold me responsible if you brick your speaker when using this library.

## Versioning and Changelog

This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Credits

This project would not have been possible without, but not limited to, the following projects:

- [Samsung Wireless Audio Multiroom (WAM) Research](https://sites.google.com/view/samsungwirelessaudiomultiroom/other), Moosy Research
- [WAM_API_DOC](https://github.com/bacl/WAM_API_DOC), Bruno Lopes
- [com.samsung.wam](https://github.com/balmli/com.samsung.wam), Bjørnar Almli
- [Hubitat-Samsung-WiFi-Audio](https://github.com/DaveGut/HubitatActive/tree/master/SamsungMultiroom), David Gutheinz
- [Samsung Multiroom (WIP)](https://github.com/krygal/samsung_multiroom), Krystian Galutowski
- [SamsungNotify](https://github.com/moengiant/SamsungNotify), Moengiant

## Support the work

[![BuyMeCoffee][coffeebadge]][coffeelink]

[coffeelink]: https://www.buymeacoffee.com/76strixx
[coffeebadge]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
[pypibadge]: https://img.shields.io/pypi/dm/pywam?label=PyPi%20Downloads
[pypilink]: https://pypi.org/project/pywam/
