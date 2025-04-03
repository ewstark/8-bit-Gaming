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

## Mock Game: **Canary Crush**

As a part of learning all aspects of the gaming ecosystem, I'm creating my own example game called **Canary Crush**. It is in the style of early-1980's free-standing arcade games. In particular, I'm shamelessly modeling the game after Pengo. It is a simple game that should be easy to replicate, and it provides a means for testing interactions with various components such as the game loop, the user interface, 2D pixel art (sprites), and asynchronous audio event processing.

**Canary Crush** is targeted to 320x240 graphics in landscape orientation with 4 bits-per-pixel (16-color) palette-based colors.

    Using 16x16 cells, screen grid is 20 wide by 15 high.
   
                            1 1 1 1 1 1 1 1 1 1 2
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
       +-----------------------------------------+
     0 |w w w w w w w w w w w w w w w  Game Name |
     1 |w                           w            |
     2 |w                           w  Game--Art |
     3 |w                           w  Game--Art |
     4 |w                           w  Game--Art |
     5 |w                           w  Game--Art |
     6 |w                           w            |
     7 |w                           w P1: 1234567|
     8 |w                           w #lvl #lives|
     9 |w                           w            |
    10 |w                           w P2: 1234567|
    11 |w                           w #lvl #lives|
    12 |w                           w            |
    13 |w                           w MSA Arcade |
    14 |w w w w w w w w w w w w w w w  (c) 1982  |
       +-----------------------------------------+

You are a canary stuck in a mine! A maze of rocks surrounds you. You can slide the rocks if nothing is behind them. You can crush rocks that can't move. Gas clouds are chasing you. Avoid or destroy them by smashing them with rocks. They can also be stunned when player slams a common wall. Stunned clouds move slowly for a period of time.

Within the rocks are parts of the ventilation shaft. These can be slid but not broken. Align them to automatically disperse all gas clouds. Destroy all clouds or repair the ventilation shaft to complete the level. The further you descend into the mine, the gas clouds will become more numerous, quick, and aggressive.
