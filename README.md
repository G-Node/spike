Spikesorting Evaluation Website at the G-Node

This Django based web-application provides an evaluation backend for spike
sorting algorithms.

The concept is based on a set of benchmark dataset that are served by the
application. For these benchmark datasets the application will know the spike
sorting ground truth. Users can download and apply a spike sorting algorithm of
their choice to the datasets and upload the resulting spike train sets back to
the website. The uploded spike trainsets will be compared to the ground truth
and an error statistic will be build to compare different algorithms on the
same benchmark datasets. This is called an Evaluation.

Evaluations can be published, so that all users will be able to watch them and
compare all published Evaluations against each other and their own unpublished
Evaluations.

The service is thus providing means of 1) personal evaluation for developers of
spike sorting methods, 2) a tabular summary of relative performance of the
applied spike sorting algorithms and 3) should the remove the need for diverse
and singular toy dada sets in each and every spike sorting method publication.
