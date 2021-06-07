# pytheas 2021
New home for a very old project that accompanied a workshop-paper on Mobile Gaming.
Originally written for the long defunct Symbian S60 it might be useful on Rapsberry Pi as well.

Check the slides at https://de.slideshare.net/loppermann/mobile-gaming-2009-an-abstract-location-model
Details in the paper: https://dl.gi.de/handle/20.500.12116/31155


Original notes below
# Notes on the Pytheas alpha release

This is a first punt at releasing a Python reference implementation of my abstract location model. This is an alpha release, so things will change in the future.

The model behind this code evolved from my direct involvement in the creation of several location-based experiences while working at the Mixed Reality Lab at Nottingham University. They all used different technologies to somehow express a notion of location. A part of my PhD thesis then generalised those different requirements into the presented abstract location model. A paper about this model has also been presented at the Mobile Gaming 2009 workshop at the annual meeting of the German Gesellschaft fuer Informatik (GI 2009) in Luebeck.

This code abstracts that notion of location from any particular technology and allows for a more flexible definition of spaces that are intended to be meaningful for the intended location-based experience. The model currently support GPS, Wi-Fi and GSM cell ID.

This code works with Nokia Python for S60 and has been tested on N95 phones. This code has actually been used to create a location-based experience for cyclists called "The Sillitoe Trail". Findings from this experience (and from another experience called "Rider Spoke") have been presented at Mobile HCI 2009 in Bonn (Ubikequitous Computing: Designing Interactive Experiences for Cyclists.Rowland, Duncan; Flintham, Martin; Oppermann, Leif; Marshall, Joe; Chamberlain, Alan; Koleva, Boriana; Benford, Steve; Perez, Citlali. Full Paper)

Plans for the the future include making it work on other flavours of Python, including Windows and Maemo.

Please get in touch if this project is useful to you or if you want to have your say. This might actually accelerate future development

# Leif Oppermann, 25.09.2009
