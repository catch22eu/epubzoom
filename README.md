# epubzoom
epubzoom is a utility for correcting image sizes in epub files.

The tool parses an epub file and is able find references to images, their original dimensions, and has a default (and customizable) set of parameters that are used to alter the display size of these images. 

The tool is currently in development, which should be able to alter the majority of epub files and the images contained within them. There are multiple methods to reference images in the epub standard, as well as multiple document structures that can be used. Currently implemented are xhtml 'img' references. The size of the referenced images are determined, and based on a set of parameters style dimensions are determined that are relative to the display size (e.g. the ereader), or character size. A distinction is therefore made between small images that are relative to the character size of the text, which are for instance scanned formulae, and larger images. The input parameters are:
- the book's original display size in pixels
- the threshold when to regard an image size to be regarded relative to text size or page size
- zoomfactors for both image types (relative to text or page)

### Prerequisites

PDFaudit is written in Python, and uses Python3 code. For windows and OSx, see https://www.python.org/downloads/. For Linux, Python3 may already have been installed or can be retrieved using your package manager and native repositories. 

Following additional library is used: 
- imagesize. 

For a Debian based system, this library is available in the Debian repositories as python3-images.deb.

### Installing and Using

Simply download the github code to your computer, and running it.

Using the python command, explicitly using python3:
```
python3 epubzoom.py inputfile.epub
```

On recent versions of Windows, the following may work as well:
```
epubzoom.py inputfile.epub
```

To be able to do the same on Linux, the script has to be made executable first:
```
chmod u+x epubzoom.py
```
before the script can be executed like:
```
epubzom.py inputfile.epub
```

### TODO list
1) Make input parameters accessible through command-line
2) Refactoring and further testing

## Version History

#### v0.2: 27 November 2021
##### New:
- Removed the css parser, as it was not used


#### v0.1 25 November 2021
First version


## License

epubzoom Copyright (C) 2021 Joseph Heller

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.





