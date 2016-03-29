#!/usr/bin/python

import csv
import time
import numpy
import seaborn
from pandas import DataFrame
from matplotlib.colors import ListedColormap

def load_matrices(path_distances, path_scores):
    distances_matrix = numpy.load(path_distances)

    reader=csv.reader(open(path_scores,"r"),delimiter=',')
    tmp_scores=list(reader)
    scores_matrix = numpy.array(tmp_scores).astype('float')

    return distances_matrix, scores_matrix

def load_metadata(dataset_folder):
    file = open(dataset_folder + 'metadata.dat')
    for line in iter(file):
        if line.startswith('Second loop index: '):
            line = line.replace('Second loop index: ', '')
            second_loop_index = int(line)
        elif line.startswith('Loop 1 odometry difference: '):
            line = line.replace('Loop 1 odometry difference: ', '')
            loop1_odom_diff = [float(i) for i in line.split()]
        elif line.startswith('Loop 2 odometry difference: '):
            line = line.replace('Loop 2 odometry difference: ', '')
            loop2_odom_diff = [float(i) for i in line.split()]
    metadata = [second_loop_index, loop1_odom_diff, loop2_odom_diff]

    return metadata

def create_lists(distances_matrix, scores_matrix):
    # Create lists for index1, index2, distances (left-lower diago excl. diago)
    matrix_size = distances_matrix.shape[1]
    index1 = []
    index2 = []
    distances = []
    scores = []
    for i in range(0, matrix_size):
        for j in range(0,i):
            index1.extend([i])
            index2.extend([j])
            distances.extend([distances_matrix[i,j]])
            scores.extend([scores_matrix[i,j]])

    return index1, index2, distances, scores

def sort_by_distance(index1, index2, distances, scores):
    sorted_indexes = numpy.argsort(distances)
    sorted_index1 = [index1[i] for i in sorted_indexes]
    sorted_index2 = [index2[i] for i in sorted_indexes]
    sorted_distances = [distances[i] for i in sorted_indexes]
    sorted_scores = [scores[i] for i in sorted_indexes]

    return sorted_index1, sorted_index2, sorted_distances, sorted_scores

def compute_results(sorted_distances, sorted_scores, score_threshold):
    # Compute values for distance = 0
    fn = 0
    fp = 0
    tn = 0
    tp = 0
    pairCounts = len(sorted_distances)
    for i in range(0, pairCounts):
        if sorted_scores[i] > score_threshold:
            fp = fp + 1
        else:
            tn = tn + 1

    result_distances = [0]
    result_fn = [0]
    result_fp = [fp]
    result_tn = [tn]
    result_tp = [0]

    # Loop for all pairs in ascending order by distance...
    # switch the old value for new value and record
    for i in range(0, pairCounts): # Basically the pair become "in range'
        if sorted_scores[i] > score_threshold:
            fp = fp - 1
            tp = tp + 1
        else:
            tn = tn - 1
            fn = fn + 1

        result_distances.extend([sorted_distances[i]]) # Could do it in one shot
        result_fn.extend([fn])
        result_fp.extend([fp])
        result_tn.extend([tn])
        result_tp.extend([tp])

    return result_distances, result_fn, result_fp, result_tn, result_tp

def create_plot(x,y):
    seaborn.set_style('whitegrid')
    seaborn.plt.title('Recall Rate for different maximum distance thresholds')
    seaborn.plt.xlabel('Maximum distance threshold (m)')
    seaborn.plt.ylabel('Recall rate (%)')
    seaborn.plt.plot(x, y, '-')
    seaborn.plt.grid(True)

    seaborn.plt.savefig('Data/recall_plot.pdf')
    seaborn.plt.show()

def create_distances_heatmap(distances_matrix, second_loop_index):
    seaborn.plt.title('Distances matrix', fontsize=20)

    seaborn.set(font_scale=2.0)
    labels = ['' for i in range(0, distances_matrix.shape[0])]
    labels[0] = '0'
    labels[second_loop_index] = str(second_loop_index)
    last_index = distances_matrix.shape[0]-1
    labels[last_index] = str(last_index)

    dataframe = DataFrame(data=distances_matrix)
    cmap1 = ListedColormap(seaborn.color_palette("gist_heat_r",512))
    fig = seaborn.heatmap(dataframe, square=True, yticklabels=labels, xticklabels=labels, cmap=cmap1)
    seaborn.plt.ylabel('Sample index')
    seaborn.plt.xlabel('Sample index')
    fig.invert_yaxis()

    seaborn.plt.savefig('Data/distances_matrix.png')
    seaborn.plt.show()

def create_scores_heatmap(scores_matrix, second_loop_index):
    seaborn.plt.title('Scores matrix', fontsize=20)

    labels = ['' for i in range(0, scores_matrix.shape[0])]
    labels[0] = '0'
    labels[second_loop_index] = str(second_loop_index)
    last_index = scores_matrix.shape[0]-1
    labels[last_index] = str(last_index)

    dataframe = DataFrame(data=scores_matrix)
    cmap1 = ListedColormap(seaborn.color_palette("gist_heat_r",512))
    fig = seaborn.heatmap(dataframe, square=True, yticklabels=labels, xticklabels=labels, cmap=cmap1)
    seaborn.plt.ylabel('Sample index')
    seaborn.plt.xlabel('Sample index')
    fig.invert_yaxis()

    seaborn.plt.savefig('Data/scores_matrix.png')
    seaborn.plt.show()

def main():
    print("Computing place recognition results...")

    distances_matrix_file = 'Data/distances_matrix.npy'
    dataset_folder = '/media/D/Datasets/PlaceRecognition/SickBuilding/Output/'
    scores_matrix_file = dataset_folder + 'scores_matrix.csv'

    distances_matrix, scores_matrix = load_matrices(distances_matrix_file, scores_matrix_file)
    metadata = load_metadata(dataset_folder)
    second_loop_index = metadata[0]

    index1, index2, distances, scores = create_lists(distances_matrix, scores_matrix)
    sorted_index1, sorted_index2, sorted_distances, sorted_scores = sort_by_distance(index1, index2, distances, scores)

    # create_distances_heatmap(distances_matrix, second_loop_index)
    # create_scores_heatmap(scores_matrix, second_loop_index)

    score_threshold = 0.2
    result_distances, fn, fp, tn, tp = compute_results(sorted_distances, sorted_scores, score_threshold)
    tp = numpy.array(tp, dtype=numpy.float)
    fn = numpy.array(fn, dtype=numpy.float)
    recall = numpy.divide(tp, numpy.add(tp, fn))*100
    create_plot(result_distances, recall)

    print("Done !")


if __name__ == '__main__':
    main()
