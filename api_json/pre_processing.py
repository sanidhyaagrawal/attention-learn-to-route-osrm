'''
#TODO Refactor
'''

import json
import os

datas = [["api_json/response_tours_agthia.json", "api_json/response_dist_agthia.json"], 
         ["api_json/response_tours_bukalapak.json", "api_json/response_dist_bukalapak.json"],
         ["api_json/response.json", "api_json/response_dist.json"]]  

base_dir = os.path.dirname(os.path.abspath(__file__)).replace("api_json", "")

def get_sequences(source_id):
    file = open(base_dir + datas[source_id][0], 'r')
    data = json.load(file)
    all_sequences = []
    for tour_data in data["tours"]:
        sequences = []
        for visit_data in tour_data["visits"]:
            if visit_data["id"] == "customer":
                sequences.append(visit_data["sourceId"])
        all_sequences.append(sequences)
    return all_sequences

def create_task_cord_dict(source_id):
    file = open(base_dir + datas[source_id][1], 'r')
    data = json.load(file)
    task_cord_dict = {}
    for tasks in data["tasks"]:
        task_cord_dict[tasks["taskId"]] = [tasks["location"]["lat"], tasks["location"]["lng"]]
    return task_cord_dict

def get_distance_matrix(source_id):
    file = open(base_dir + datas[source_id][1], 'r')
    data = json.load(file)
    _precision = 5
    matrix = {}
    for d in  data["distanceMatrix"]["responses"]:
        matrix[(round(d['sourceLat'], _precision), round(d['sourceLng'], _precision), round(d['destinationLat'], _precision), round(d['destinationLng'], _precision))] = {'distance': d['distance'], 'duration': d["duration"]}
        matrix[(round(d['destinationLat'], _precision), round(d['destinationLng'], _precision), round(d['sourceLat'], _precision), round(d['sourceLng'], _precision))] = {'distance': d['distance'], 'duration': d["duration"]}

        matrix[(round(d['destinationLat'], _precision), round(d['destinationLng'], _precision), d['destinationLat'], _precision), round(d['destinationLng'], _precision)] = {'distance': d['distance'], 'duration': d["duration"]}
        matrix[(round(d['sourceLat'], _precision), round(d['sourceLng'], _precision), round(d['sourceLat'], _precision), round(d['sourceLng'], _precision))] = {'distance': d['distance'], 'duration': d["duration"]}

    print(len(matrix))
    return matrix

def sequences_to_cords(sequences, source_id):
    task_cord_dict = create_task_cord_dict(source_id)
    cord_sequences = []
    for sequence in sequences:
        cord_sequence = []
        for task in sequence:
            cord_sequence.append(task_cord_dict[task])
        cord_sequences.append(cord_sequence)
    return cord_sequences

def get_cords(source_id = 0):
    # print(datas[source_id][0])
    sequences = get_sequences(source_id)
    # print(sequences)
    cords = sequences_to_cords(sequences, source_id)
    return cords



if __name__ == "__main__":
    # cords0 = get_cords(0)
    # cords1 = get_cords(1)

    # print(len(cords0))
    # print(len(cords1))

    # print(cords0 == cords1)
    get_distance_matrix(1)

   
