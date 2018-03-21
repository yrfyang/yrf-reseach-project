# Update SVM methods

1 get all features (including hog) from the images [process-clipping](https://github.com/yrfyang/yrf-reseach-project/blob/master/code/process-clipping.py)

2 get specific hog from the images [hog](https://github.com/yrfyang/yrf-reseach-project/blob/master/code/hog.py)

3 divide the data into positive and negative [data-division](https://github.com/yrfyang/yrf-reseach-project/blob/master/code/data-division.py)

# some results of SVM

[dataset](https://github.com/yrfyang/yrf-reseach-project/blob/master/data_set/data_setdata.txt)

different kenerals:
SVM use hyperplanes to perform classification. While performing classifications using SVM there are 2 types of SVM

C SVM
Nu SVM

C and nu are regularisation parameters which help implement a penalty on the misclassifications that are performed while separating the classes. Thus helps in improving the accuracy of the output.

C ranges from 0 to infinity and can be a bit hard to estimate and use. A modification to this was the introduction of nu which operates between 0-1 and represents the lower and upper bound on the number of examples that are support vectors and that lie on the wrong side of the hyperplane.

Both have a comparative similar classification power, but the nu- SVM has been harder to optimise
