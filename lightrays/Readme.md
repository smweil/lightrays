# LightRays - Light Painting in Python

A [L.A.S.E.R Tag](http://www.graffitiresearchlab.com/blog/projects/laser-tag/)inspired light graffiti application written in python with lots of inspiration from [pyimagesearch](www.pyimagesearch.com).


## Overview
This program tracks a laser pointer on a surface and creates a trail of light behind it via a projector pointed at the same surface.

It detects the laser using OpenCV's color filtering. To detect a laser we setup upper and lower `HSV` boundaries which are stored in `config.py`. We can also do this on the fly by hitting the `f` key at the camera setup screen.



## Quick Run
Run `LightRays.py`:
  * The first screen is the `canvas` -- it should be projected on the target. Use `u`,`o` to stretch/shrink the canvas and `q`,`e` to resize the image (add pixels).
    * Note: You can use `a,s,d,w` and `j,k,l,i` keys to resize the image/canvas without preserving the aspect ratio as well.
  * Point your camera at the projected screen. If y

## Dependencies:
  * `OpenCV` (pip install opencv-python)
  * `numpy`
  * `imutils` (pip install imutils)

`placeholder` words _italics_ more words

## List!

  * List 1
  * :penguin: Penguin
  * More `command text` good description

## Using

More stuff here!
