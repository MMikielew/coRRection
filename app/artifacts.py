"""
Moduł odpowiedziany za automatyczne wyznaczanie oraz usuwanie artefaktów
"""
import numpy as np
from scipy import interpolate
import scipy as sp
import pandas as pd

def find_art_tarvainen(obj,
                        c1=0.13,
                        c2=0.17,
                        alpha=5.2,
                        window_width=91,
                        medfilt_order=11):

    def _compute_threshold(signal, alpha, window_width):
        df = pd.DataFrame({"signal": np.abs(signal)})
        q1 = (
            df.rolling(window_width, center=True, min_periods=1)
            .quantile(0.25)
            .signal
        )
        q3 = (
            df.rolling(window_width, center=True, min_periods=1)
            .quantile(0.75)
            .signal
        )
        th = alpha * ((q3 - q1) / 2)

        return th

    rr = list(map(lambda x: x.value, obj.examination.RR_intervals))
    #rr = list(map(int, rr))
    drrs = np.ediff1d(rr, to_begin=0)
    drrs[0] = np.mean(drrs[1:])
    th1 = _compute_threshold(drrs, alpha, window_width)
    # ignore division by 0 warning
    old_setting = np.seterr(divide="ignore", invalid="ignore")
    drrs /= th1
    # return old setting
    np.seterr(**old_setting)
    padding = 2
    drrs_pad = np.pad(drrs, padding, "reflect")

    s12 = np.zeros(drrs.size)
    for d in np.arange(padding, padding + drrs.size):
        if drrs_pad[d] > 0:
            s12[d - padding] = np.max([drrs_pad[d - 1], drrs_pad[d + 1]])
        elif drrs_pad[d] < 0:
            s12[d - padding] = np.min([drrs_pad[d - 1], drrs_pad[d + 1]])
    # Cast dRRs to subspace s22.
    s22 = np.zeros(drrs.size)
    for d in np.arange(padding, padding + drrs.size):
        if drrs_pad[d] >= 0:
            s22[d - padding] = np.min([drrs_pad[d + 1], drrs_pad[d + 2]])
        elif drrs_pad[d] < 0:
            s22[d - padding] = np.max([drrs_pad[d + 1], drrs_pad[d + 2]])
    # Compute mRRs: time series of deviation of RRs from median.
    df = pd.DataFrame({"signal": rr})
    medrr = df.rolling(medfilt_order, center=True, min_periods=1).median().signal.values
    mrrs = rr - medrr
    mrrs[mrrs < 0] = mrrs[mrrs < 0] * 2
    # Normalize by threshold.
    th2 = _compute_threshold(mrrs, alpha, window_width)
    mrrs /= th2
    # Artifact classes.
    artifacts = []
    extra_idcs = []
    missed_idcs = []
    ectopic_idcs = []
    longshort_idcs = []

    i = 0
    while i < len(rr) - 2:  # The flow control is implemented based on Figure 1
        if np.abs(drrs[i]) <= 1:  # Figure 1
            i += 1
            continue
        eq1 = np.logical_and(
            drrs[i] > 1, s12[i] < (-c1 * drrs[i] - c2)
        )  # pylint: disable=E1111
        eq2 = np.logical_and(
            drrs[i] < -1, s12[i] > (-c1 * drrs[i] + c2)
        )  # pylint: disable=E1111

        if np.any([eq1, eq2]):
            # If any of the two equations is true.
            ectopic_idcs.append(i)
            i += 1
            continue
        # If none of the two equations is true.
        if ~np.any([np.abs(drrs[i]) > 1, np.abs(mrrs[i]) > 3]):  # Figure 1
            i += 1
            continue
        longshort_candidates = [i]
        # Check if the following beat also needs to be evaluated.
        if np.abs(drrs[i + 1]) < np.abs(drrs[i + 2]):
            longshort_candidates.append(i + 1)
        for j in longshort_candidates:
            # Long beat.
            eq3 = np.logical_and(drrs[j] > 1, s22[j] < -1)  # pylint: disable=E1111
            # Long or short.
            eq4 = np.abs(mrrs[j]) > 3  # Figure 1
            # Short beat.
            eq5 = np.logical_and(drrs[j] < -1, s22[j] > 1)  # pylint: disable=E1111

            if ~np.any([eq3, eq4, eq5]):
                # If none of the three equations is true: normal beat.
                i += 1
                continue
            # If any of the three equations is true: check for missing or extra
            # peaks.

            # Missing.
            eq6 = np.abs(rr[j] / 2 - medrr[j]) < th2[j]  # Figure 1
            # Extra.
            eq7 = np.abs(rr[j] + rr[j + 1] - medrr[j]) < th2[j]  # Figure 1

            # Check if extra.
            if np.all([eq5, eq7]):
                extra_idcs.append(j)
                i += 1
                continue
            # Check if missing.
            if np.all([eq3, eq6]):
                missed_idcs.append(j)
                i += 1
                continue
            # If neither classified as extra or missing, classify as "long or
            # short".
            longshort_idcs.append(j)
            i += 1

    for artifact_type in (extra_idcs, missed_idcs, ectopic_idcs, longshort_idcs):
        artifacts.extend(artifact_type)
    
    return artifacts

def find_art1(obj):
    """
    funkcja do wyszukiwania artefaktów typu 1
    """
    diff = int(obj.textbox_art1.text())
    # count differences between this and previous interval
    d_prev = [1 if abs(obj.examination.RR_intervals[i].value - obj.examination.RR_intervals[i-1].value) > diff else 0 for i in range(1, len(obj.examination.RR_intervals))]
    d_prev.insert(0, 0)
    # count differences between this and next interval
    d_next = [1 if abs(obj.examination.RR_intervals[i-1].value - obj.examination.RR_intervals[i].value) > diff else 0 for i in range(1, len(obj.examination.RR_intervals))]
    d_next.insert(-1, 0)

    final_list = [sum(value) for value in zip(d_prev, d_next)]
    #check for last interval
    if abs(obj.examination.RR_intervals[-1].value - obj.examination.RR_intervals[-2].value) > diff:
        final_list[-1] = 2
    
    idx = np.where(np.array(final_list) == 2)[0]

    return idx.tolist()

def find_art2(obj):
    """
    funkcja do wyszukiwania artefaktów typu 2 - długi interwał po którym następuje krótki interwał
    """
    diff = int(obj.textbox_art2.text())
    # obliczone różnice między obecnym i następnym interwałem
    d_next = [1 if (obj.examination.RR_intervals[i-1].value - obj.examination.RR_intervals[i].value) > diff else 0 for i in range(1, len(obj.examination.RR_intervals))]
    d_next.insert(-1, 0)
    # check for last sample
    if obj.examination.RR_intervals[-2].value - obj.examination.RR_intervals[-1].value > diff:
        d_next[-1] = 1

    idx = np.where(np.array(d_next) == 1)[0]
    art1 = find_art1(obj)
    final = [x for x in idx if x not in art1]
    return final

def find_art3(obj):
    """
    funkcja do wyszukiwania artefaktów typu 3 - krótki interwał po którym następuje długi interwał
    """
    diff = int(obj.textbox_art3.text())
    # obliczone różnice między obecnym i następnym interwałem
    d_next = [1 if (obj.examination.RR_intervals[i-1].value - obj.examination.RR_intervals[i].value) > diff else 0 for i in range(1, len(obj.examination.RR_intervals))]
    d_next.insert(-1, 0)
    # check for last sample
    if obj.examination.RR_intervals[-1].value - obj.examination.RR_intervals[-2].value > diff:
        d_next[-1] = 1
    idx = np.where(np.array(d_next) == 1)[0]
    art1 = find_art1(obj)
    final = [x for x in idx if x not in art1]
    return final

def find_art_quotient(obj):
    """
    function to find artifacts with a use of Piskorski-Guzik filter
    """
    x = np.array([interval.value for interval in obj.examination.RR_intervals])
    L = len(x) - 1
    condition1 = x[:L] / x[1:] <= 0.8
    condition2 = x[:L] / x[:L] > 1.2
    condition3 = x[1:] / x[:L] < 0.8
    condition4 = x[1:] / x[:L] > 1.2

    indices_p = np.where(condition1 | condition2 | condition3 | condition4)[0]
    indices_m = indices_p

    return indices_m.tolist()

def remove_artifacts(obj):
    '''
    function to change chosen artifacts
    '''
    # odczyt wybranych przez uzytkownika artefaktow wybranych do usuniecia
    atypes = obj.chosen_artifacts
    # sprawdzenie wybranej metody korekcji artefaktow
    for m in [obj.m1, obj.m2, obj.m3, obj.m4, obj.m5]:
        if m.isChecked() == True:
            method = m.text()
    
    idx = np.array([])
    for atype in atypes:
        # dodanie odczytanych artefaktow do listy przeznaczonej do skorygowania
        for el in obj.examination.artifacts[atype]:
            if (el >= obj.exam_start and el <= obj.exam_stop):
                idx = np.append(idx, el)
                if obj.examination.RR_intervals[int(el)].artifact == None:
                    obj.examination.RR_intervals[int(el)].artifact = atype

    # sprawdzenie ilosci
    if len(idx) > 0:
        for i in idx:
            obj.examination.RR_intervals[int(i)].value = np.nan

        RR_with_nan = np.array([interval.value for interval in obj.examination.RR_intervals])
        # utworzenie wektora indeksow
        inds = np.arange(RR_with_nan.shape[0])
        # odczytanie wartosci nieprzeznaczonych do usuniecia
        values = np.where(np.isfinite(RR_with_nan))
        # utworzenie wektora wartosci do usuniecia
        nan_values = np.where(~np.isfinite(RR_with_nan))

        deleted = np.empty(0)
        # korekcja metoda interpolacji liniowej
        if method == "linear interpolation":
            f = interpolate.interp1d(inds[~np.isnan(RR_with_nan)], RR_with_nan[~np.isnan(RR_with_nan)], bounds_error=False)

            for i, interval in enumerate(obj.examination.RR_intervals):
                # Check if the interval value needs correction (e.g., if it's NaN)
                if np.isnan(interval.value):
                    # Apply linear interpolation based on the index associated with the interval
                    interval.value = f(i)
                    interval.correction_methods[method] += 1

        # korekcja metoda splajnu kubicznego
        elif method == "cubic splain":
            f = sp.interpolate.CubicSpline(inds[values], RR_with_nan[values])
            for i, interval in enumerate(obj.examination.RR_intervals):
                # Check if the interval value needs correction (e.g., if it's NaN)
                if np.isnan(interval.value):
                    # Apply linear interpolation based on the index associated with the interval
                    interval.value = f(i)
                    interval.correction_methods[method] += 1
        
        elif method == "deletion":
            nan_indices = [i for i, interval in enumerate(obj.examination.RR_intervals) if np.isnan(interval.value)]
            #obj.examination.RR_intervals = list(filter(lambda interval: not np.isnan(interval.value), obj.examination.RR_intervals))
            nan_indices = sorted(set(nan_indices), reverse=True)
            for nan_idx in nan_indices:
                for key in obj.examination.artifacts.keys():
                    if nan_idx in obj.examination.artifacts[key]:
                        obj.examination.artifacts[key].remove(nan_idx)
                        obj.examination.RR_intervals.pop(nan_idx)
                    obj.examination.artifacts[key] = [x - 1 if x > nan_idx else x for x in obj.examination.artifacts[key]]
                                                                                                                                                 
        # korekcja metoda sredniej kroczacej
        elif method == "moving average":
            for val in inds[nan_values]:
                # sprawdzenie warunku posiadania odpowiedniego sasiedztwa
                if 3 <= val <= len(obj.examination.RR_intervals) - 3:
                    neighborhood = RR_with_nan[val - 3:val + 4]
                    temp_means = []
                    for i in range(4):
                        temp_means.append(np.nanmean(neighborhood[i:i+4]))
                    
                    obj.examination.RR_intervals[val].value = np.mean(temp_means)
                    obj.examination.RR_intervals[val].correction_methods[method] += 1

                # jeśli przypadek skrajny o mniejszym sąsiedztwie niż zakładamy (+/-3) - interpolacja
                else:
                    f = interpolate.interp1d(inds[nan_values], RR_with_nan[nan_values], bounds_error=False)                            
                    if np.isnan(obj.examination.RR_intervals[val].value):
                        # Apply linear interpolation based on the index associated with the interval
                        obj.examination.RR_intervals[val].value = f(i)
                        obj.examination.RR_intervals[val].correction_methods["linear interpolation"] += 1

            # if any nans left (happen if there are many nans near each other or at the beggining/end - interpolate)
            RR_with_nan_new = np.array([interval.value for interval in obj.examination.RR_intervals])
            f = interpolate.interp1d(inds[~np.isnan(RR_with_nan_new)], RR_with_nan[~np.isnan(RR_with_nan_new)], bounds_error=False)
            for i, interval in enumerate(obj.examination.RR_intervals):
                # Check if the interval value needs correction (e.g., if it's NaN)
                if np.isnan(interval.value):
                    # Apply linear interpolation based on the index associated with the interval
                    interval.value = f(i)
                    interval.correction_methods["linear interpolation"] += 1

        elif method == "pre mean":
            for val in inds[nan_values]:
                value_from_gui = int(obj.pre_mean_count.currentText())
                # sprawdzenie warunku posiadania odpowiedniego sasiedztwa
                if value_from_gui <= val <= len(obj.examination.RR_intervals):
                    neighborhood = RR_with_nan[val - value_from_gui:val]
                    
                    obj.examination.RR_intervals[val].value = np.mean(neighborhood)
                    obj.examination.RR_intervals[val].correction_methods[method] += 1

                # jeśli przypadek skrajny o mniejszym sąsiedztwie niż zakładamy (+/-3) - interpolacja
                else:
                    f = interpolate.interp1d(inds[nan_values], RR_with_nan[nan_values], bounds_error=False)
                    if np.isnan(obj.examination.RR_intervals[val].value):
                        # Apply cubic spline interpolation based on the index associated with the interval
                        obj.examination.RR_intervals[val].value = f(val)
                        obj.examination.RR_intervals[val].correction_methods["linear interpolation"] += 1

            # if any nans left (happen if there are many nans near each other or at the beggining/end - interpolate)
            RR_with_nan_new = np.array([interval.value for interval in obj.examination.RR_intervals])
            f = interpolate.interp1d(inds[~np.isnan(RR_with_nan_new)], RR_with_nan_new[~np.isnan(RR_with_nan_new)], bounds_error=False)
            for i, interval in enumerate(obj.examination.RR_intervals):
                # Check if the interval value needs correction (e.g., if it's NaN)
                if np.isnan(interval.value):
                    # Apply linear interpolation based on the index associated with the interval
                    interval.value = f(i)
                    interval.correction_methods["linear interpolation"] += 1


        # pętla usuwająca wartości NAN z początku badania - te wartości nie mogły zostać zinterpolowane
        while np.isnan(obj.examination.RR_intervals[0].value):
            obj.examination.RR_intervals.pop(0)
            # jesli usunieto 1. element - zaktualizować indeksy
            for key in obj.examination.artifacts.keys():
                obj.examination.artifacts[key] = [x - 1 for x in obj.examination.artifacts[key]]
        
        # pętla usuwająca wartości NAN z końca badania
        while np.isnan(obj.examination.RR_intervals[-1].value):
            obj.examination.RR_intervals.pop(-1)
            for key in obj.examination.artifacts.keys():
                if len(obj.examination.RR_intervals) in obj.examination.artifacts[key]:
                    obj.examination.artifacts[key].remove(len(obj.examination.RR_intervals))

        #obj.examination.RR = np.array([int(element.value) for element in obj.examination.RR_intervals])
        for key in obj.examination.artifacts.keys():
            for i in idx:
                if i in obj.examination.artifacts[key]:
                    obj.examination.artifacts[key].remove(i)
        
        #obj.examination.RR  = np.array([int(interval.value) for interval in obj.examination.RR_intervals])
        return deleted
    else:
        return np.array([])

