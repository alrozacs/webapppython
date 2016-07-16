from numpy import shape, zeros
from math import exp, log, sqrt
from scipy.stats import norm

# import scipy.stats.norm to calculate cdf function

# k - strike price
# s - underlying price
# r - risk-free rate
# sigma - volatility
# t - time to option exercise date
# q - dividend yield
# flag -- string input to check if it's call -- input required: "call"
def blsprice(k, s, r, sigma, t, q, flag):
    d1 = (log(s/k)+(r - q + (sigma**2)/2)*t)/(sigma*sqrt(t))
    d2 = d1 - sigma*sqrt(t)
    if flag == "call":
        price = s*norm.cdf(d1)-k*norm.cdf(d2)*exp(-r*t)
    else:
        price = k*norm.cdf(-d2)-s*norm.cdf(-d1)*exp(-r*t)
    return price

# function is_number:
# input: variable to check if it is float type
# output: Boolean(True of False) if float type, then True

def is_number(variable):
    try:
        if type(float(variable)) == float:
            return True
    except Exception:
        return False

# function text2data_col:
# input: text file with 2 column data
# **** (input file is already open.
# every time you run this function
# you should close the file (f.close()) )
# output: matrix with data in columns
# example output: [[1,2,3,4], [3,2,3,5]]

def text2data_col(f):
    firstcolumn = []
    secondcolumn = []
    for row in f.readlines():
        Data = row.split()
        try:
            if is_number(Data[0]) and is_number(Data[1]):
                firstcolumn.append(float(Data[0]))
                secondcolumn.append(float(Data[1]))
        except IndexError:
            break
    datamat = [firstcolumn, secondcolumn]
    return datamat

# function text2data_row:
# input: text file with 2 column data
# **** (input file is already open.
# every time you run this function
# you should close the file (f.close()) )
# output: matrix with data in rows
# example output: [[1,2], [3,4], [3,2], [3,5]]

def text2data_row(file):
    datamat = []
    for row in file.readlines():
        data = row.split()
        eachrow = []
        try:
            if is_number(data[0]) and is_number(data[1]):
                eachrow.append(float(data[0]))
                eachrow.append(float(data[1]))
                datamat.append(eachrow)
        except IndexError:
            break
    return datamat

# function bootstrapping_row:
# input: swap rates matrix from text2data_row
# output: spot rates with data in rows

def bootstrapping_row(swap_structure):
    t=swap_structure[1][0]-swap_structure[0][0]
    spot_structure = zeros(shape(swap_structure))
    spot_structure[0][1] = swap_structure[0][1]
    for k in range(len(swap_structure)):
        spot_structure[k][0]=swap_structure[k][0]
    for i in range(1, shape(spot_structure)[0]):
        summation = 0
        for j in range(i):
            summation += swap_structure[i][1]*t*exp(-spot_structure[j][1]*spot_structure[j][0])
        spot_structure[i][1] = (-1/spot_structure[i][0])*log((1-summation)/(1+t*swap_structure[i][1]))
    return spot_structure

# function bootstrapping_col:
# input: swap rates matrix from text2data_col
# output: spot rates with data in columns

def bootstrapping_col(swap_structure):
    t=swap_structure[0][1]-swap_structure[0][0]
    spot_structure = zeros(shape(swap_structure))
    spot_structure[1][0] = swap_structure[1][0]
    for k in range(len(swap_structure[0])):
        spot_structure[0][k]=swap_structure[0][k]
    for i in range(1, len(spot_structure[0])):
        summation = 0
        for j in range(i):
            summation += swap_structure[1][i]*t*exp(-spot_structure[1][j]*spot_structure[0][j])
        spot_structure[1][i] = (-1/spot_structure[0][i])*log((1-summation)/(1+t*swap_structure[1][i]))
    return spot_structure

'''
def is_row_matrix(matrix):
    if shape(matrix)[1] == 2:
        is_row = True
    else:
        is_row = False
    return is_row

def is_col_matrix(matrix):
    if shape(matrix)[0] == 2:
        is_col = True
    else:
        is_col = False
    return is_col
'''