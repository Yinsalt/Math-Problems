import numpy as np
import time
np.random.seed(int(time.time_ns()%10000))

def new_test(a,b):
    original = np.random.randint(2,size=(a,b))

    sort_idx = np.argsort(original.sum(axis=1))[::-1]
    sorted_matrix = original[sort_idx:,:,sort_idx]

    sort_idx =np.sort(sort_idx)[::-1]
    return sorted_matrix,sort_idx



A = new_test(10,10)

def count_rows(test_matrix):
    count_dict = dict()
    for label in range(len(test_matrix[1])):
        count_dict[label] = 0
    
    for row in test_matrix:
        row_sum = int(row.sum())
        count_dict[row_sum]+=1

    for key in list(count_dict.keys())[::-1]:
        print(f'label: {key}: {count_dict[key]}')

    return count_dict

print(A)

count_dict=count_rows(A)

print(count_dict)

def max_possible_c(count_dict):
    accumulated = 0
    for key in list(count_dict.keys())[::-1]:
        accumulated += count_dict[key]
        if(key<=accumulated):
            return key
        
stop_value = max_possible_c(count_dict)

print("max possible structure:",stop_value)


# tracken der verbindungen höherer ordnungen um sie schnell auszusortieren -> dropout
# idx tracking, zuerst die 1 row für row durchgehen und gegenchecken, auch tracken welche label ausgeschlossen werden können

def list_of_labels(stop_value):
    labels = []
    for i in range(stop_value, 2,-1):
        labels.append(i)
    return labels

label_list = list_of_labels(stop_value)
print(label_list)
label_eliminator = {}




#zuallererst die großen eliminieren. das ist einfach, denn man muss nur bis zu den akkumuliertem wert an nodes checken um das auszuschließen.
# außerdem könnte man darauf alle übrigen checks durchführen
# das tracken würde kandidaten ausschließen, die schon mal für bestimmte checks benutzt wurden, somit würden nur noch
# die übrigen niederen checks übrig  bleiben.
#würde eine struktur gefunden werden, hätten wir die untere grenze und könnten operationen darunter ausschließen und kandidaten eliminieren

#man beschneidet den arbeitsaufwand für zukünftige durchläufe von beiden seiten aus.

# wenn eine struktur gefunden wurde, müssen nur noch die nächsthöheren ebenen durchsucht werden
# 

def tracking_matrix(test_matrix):
    height,width = test_matrix.shape
    return np.zeros((height,width))



print(tracking_matrix(A))


label_tracking_matrices = dict()

for label in label_list:
    print(label)

# eliminate rows and columns is optional. MASKING


# durchlaufe äußerste schichten und prüfe auf  verbindungen untereinander. 
# bei stop_value gefundenen elementen subgraphen untersuchen
# auf subgrapheigenschaften untersuchen





#Permutationsmatrizen

# p = {1,2,0]}
#a_permuted = A[np.ix_(p,p)

p = np.eye(3)[2,0,1]



#aus dem sorted musst du im original suchen
