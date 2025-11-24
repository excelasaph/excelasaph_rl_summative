# Game Sound Assets

To enable audio in the game, please add the following MP3 files to the `public/sounds/` directory.
You can find free sound effects on sites like [Freesound.org](https://freesound.org/) or [Mixkit](https://mixkit.co/free-sound-effects/).

## Required Files

| Filename | Description |
|----------|-------------|
| `city_ambient.mp3` | Background city noise (traffic, wind) |
| `engine_idle.mp3` | Bus engine idling loop |
| `engine_rev.mp3` | Engine revving up / accelerating |
| `brakes.mp3` | Squeaky brake sound |
| `door_open.mp3` | Bus door opening (pneumatic hiss) |
| `door_close.mp3` | Bus door closing |
| `coin.mp3` | "Ching" sound for collecting money/passengers |
| `shuffle.mp3` | Crowd shuffling/footsteps for dropoff |
| `horn.mp3` | Car horn (used when fined) |
| `whistle.mp3` | Police whistle |
| `beep.mp3` | Traffic light beep or warning |
| `success.mp3` | Level complete / high reward sound |
| `fail.mp3` | Negative sound (fine/crash) |
| `click.mp3` | UI button click |

## Directory Structure

```
3d-render/
  public/
    sounds/
      city_ambient.mp3
      engine_idle.mp3
      ...
```

Once these files are added, the game will automatically load and play them.
