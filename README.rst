======
LensMe
======

LensMe is a small python software meant for demonstrating how gravitational lensing works.
LensMe allows to capture the videoinput from a webcam and shows the image as it it would appear when lensed by a NFW halo.
LensMe also features a simple GUI.
So far LensMe is only fully supported on Linux systems.


Installation
============

To install LensMe type::

    git clone git@github.com:DZuercher/LensMe.git  
    cd LensMe
    python setup.py install

in your terminal. 

Note: For wx to work you need to install the GTK3 development tools (on Ubuntu: sudo apt install libgtk-3-dev).

Usage
=====

Just type:: 

    lensme 
    
in your terminal and you are ready to go.

.. image:: lensme.png
    :width: 600px


Credits
=======

The nfw_halo_lens class is heavily based on `gravity-game <https://github.com/mdlreyes/gravity-game>`_