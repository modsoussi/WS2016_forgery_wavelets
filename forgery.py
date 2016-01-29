''' A program that detects forged handwriting. This is still merely a prototype.
I'm implementing the algorithm used by Beverly Lyle and Caroline Young.
(c) 2016. modsoussi.

    Comments:
        + To multiply matrices, it's better to use the np.dot method, instead of '__mul__' in np.array. '__mul__' doesn't look
        like it's doing the right thing.
            > np.dot(a,b) if a.b and (b,a) if b.a.
        + Useful links:
            > http://docs.scipy.org/doc/scipy/reference/signal.html#filtering
            > http://wavelets.pybytes.com/wavelet/db1/
            > http://pywavelets.readthedocs.org/en/latest/ref/index.html
            > http://docs.scipy.org/doc/numpy/reference/
            > http://stackoverflow.com/questions/8553573/histogram-matplotlib-from-arrays\
            > http://matplotlib.org/1.3.1/index.html
        + In numpy, to get the transpose of an np.array, just do np.array.T.
        + Because I couldn't implement the filtering using bivariate filters, I followed a different approach that applies
        Daubechies' discrete wavelet decomposition multiple times.
'''

from PIL import Image
import numpy as np
import scipy as sp
import pywt
import matplotlib.pyplot as plt
import sys
import string

''' This method ensures the matrix passed in has dimensions that are multiples of 256. 
Returns a new matrix with the correct dimenstions '''
def _resize_for_analysis(m):
    print "[***] _resizing ... sides of square need to be powers of 2"
    h,w = m.shape # w for width, h for height
    w_limit = w/256 * 256
    h_limit = h/256 * 256
    if((w_limit != 0) and (h_limit != 0)):
        return np.array(m[:h_limit, :w_limit], np.int32)
    return m

''' This method does the filtering, returns the wavelet coefficients matrix obtained after applying
Daubechies' wavelet decomposition iteratively. '''
def _filter(m):
    print "[***] _filtering ..."
    cA, cD = pywt.dwt(m, 'db6', axis=1)
    m = np.concatenate((cA,cD), axis=0)
    cA, cD = pywt.dwt(m, 'db6')
    m = np.concatenate((cA,cD), axis=1)
    height, width = m.shape
    m = _resize_for_analysis(m)
    height /= 2
    width /= 2
    m_1 = np.array(m[:height, :width])
    cA_1, cD_1 = pywt.dwt(m_1, 'db6', axis = 0)
    m_1 = np.concatenate((cA_1,cD_1), axis = 1)
    cA_1, cD_1 = pywt.dwt(m_1, 'db6')
    m_1 = np.concatenate((cA_1,cD_1), axis = 0)
    m_1 = np.array(m_1[:height, :width])
    m[:height, :width] = m_1
    return m
    
''' The main method. Here we open the image, save it as portable greymap, then open the portable greymap version
and convert it to black and white.'''
def main(img_path):
    im = Image.open("images/"+img_path)
    name, extension = string.split(img_path,'.')
    im.save("images/%s.pgm" % (name))
    pgm_im = Image.open("images/%s.pgm" % (name))
    pgm_im_bw = pgm_im.convert("L")
    im_data = list(pgm_im_bw.getdata())

    width, height = pgm_im_bw.size
    print "Width = %d, height = %d" % (width, height)

    ''' Initializing numpy heightxwidth array, so I can perform matrix operations using numpy '''
    img_matrix = np.array(im_data, np.int32).reshape(height, width)

    img_matrix = _resize_for_analysis(img_matrix)
    height, width = img_matrix.shape
    print "Width = %d, height = %d" % (width, height)
    
    new_im_matrix = _filter(img_matrix)
    print "new_im_matrix.shape = ", new_im_matrix.shape
    
    ''' Plotting histogram based on data in new_im_matrix '''
    new_im_array = new_im_matrix.flatten()
    plt.hist(new_im_array, bins=250)
    print max(new_im_array[200:1500])
    #plt.axis([200,1500,0,2000])
    plt.show()
    
if __name__ == "__main__":
    n_args = len(sys.argv)
    if(n_args < 2):
        print "Error: No image supplised.\nUsage:\n\t-Please supply one image to run the program on.\n"
        exit(1)
    main(sys.argv[1])