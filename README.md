# PhotoBridge

Export your photos from a local directory to Apple Photos. 

## Rationale

This simple script was mostly built for my own personal use case. However, if you find it useful, feel free to use it! The 
reason it exists is summarised below:

**Situation**:  
You use iCloud photos, but you also use another service which synchronises photos to a local directory 
(such as NextCloud Photos, Immich, etc.).   

**Problem**:  
You sometimes take or add photos on a device which cannot synchronise with iCloud Photos (Android, Linux, etc.). Problem is, 
these photos do not make it to your iCloud Photos library.

**What you need**:  
You need a program which can scan your non-iCloud photos directory and upload any new photos to your iCloud library.

**What PhotoBridge does**:  
PhotoBridge scans the contents of a local directory and identifies new files (i.e. your new photos or images). It then adds 
those images to an Album in your iCloud Photos library. 

# Disclaimer

Although every care has been taken when developing PhotoBridge, there are two **important** things you should be aware of:

1. PhotoBridge is a simple utility I created for myself. I've released it to the public since others might find it useful, however,
   I've only tested this on my system. In the **highly unlikely** event that PhotoBridge destroys your wedding photos, the selfie 
   you took with Bono, or the video of baby's first steps, don't come crying to me. You should **ALWAYS** have a backup!
2. Unfortunately, the way that Apple Photos is built makes it quite difficult to interact with it programmatically.
   This means that, at any point, Apple may decide to change how Photos works, or disable programmatic interation
   entirely. This means that PhotoBridge can stop working without any prior notice!

Due to the above:

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Requirements

- PhotoBridge *only* runs on macOS systems. It uses AppleScript to interact directly with Apple Photos.
- PhotoBridge performs *one-way* synchronisation. It will upload new photos in a directory to iCloud Photos. Other solutions 
already exist which synchronise iCloud Photos to third-party services, such as the NextCloud app, the Immich app etc.
- PhotoBridge has only been tested in conjunction with NextCloud Photos (because that's how I use it). **In theory**, it should
also work with any folder-based photo service, but your mileage may vary.

## What It Does

The best way to understand what PhotoBridge does is via example. So, we'll use the following example for this section:

- This is Bob:

![](docs/bob.png)

- Bob is in Apple's walled garden. He has an iPhone, a Mac and an iCloud subscription. However, Bob also has some non-Apple stuff. 
So, he's installed the NextCloud app on his iPhone. 

![](docs/doc1.png)

- When Bob takes a photo on his iPhone, iCloud takes care of synchronising it to his other Apple devices. On the other hand,
the NextCloud app synchronises it to his non-Apple devices. Bob can see his photo regardless of which device he's using - 
this is good!

![](docs/doc2.png)

- There is, however, a problem. Due to Apple's restrictive practices, the NextCloud app on Bob's iPhone only does *one-way sync*. 
This means photos are uploaded from his iCloud photo library to NextCloud, but not the other way round; whihc means that 
when Bob takes a photo on his Android phone, it doesn't make it back to his iCloud photo library. He can only use his non-Apple 
devices to view that photo. This is bad 😢.

![](docs/doc3.png)

- Mama Bob didn't raise no fool, so Bob installs PhotoBridge on his Mac. He tells PhotoBridge where the NextCloud app on his Mac 
stores his NextCloud photos. PhotoBridge then scans this folder and builds a database. On every subsequent scan, PhotoBridge 
identifies new photos, and adds them to Bob's photo library in the desktop Apple Photos app. iCloud will then synchronise these
to the cloud, and they'll make their way to Bob's iPhone.

![](docs/doc4.png)

- Now, when Bob takes a photo with his Android phone, or adds a photo to his NextCloud library on a non-Apple device, it will be 
synchronised to all of his devices. Huzzah!

![](docs/doc5.png)

## Installing

The easiest way to install PhotoBridge is via [pipx](https://github.com/pypa/pipx#readme). If you don't have pipx installed,
you can easily install it via [HomeBrew](https://brew.sh):

```shell
brew install pipx
pipx ensurepath
```

Once that's done, run the following command to install PhotoBridge. This will install a ```photobridge``` command on your
system.

```shell
pipx install "git+https://github.com/keithvassallomt/photobridge.git"
```

## Usage

```
photobridge [-h] [--photos-folder PHOTOS_FOLDER] [--reset-database] [--dry-run] [--save-current-state]
```

Let's assume that, on your Mac, NextCloud is storing your photos in ```/Users/Bob/NextCloud/Photos```. Let's also assume that 
prior to using PhotoBridge, you were manually synchronising your NextCloud photos to your iCloud library.

The first thing you'll need to do is let PhotoBridge build its database of your existing photos. Otherwise, when you run 
PhotoBridge, it will re-upload all your NextCloud photos to iCloud, and that's probably not what you want. So, run this:

```shell
photobridge --photos-folder /Users/Bob/NextCloud/Photos --save-current-state 
```

This has now built the PhotoBridge database. Any photos added to the folder **from this point onwards** will be synchronised to 
Apple Photos when you run PhotoBridge. 

When you want to synchronise your photos, run PhotoBridge as follows:

```shell
photobridge --photos-folder /Users/Bob/NextCloud/Photos
```

## Super-Important Point

Since PhotoBridge relies on the photo's file name for synchornisation, you need to ensure that any app on your devices which is 
synchronising to your non-Apple cloud (such as NextCloud, Immich, etc.) is **preserving the original filenames used by iCloud***. 
Most apps allow you to do this. 

In NextCloud, for example:

**More** > **Settings** > **Advanced** > **Change filename mask** > **Maintain original filename**.

![](docs/doc6.jpeg)


## Options

The CLI has a few basic options you may find useful:

| Option                     | Description                                                                                                                                                            |  
|:---------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ```-h```                   | Display the usage instructions.                                                                                                                                        |
| ```--save-current-state``` | Save the current folder state. Very useful the first time you run PhotoBridge so existing photos aren't re-uploaded. Use with ```--photos-folder```.                   |
| ```--reset-database```     | Reset the internal database so all 'known' photos are forgotten. Useful if you screw something up!                                                                     |
| ```--photos-folder```      | Add the path to where your non-Apple (e.g. NextCloud) photos are stored. This is the folder which will be synchronised with Apple Photos.                              |
| ```--dry-run```            | Use this to simulate a synchronisation without actually moving any data. Useful to confirm what PhotoBridge would do with your photos. Use with ```--photos-folder```. |

## See Also

Happy with PhotoBridge? How about also synchronising your Apple Reminders and Notes to non-Apple devices? Check out [TaskBridge](https://taskbridge.app).