""" fitting_utils . py PPGSEA / UFLA , 2026 """
import numpy as np
from scipy . optimize import curve_fit
from scipy . stats import pearsonr
from sklearn . linear_model import RidgeCV
from sklearn . model_selection import KFold
from sklearn . metrics import mean_squared_error


def mtp_sigmoid (tau , k , tau0 ):
    """MTP - MOS sigmoid ( Eq . 3.3) . Output : MOS [1 ,5]. """
    return 4.0 / (1.0 + np . exp (k *( tau - tau0 ))) + 1.0


def fit_sigmoid ( tau_vals , mos_vals , p0 =(0.30 , 20.0) ):
    """Non - linear least - squares fit of sigmoid to Campaign A data ."""
    popt , pcov = curve_fit ( mtp_sigmoid , tau_vals , mos_vals ,
                             p0 =p0 , bounds =([0.01 ,0] ,[2.0 ,100]) ,
                             maxfev =10 _000 )
    perr = np . sqrt ( np . diag ( pcov ))
    res = mos_vals - mtp_sigmoid ( tau_vals , * popt )
    r2 = 1.0 - res . var () / mos_vals . var ()
    return {"k": popt [0] , " tau0 ": popt [1] ,
            " k_se ": perr [0] , " tau0_se ": perr [1] , " r2 ": r2 }


def fit_qoe_model (X , y , alphas = None , n_splits =5 , seed =42) :
    """ Ridge regression with k - fold CV ; returns normalised weights ."""
    if alphas is None :
        alphas = np . logspace (-3 , 3, 50)
    kf = KFold ( n_splits = n_splits , shuffle = True , random_state = seed )
    mdl = RidgeCV ( alphas = alphas , cv =kf , fit_intercept = True )
    mdl . fit (X , y)

    y_hat = mdl . predict (X)
    r , _ = pearsonr (y , y_hat )
    rmse = float( np . sqrt ( mean_squared_error (y , y_hat )))
    coef = np . maximum ( mdl . coef_ , 0.0)
    w_norm = coef / coef .sum() if coef .sum() >1e -9 else np . ones (5) /5
    return {" weights ": w_norm . tolist () , " alpha ": mdl . alpha_ ,
            " pearson_r ":r , " rmse ": rmse }


def bootstrap_ci ( y_true , y_pred , n =1000 , ci =0.95 , seed =0) :
    """ Bootstrap 95% CI for Pearson r."""
    rng = np . random . default_rng ( seed )
    N = len( y_true )
    rs = [ pearsonr ( y_true [i := rng . integers (0 ,N ,N)],
                      y_pred [i ]) [0] for _ in range(n)]
    a = (1 - ci ) /2
    return float( np . quantile (rs ,a)) , float( np . quantile (rs ,1 -a))
