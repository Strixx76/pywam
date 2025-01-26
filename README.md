# pywam

[![License][licensebadge]][licenselink]
[![PyPi Downloads][pypibadge]][pypilink]

[![Buy Me A Coffee][coffeebadge]][coffeelink]
[![Ko-fi][kofibadge]][kofilink]
[![Paypal][paypalbadge]][paypallink]
[![GitHub Sponsors][githubsponsorsbadge]][githubsponsorslink]

pywam is an fast and lightweight python asyncio library without external dependencies for communicating with Samsung Wireless Audio (R) speakers (WAM). It was developed to be used for integrating the speakers in [Home Assistant](https://www.home-assistant.io/) with the [Samsung Wireless Audio Integration](https://github.com/Strixx76/samsungwam)

> [!NOTE]
> Latest version is 0.1.0rc6 and will stay versioned as release candidate. This is because of small mistake with dependencies in the first release of the Samsung Wireless Audio. So next none beta or rc release of this library will be either 0.2 or 1.0, there will be no 0.1 release.

## Features

- Control Samsung Multiroom speakers.
- Keep track of the state of Samsung Multiroom speakers.

## Limitations

The `SetUrlPlayback` API used to get the speakers playing url streams is only partially implemented in the speakers. I have found information that not all speakers accept it, and the one that does will only play the url. The speaker will not report that it is playing a url. This means that as soon as the speakers is asked for current state it will report that it is not playing anything, which this library will pick up and believe to be true.

## Installation

```bash
pip install pywam
```

## Usage

Set the speaker volume to 50% with python context manager:

```python
from pywam.speaker import Speaker

async with Speaker('192.168.1.100') as speaker:
    await speaker.update()
    await speaker.set_volume(50)
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

Example of playing a url stream:

```python
from pywam.lib.url import UrlMediaItem

item = UrlMediaItem('http://live-bauerse-fm.sharp-stream.com/retrofm_mp3')
await speaker.play_url(item)
```

Example of group handling:

```python
from pywam.speaker import Speaker

kitchen = Speaker('192.168.1.50')
await kitchen.connect()
await kitchen.update()

bedroom = Speaker('192.168.1.51')
await bedroom.connect()
await bedroom.update()

bathroom = Speaker('192.168.1.52')
await bathroom.connect()
await bathroom.update()

# Group bathroom with kitchen as master
await kitchen.group([], [bathroom])

# Add bedroom to the group
await kitchen.group([bathroom], [bathroom, bedroom])

# Remove bathroom from group
await kitchen.group([bathroom, bedroom], [bedroom])

# Ungroup
await kitchen.group([bedroom], [])
```

Get notifications about speakers state changes:

```python
from pywam.speaker import Speaker

def state_receiver(event):
    print(event)

speaker = Speaker('192.168.1.150')
speaker.events.register_subscriber(state_receiver, 2)
await speaker.connect()
await speaker.update()
```

For more examples please check the [Samsung Wireless Audio Integration](https://github.com/Strixx76/samsungwam)

## Contribute

- Find a bug or something to improve? Please file a issue at https://github.com/Strixx76/pywam/issues
- Want to contribute with code? Check the source at https://github.com/Strixx76/pywam

## Roadmap

- There are some TODO's in the source that should be fixed.
- Better workaround for play_url to show correct state when url streams are played.
- I would also like to change all the API keys and values strings in both the event receiver and the state machine to string enums.
- Make the code less complex.
- Add more API calls.

## Style guide

PEP8 and Google styled PEP257.
But none of them is strictly enforced.

## License

The project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Disclaimer Notice

I have tested all functions in this library on all of my Samsung Multiroom speakers, and the worst that has happened is that speakers froze when receiving faulty calls. A simple power cycle would solve it.
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

If you find this library useful please consider a small donation to show your appreciation.

[![Buy Me A Coffee][coffeebutton]][coffeelink]
[![Ko-fi][kofibutton]][kofilink]
[![Paypal][paypalbutton]][paypallink]
[![GitHub Sponsors][githubsponsorsbutton]][githubsponsorslink]

[licensebadge]: https://img.shields.io/badge/licens-MIT-41BDF5.svg
[licenselink]: LICENSE.txt
[pypibadge]: https://img.shields.io/pypi/dm/pywam?label=PyPi%20Downloads
[pypilink]: https://pypi.org/project/pywam/
[coffeelink]: https://www.buymeacoffee.com/76strixx
[coffeebadge]: https://img.shields.io/badge/Buy_Me_A_Coffee-Donate-ffdc02?logo=buymeacoffee&logoColor=white
[coffeebutton]: ./.github/assets/coffee.png
[kofilink]: https://ko-fi.com/strixx76
[kofibadge]: https://img.shields.io/badge/Ko--fi-Donate-ff5a16?logo=kofi&logoColor=white
[kofibutton]: ./.github/assets/ko-fi.png
[paypallink]: https://www.paypal.com/donate/?hosted_button_id=XAWX4FG9FJW6Q
[paypalbadge]: https://img.shields.io/badge/Paypal-Donate-0070ba?logo=paypal&logoColor=white
[paypalbutton]: ./.github/assets/paypal.png
[githubsponsorslink]: https://github.com/sponsors/Strixx76
[githubsponsorsbadge]: https://img.shields.io/badge/GitHub_Sponsors-Donate-ea4aaa?logo=github&logoColor=white
[githubsponsorsbutton]: ./.github/assets/github.png
