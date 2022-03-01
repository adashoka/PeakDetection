from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import glob
import os
import logging

total_class_a = 0
total_class_b = 0
image_output_dir = '../output/peak_detection/images/'
log_file = '../log/peak_detection/run.log'


formatter = "%(funcName)20s() | %(levelname)8s | %(message)s"
logging.basicConfig(filename=log_file,
                    filemode='w',
                    format=formatter,
                    level=logging.INFO)
logger = logging.getLogger()


def read_raw_file(name):
    data1_l = []
    data2_l = []
    with open(name) as file:
        for line in file:
            line = line.rstrip()
            data1, data2 = line.split()
            data1_f = float(data1)
            data2_f = float(data2)
            data1_l.append(data1_f)
            data2_l.append(data2_f)
    return data1_l, data2_l


def read_expected_peaks(name):
    apex_time_l = []
    class_l = []
    start_time_l = []
    start_height_l = []
    end_time_l = []
    end_height_l = []
    with open(name) as file:
        file.readline()
        for line in file:
            line = line.rstrip()
            at, c, st, sh, et, eh = line.split()
            at_f = float(at)
            st_f = float(st)
            sh_f = float(sh)
            et_f = float(et)
            eh_f = float(eh)
            apex_time_l.append(at_f)
            class_l.append(c)
            start_time_l.append(st_f)
            start_height_l.append(sh_f)
            end_time_l.append(et_f)
            end_height_l.append(eh_f)
    return apex_time_l, class_l, start_time_l, start_height_l, end_time_l, end_height_l


def experiment_0(time_l,value_l):
    # average window
    window_size = 100
    average_value = []
    average_value_v1 = []
    # has no memory; zero every time
    window_total = 0.0
    # starting state = previous average value
    window_total_v1 = 0.0

    window_index = 0
    i = 0
    total_samples = len(time_l)
    evaluate = True
    while evaluate is True:
        # set initial conditions for variables
        v = value_l[i]
        logger.info("value:{}".format(v))

        # calculate window total
        if window_index < window_size:
            window_index = window_index + 1
            window_total = window_total + v
            window_total_v1 = window_total_v1 + v
            logger.info("window_total:{}".format(window_total))
            logger.info("window_total_v1:{}".format(window_total_v1))

        # calculate window average at the end of window
        else:
            window_index = 0
            # calculate window average
            window_average = window_total / window_size
            window_average_v1 = window_total_v1 / window_size
            logger.info("window_average:{}".format(window_average))
            logger.info("window_average_v1:{}".format(window_average_v1))

            # doesn't do a good job of capturing peaks
            # future peak affects average value a lot
            # create average value array
            for j in range(0, window_size):
                average_value.append(window_average)
                average_value_v1.append(window_average_v1)
            # initialize variables for next iteration
            window_total_v1 = window_average_v1
            window_total = 0
            i = i + window_size

        # exit criteria (you need to handle this more gracefully)
        # right now you are loosing samples; what happens if you have a curve
        # towards the end ?
        if i >= total_samples:
            evaluate = False

    # remove any extra elements you've inserted; this is happening because you
    # are not handling the i varaible well
    remove_count = len(time_l) - len(average_value)
    del average_value[remove_count:]
    del average_value_v1[remove_count:]

    return average_value,average_value_v1


def zero_list(n):
    list_of_zeros = [0] * n
    return list_of_zeros


def rate_of_change(value_l, window_size):
    chunks = [value_l[x:x+window_size] for x in range(0, len(value_l), window_size)]
    rate_of_change_l = []
    for my_list in chunks:
        list_length = len(my_list)
        total = 0
        if list_length == window_size:
            for elements in my_list:
                total = total + abs(elements)
                logger.info("total:{}".format(total))
            rate_of_change = total/window_size
            logger.info("rate_of_change:{}".format(rate_of_change))
            rate_of_change_l.append(rate_of_change)
    return rate_of_change_l


def flat_land(total_samples, roc_window_size, roc_l, flat_land_acceptance):
    previous_value = 0
    flat_land_marker = []
    for i in range(len(roc_l)):
        current_value = roc_l[i]
        delta = previous_value - current_value
        abs_delta = abs(delta)
        previous_value = current_value
        if abs_delta <= flat_land_acceptance:
            absolute_index = i * roc_window_size
            flat_land_marker.append(absolute_index)
    return flat_land_marker






def moving_average(time_l, value_l):
    total_samples = len(time_l)
    window_size = 4
    average_value = []
    previous_avg = 0.0
    window_total = 0.0

    i = 0
    evaluate = True
    while evaluate is True:
        # set initial conditions for
        window_total = 0
        v = value_l[i]
        logger.info("value:{}".format(v))
        for j in range(0, window_size):
            sample_index = i + j
            window_total = previous_avg + window_total + value_l[sample_index]
        window_average = window_total/window_size
        average_value.append(window_average)
        # you'll miss samples in the end
        if i + window_size < total_samples:
            i = i + 1
        else:
            evaluate = False
    return average_value


def overlay(raw_file, expected_file, index):
    raw_file = raw_file
    expected_file = expected_file
    raw_file_name = raw_file.split('\\')[-1]

    logger.info("raw_file     :{}".format(raw_file))
    logger.info("expected_file:{}".format(expected_file))
    logger.info("file_name    :{}".format(raw_file_name))
    time_l, value_l = read_raw_file(name=raw_file)
    logger.info("length       :{}".format(len(time_l)))
    total_samples = len(time_l)
    # ##########################################################################
    # different experiments go here

    # average_value, average_value_v1 = experiment_0(time_l=time_l, value_l=value_l)
    # average_value = moving_average(time_l=time_l, value_l=value_l)

    roc_window_size = 2
    roc_l = rate_of_change(value_l=value_l, window_size=roc_window_size)
    graph_roc = []
    add_element_flag = 0
    roc_index = 0
    window_edge = roc_window_size - 1
    for i in range(len(time_l)):
        if add_element_flag == window_edge:
            add_element_flag = 0
            graph_roc.append(roc_l[roc_index])
            roc_index = roc_index + 1
        else:
            add_element_flag = add_element_flag + 1
            graph_roc.append(0)
    flat_markers = flat_land(total_samples=total_samples,
                             roc_window_size=roc_window_size,
                             roc_l=roc_l,
                             flat_land_acceptance=50)








    # make length similar -- trim end samples
    # #########################################################################
    logger.info("original:{}".format(len(time_l)))
    #logger.info("mylength:{}".format(len(average_value)))
    logger.info("mylength:{}".format(len(graph_roc)))

    remove_count = len(time_l) - len(graph_roc)
    logger.info("remove_count:{}".format(remove_count))
    if remove_count < 0:
        del graph_roc[remove_count:]
    elif remove_count > 0:
        remove_count = -1 * remove_count
        del time_l[remove_count:]
        del value_l[remove_count:]
    logger.info("time_length:{}".format(len(time_l)))
    logger.info("value_length:{}".format(len(value_l)))
    logger.info("mylist_length:{}".format(len(graph_roc)))



    # graphing part
    # #########################################################################
    at_l, c_l, st_l, sh_l, et_l, eh_l = read_expected_peaks(name=expected_file)
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%0.7f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%0.7f'))
    local_class_a = 0
    local_class_b = 0
    for i in range(len(at_l)):
        my_at = at_l[i]
        my_c = c_l[i]
        my_st = st_l[i]
        my_sh = sh_l[i]
        my_et = et_l[i]
        my_eh = eh_l[i]
        if my_c == 'A':
            global total_class_a
            total_class_a = total_class_a + 1
            local_class_a = local_class_a + 1
            ax.axvline(my_at, color='r', linestyle='--', alpha=0.25)
            ax.axvspan(my_st, my_et, color='k', alpha=0.07)
            ax.plot(my_st, my_sh, color='g', marker='^')
            ax.plot(my_et, my_eh, color='r', marker='o')
        elif my_c == 'B':
            global total_class_b
            total_class_b = total_class_b + 1
            local_class_b = local_class_b + 1
            ax.axvline(my_at, color='m', linestyle='--', alpha=0.25)
            ax.axvspan(my_st, my_et, color='b', alpha=0.03)
            ax.plot(my_st, my_sh, color='y', marker='^')
            ax.plot(my_et, my_eh, color='k', marker='o')

    local_total = local_class_a + local_class_b
    prefix = "i{}_a{}_b{}_t{}_".format(index, local_class_a, local_class_b, local_total)
    image_name = prefix + raw_file_name.replace(".txt", ".png")
    logger.info("image_name   :{}".format(image_name))
    logger.info("A Peak #     :{}".format(local_class_a))
    logger.info("B Peak #     :{}".format(local_class_b))
    plt.style.use('seaborn')
    ax.plot(time_l, value_l)

    # your stuff
    ##############################################################################
    #ax.plot(time_l, average_value, color='b', alpha=0.7, linestyle='--')
    #ax.plot(time_l, average_value_v1, color='m', alpha=0.5, linestyle='dashdot')
    logger.info(len(time_l))
    logger.info(len(graph_roc))
    #ax.plot(time_l, graph_roc)

    #add markers
    #for i in flat_markers:
     #   ax.axvline(i, color='y', linestyle='--', alpha=0.25)

    plt.tight_layout()
    plt.grid()
    plt.show()
    plt.close('all')


def main():
    '''
    [1] Identify at least 95% of the class A peaks in each of the raw data files.
    [2] False positive rate no greater than 15%
    [3] Start Time, and End Time error for 95% of Class A peaks is less than 15% of peak width.
    (peak width is given as time between End and Start time of the expected peak.)
    [4] Have an error of less than 10% for Start Height and End Height for 95% of Class A peak.
    :return:
    '''
    # total file count: 650
    # start file index: 0
    # end file index: 649
    # range (0,1) : 0
    # range (0,5) : 0,1,2,3,4
    # range (6,7) : 6
    # range (7,8) : 7
    start = 23
    end = 24

    training_raw_glob = '../input/peak_detection/Training/*/*raw.txt'
    training_expected_glob = '../input/peak_detection/Training/*/*expected.txt'
    raw_files = [os.path.normpath(i) for i in glob.glob(training_raw_glob, recursive=True)]
    expected_files = [os.path.normpath(i) for i in glob.glob(training_expected_glob, recursive=True)]
    logger.info("Total raw files:{}".format(len(raw_files)))
    logger.info("Total expected files:{}".format(len(expected_files)))
    for i in range(start, end):
        logger.info("-------------------------------------")
        logger.info("index:{}".format(i))
        my_raw_file = raw_files[i]
        my_expected_file = expected_files[i]
        overlay(raw_file=my_raw_file, expected_file=my_expected_file, index=i)

    logger.info("#####################################")
    logger.info("Total Class A peak count:{}".format(total_class_a))
    logger.info("Total Class B peak count:{}".format(total_class_b))


if __name__ == "__main__":
    main()

