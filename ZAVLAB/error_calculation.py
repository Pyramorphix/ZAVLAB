import numpy as np
import math
from scipy.optimize import minimize
from lmfit import Parameters, minimize, fit_report
import types
"""
This part was made by Arina with help of Stepan Shipilov. 
For more inforamtion about calculating errors you can visit his github: https://github.com/stive-shipilov
Again, as in graph_plotting, in this file, all "inspiration" comments are just my attempt
to make this work a little more lively!

Also, if you find any mistakes DON'T bother yourself to email us to report an issue. 
Now, let's go!
"""


start_of_err_msg = "Just put data from data_structure array! It will be a lot simplier for everyone. The structure of input data which is expected to be is [[x, xerr], [y, yerr]] (where x_err and y_err are not compulsory if they are not asked for this func). IMPORTANT NOTE: these functions DON'T work for 3D data type."

def __check_of_data_with_x_xerr_y_yerr(data):
    global start_of_err_msg
    if len(data) != 2:
        raise ValueError(start_of_err_msg + "Input data has to have two elenments each of them has two have on the zero position x(y) array.")
    if not isinstance(data[0], list) or not (len(data[1]) == 2):
        raise TypeError(start_of_err_msg + " First element of data should be a list with x and x_err.")
    if not isinstance(data[1], list) or not (len(data[1]) == 2):
        raise TypeError(start_of_err_msg + " First element of data should be a list with y and y_err.")
    if not isinstance(data[0][0], np.ndarray):
        raise TypeError(start_of_err_msg + " X element should numpy array.")
    if not isinstance(data[0][1], np.ndarray):
        raise TypeError(start_of_err_msg + " x_err element should numpy array.")
    if not isinstance(data[1][0], np.ndarray):
        raise TypeError(start_of_err_msg + " Y element should numpy array.")
    if not isinstance(data[1][1], np.ndarray):
        raise TypeError(start_of_err_msg + " y_err element should numpy array.")
def __check_of_data_with_x_y_yerr(data):
    global start_of_err_msg
    if len(data) != 2:
        raise ValueError(start_of_err_msg + "Input data has to have two elenments each of them has two have on the zero position x(y) array.")
    if not isinstance(data[0], list):
        raise TypeError(start_of_err_msg + " First element of data should be a list with x (and x_err).")
    if not isinstance(data[1], list) or not (len(data[1]) == 2):
        raise TypeError(start_of_err_msg + " First element of data should be a list with y and y_err.")
    if not isinstance(data[0][0], np.ndarray):
        raise TypeError(start_of_err_msg + " X element should numpy array.")
    if not isinstance(data[1][0], np.ndarray):
        raise TypeError(start_of_err_msg + " Y element should numpy array.")
    if not isinstance(data[1][1], np.ndarray):
        raise TypeError(start_of_err_msg + " y_err element should numpy array.")
def __check_of_data_with_x_y(data):
    global start_of_err_msg
    if len(data) != 2:
        raise ValueError(start_of_err_msg + "Input data has to have two elenments each of them has two have on the zero position x(y) array.")
    if not isinstance(data[0], list):
        raise TypeError(start_of_err_msg + " First element of data should be a list with x (and x_err).")
    if not isinstance(data[1], list):
        raise TypeError(start_of_err_msg + " First element of data should be a list with y (and y_err).")
    if not isinstance(data[0][0], np.ndarray):
        raise TypeError(start_of_err_msg + " X element should numpy array.")
    if not isinstance(data[1][0], np.ndarray):
        raise TypeError(start_of_err_msg + " Y element should numpy array.")
        

def mnk(data, use_systematic = False, systematic_eror = None):
    try:
        __check_of_data_with_x_y(data)
    except (ValueError, TypeError) as e:
        print(f"Error is {e}")
        
    data_x = data[0][0]
    data_y = data[1][0]
    slope = (np.mean(data_x*data_y) - np.mean(data_x*np.mean(data_y)))/(np.mean(data_x**2) - (np.mean(data_x))**2)
    slope_sig = np.sqrt((1/(data_x.shape[0] - 1))*(np.sum((data_y - np.mean(data_y))**2)/np.sum((data_x - np.mean(data_x))**2) - slope**2))
    if use_systematic and systematic_eror is not None:
        av_sys_error = np.mean(systematic_eror)
        slope_sig = math.sqrt(av_sys_error**2 + slope_sig**2)
    b = np.mean(data_y) - slope * np.mean(data_x)
    b_sig = slope_sig * np.sqrt(np.mean(data_x ** 2))
    return slope, b, slope_sig, b_sig


def chi2_regression_1d(data):
    try:
        __check_of_data_with_x_y_yerr(data)
    except (ValueError, TypeError) as e:
        print(f"Error is {e}")
        
    data_x = data[0][0]
    data_y = data[1][0]
    y_err = data[1][1]
    # Масштабируем данные
    x_scale = np.max(data_x)
    y_scale = np.max(data_y)

    data_x_scaled = data_x / x_scale
    data_y_scaled = data_y / y_scale
    y_err_scaled = y_err / y_scale

    def chi2_d1(coeffs):
        a, b = coeffs
        model = a * data_x_scaled + b
        return np.sum(((data_y_scaled - model) / y_err_scaled) ** 2)
    
    initial_coeffs = [1, 0]

    # Используем метод оптимизации с поддержкой Гессе
    result = minimize(chi2_d1, initial_coeffs, method='BFGS')

    slope_scaled, intercept_scaled = result.x
    chi2_value = result.fun

    # Проверяем доступность обратной матрицы Гессе
    if hasattr(result, 'hess_inv'):
        hessian_inv = result.hess_inv  # Обратная матрица Гессе
        slope_err_scaled = math.sqrt(hessian_inv[0, 0])
        intercept_err_scaled = math.sqrt(hessian_inv[1, 1])
    else:
        slope_err_scaled = None
        intercept_err_scaled = None

    # Пересчитываем коэффициенты и ошибки в исходный масштаб
    slope = slope_scaled * (y_scale / x_scale)
    intercept = intercept_scaled * y_scale
    slope_err = slope_err_scaled * (y_scale / x_scale) if slope_err_scaled is not None else None
    intercept_err = intercept_err_scaled * y_scale if intercept_err_scaled is not None else None

    return slope, intercept, slope_err, intercept_err, chi2_value

def chi2_regression_2d(data):
    try:
        __check_of_data_with_x_xerr_y_yerr(data)
    except (ValueError, TypeError) as e:
        print(f"Error is {e}")
        
    data_x = data[0][0]
    x_err = data[0][1]
    data_y = data[1][0]
    y_err = data[1][1]

    # Масштабируем данные
    x_scale = np.max(np.abs(data_x))
    y_scale = np.max(np.abs(data_y))

    data_x_scaled = data_x / x_scale
    data_y_scaled = data_y / y_scale
    y_err_scaled = y_err / y_scale
    x_err_scaled = x_err / x_scale

    # Определяем функцию для минимизации
    def chi2_d2(coeffs):
        a, b = coeffs
        model = a * data_x_scaled + b
        sigma_total = np.sqrt(y_err_scaled**2 + (a * x_err_scaled)**2) + 1e-10
        chi2 = np.sum(((data_y_scaled - model) / sigma_total) ** 2)
        regularization = 1e-5 * (a**2 + b**2)  # Регуляризация
        return chi2 + regularization

    # Улучшаем начальную оценку коэффициентов
    coeffs_initial = np.polyfit(data_x_scaled, data_y_scaled, 1)
    initial_coeffs = [coeffs_initial[0], coeffs_initial[1]]

    # Оптимизация
    result = minimize(chi2_d2, initial_coeffs, method='Powell')  # Используем метод Powell

    # Проверка успешности оптимизации
    if not result.success:
        raise RuntimeError("Оптимизация не удалась: " + result.message)

    slope_scaled, intercept_scaled = result.x
    chi2_value = result.fun

    # Определяем весовую функцию
    def weights(a, x_err, y_err):
        return 1 / (y_err**2 + (a * x_err)**2 + 1e-10)

    def weighted_mean(x, w):
        return np.sum(w * x) / np.sum(w)

    def slope_error(x, y, x_err, y_err, a):
        w = weights(a, x_err, y_err)
        x_mean = weighted_mean(x, w)
        sigma_a2 = 1 / np.sum(w * (x - x_mean) ** 2)
        return np.sqrt(sigma_a2)

    def intercept_error(x, y, x_err, y_err, a, b):
        w = weights(a, x_err, y_err)
        x_mean = weighted_mean(x, w)
        sigma_b2 = 1 / np.sum(w) + (x_mean ** 2) / np.sum(w * (x - x_mean) ** 2)
        return np.sqrt(sigma_b2)

    slope_err_scaled = slope_error(data_x_scaled, data_y_scaled, x_err_scaled, y_err_scaled, slope_scaled)
    intercept_err_scaled = intercept_error(data_x_scaled, data_y_scaled, x_err_scaled, y_err_scaled, slope_scaled, intercept_scaled)

    # Пересчёт коэффициентов и ошибок в исходный масштаб
    slope = slope_scaled * (y_scale / x_scale)
    intercept = intercept_scaled * y_scale
    slope_err = slope_err_scaled * (y_scale / x_scale) if slope_err_scaled is not None else None
    intercept_err = intercept_err_scaled * y_scale if intercept_err_scaled is not None else None

    return slope, intercept, slope_err, intercept_err, chi2_value

def monte_carlo_linear_model(data, count_iter = 100):
    try:
        __check_of_data_with_x_xerr_y_yerr(data)
    except (ValueError, TypeError) as e:
        print(f"Error is {e}")
    data_x = data[0][0]
    x_err = data[0][1]
    data_y = data[1][0]
    y_err = data[1][1]    
    
    a_values = [1]
    b_values = [0]
    
    x_scale = np.max(data_x)
    y_scale = np.max(data_y)

    data_x = data_x / x_scale
    data_y = data_y / y_scale
    y_err = y_err / y_scale
    x_err = x_err / x_scale


    residuals = data_y - (a_values[-1] * data_x + b_values[-1])
    rmse = np.sqrt(np.sum(residuals**2)/data_x.shape[0])
    # Цикл Монте-Карло
    for i in range(count_iter):
        # Генерация данных с учетом погрешностей
        x_sample = data_x + np.random.normal(0, x_err)
        y_sample = data_y + np.random.normal(0, rmse)
        
        try:
            result = chi2_regression_1d(x_sample, y_sample, y_err)
            a_values.append(result[0])
            b_values.append(result[1])
        except RuntimeError:
            # Если подгонка не удалась, пропускаем итерацию
            continue

    # Оценка параметров и их неопределенностей
    slope = np.mean(a_values)
    intercept = np.mean(b_values)
    slope_err = np.std(a_values)
    intercept_err = np.std(b_values)

    slope = slope * (y_scale / x_scale)
    intercept = intercept * y_scale
    slope_err = slope_err * (y_scale / x_scale) if slope_err is not None else None
    intercept_err = intercept_err * y_scale if intercept_err is not None else None
    return slope, intercept, slope_err, intercept_err


def bootstrap_linear(data ,count_iter=100):
    try:
        __check_of_data_with_x_xerr_y_yerr(data)
    except (ValueError, TypeError) as e:
        print(f"Error is {e}")
    data_x = data[0][0]
    x_err = data[0][1]
    data_y = data[1][0]
    y_err = data[1][1]     
    
    # Бутстрэп для оценки погрешности коэффициентов
    N = len(data_x)
    slope_bootstrap = []
    intercept_bootstrap = []

    # Преобразование данных в numpy массивы
    data_x = np.array(data_x)
    data_y = np.array(data_y)
    x_err = np.array(x_err)
    y_err = np.array(y_err)

    for _ in range(count_iter):
        # Генерация выборки с возвращением
        indices = np.random.choice(N, size=N, replace=True)
        
        # Добавление случайных ошибок с учетом погрешности
        x_bootstrap = data_x[indices] + np.random.normal(0, x_err[indices])
        y_bootstrap = data_y[indices] + np.random.normal(0, y_err[indices])
        
        # Подгонка линейной регрессии для выборки с возвращением
        A = np.vstack([x_bootstrap, np.ones(N)]).T
        m, c = np.linalg.lstsq(A, y_bootstrap, rcond=None)[0]
        
        slope_bootstrap.append(m)
        intercept_bootstrap.append(c)

    # Оценка параметров и погрешностей
    slope_mean = np.mean(slope_bootstrap)
    intercept_mean = np.mean(intercept_bootstrap)

    slope_std = np.std(slope_bootstrap)
    intercept_std = np.std(intercept_bootstrap)

    return slope_mean, intercept_mean, slope_std, intercept_std

def xi_square_approximation(func, initial_coeffs, data):
    try:
        __check_of_data_with_x_xerr_y_yerr(data)
    except (ValueError, TypeError) as e:
        print(f"Error is {e}")
    data_x = data[0][0]
    x_err = data[0][1]
    data_y = data[1][0]
    y_err = data[1][1]  
    
    def chi2_d1(coeffs, x_experiment, y_experiment, y_errors):
        model = func(x_experiment, coeffs)
        return np.sum(((y_experiment - model) / y_errors) ** 2)
    
    init = initial_coeffs
    
    
    N = len(data_x)
    B = 10*N  # Количество повторений бутстрэпа
    bootstrap_result = []

    for _ in range(B):
        # Генерация выборки с возвращением
        indices = np.random.choice(N, size=N, replace=True)
        
        x_bootstrap = data_x[indices] + np.random.normal(0, x_err[indices])
        y_bootstrap = data_y[indices] + np.random.normal(0, y_err[indices])
        y_err_bootstrap = y_err[indices]

        minimize_result = minimize(chi2_d1, init, args=(x_bootstrap, y_bootstrap, y_err_bootstrap))
                
        bootstrap_result.append(minimize_result.x)

    result_val = []
    result_err = []
    for i in range(0, len(bootstrap_result[0])):
        datas = []
        for j in range(0, len(bootstrap_result)):
            datas.append(bootstrap_result[j][i])
        result_val.append(np.mean(datas))
        result_err.append(np.std(datas))

    return result_val, result_err

def residualReal(pars, x_data, func_to_calculate_y, data=None):
    # return the residual, i.e. the fitted model - the experimental data

	model=np.real(func_to_calculate_y(x_data, pars))

	if data is None:
		return model

	return (model - np.real(data))

def residualBoth(pars, x_data, func_to_calculate_y, data=None):
    # return the residual, i.e. model - experiment
	# fit to the real and imaginary parts with equal weighting [could scale one relative to the other to make it less significant]

	model=func_to_calculate_y(x_data, pars)
	if data is None:
		return model
	return ((np.real(model) - np.real(data))**2) + (np.imag(model) - np.imag(data))**2	

def approximate_params(data, fit_params, fitting_function=residualBoth, verbose=False):
    try:
        __check_of_data_with_x_y(data)
        if not isinstance(fitting_function, types.FunctionType):
            raise ValueError("fitting function should be a function!!! For example you can use residualReal or residualBoth.")
    except (ValueError, TypeError) as e:
        print(f"Error is {e}")
    
    res =  minimize(fitting_function, fit_params, args=(data[0][0]), kws={'data':data[1][0]})
    if verbose:
        print(fit_report(res))
    