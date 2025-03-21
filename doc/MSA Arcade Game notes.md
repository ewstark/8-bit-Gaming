# MSA Arcade Game

## Architecture

See the file "MSA Arcade Game.drawio" for a diagram of the system architecture.

In abstraction, the system is formed by three primary components: the **Game Engine** which executes the main game loop, the **Graphics Engine** which renders each scene of the animated game, and the **Audio Engine** which asynchronously manages, mixes, and produces game sounds and background music.

These three primary components have equivalent PyGame components within the prototype PC system.  These PyGame components can be mapped, via their APIs, to the corresponding hardware components using a bridge device.


## Abstract Processing Overview

### Game Loop
 * get time delta
 * get user input
   * upon player quit:
     * exit Game Loop
 * calculate asset updates
   * write new asset data to current **Game Data RAM** page
   * upon events (collisions, enemy spawn/death, player attack, etc.):
     * start/stop sounds, lights, or change background music
   * upon game-over condition (e.g., final player death):
     * exit Game Loop
 * flip **Game Data RAM** page
   * _optional:_ confirm previous page was fully consumed by **Graphics Engine**

### Graphics Engine
 * upon **Game Data RAM** flip:
   * render screen from new data
 * _optional:_ upon timer:
   * update animations

### Audio Engine
 * upon timer tick:
   * calculate and move audio data to output buffer
 * upon register write:
   * read reg, process event
 * upon register read:
   * write reg
