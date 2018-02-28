# 1.Install caffe
1.1 Using WayBack Mechine to get the old version of caffe website: http://web.archive.org/web/20150326045234/http://caffe.berkeleyvision.org:80/installation.html#hardware

Following caffe installation to install cuda 7.0:

install openGL Library. After 'rebot', I ccould not log in to Ubuntu. After searching some information, I knew it is a very common error. Alongside with Nvidia drivers it also installs lib-mesa which overrides the openGL files installed by previous Nvidia driver installation, which causes Ubuntu GUI to crash.

There are two methods to try. As for the first one, someone suggests to install cuda directly. It will report some errors because there is no GPU in this virtual mechine. While others suggest to install the old version of openGL Library. It seems to work well at the beginning but fail to install caffe.

I checked the official document. I think we should have a GPU first. Without GPU, there is no need to install cuda and it will cause some errors. However, caffe needs cuda.

So I believe when we get the new computer back. I am confident to follow the offical instructions online to install them.

# 2.Change current codes to the new version

It seems to work well. I modify the codes to meet the requirements of new Caffe version. There used to be 75 errors. Now there only are 8 errors.
