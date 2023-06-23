Narwhals Project
================

This is the repository containing the source codes with which we analysed the given data.

* `classify.ipynb` does the calculations for a single image given an absolute path, while `classify.py` automates this process and saves the data into the `albedo_calculations.csv`.
* `clustering.ipynb` is our attempt at trying the k-means clustering algorithm.
* `WriteExif.py` writes the data taken from the `total_interval_sec.csv` into the metadata of the images, while `GetExif.py` returns the exif data of a given image
* Lastly, `main.py` is the program that ran on the ISS. 
