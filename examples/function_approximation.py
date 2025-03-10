from ZAVLAB import error_calculation as er
import numpy as np
from lmfit import Parameters

x = np.linspace(0, 10, 10)
k = 2
b = 1.06
y = k * x + b
data = [[x], [y]]
fitParams = Parameters()
fitParams.add("k", value=1, vary=True)
fitParams.add("b", value=0, vary=True)

res = er.approximate_params(data, fitParams, er.linear_model, verbose=True)
print(res["k"].value, (k - res["k"].value) / k * 100) #here we can see that approximated value is close to inital (error of determining param is less than 2*10^-5 %)
print(res["b"].value, np.abs(b - res["b"].value) / b * 100) #here we can see that approximated value is close to inital (error of determining param is less than 2*10^-4 %)