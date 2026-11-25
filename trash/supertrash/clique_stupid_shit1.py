import numpy as np


test_matrix = np.random.randint(2,size=(8,8))

bucket_dict = dict()

print(test_matrix)


for row in test_matrix:
    
    if(row.sum() not in bucket_dict.keys()):
        bucket_dict[row.sum()]=[]
    bucket_dict[row.sum()].append(row.copy())


inverse_len_dict = {}



for key in bucket_dict.keys(): 
    if len(bucket_dict[key]) not in inverse_len_dict:
        inverse_len_dict[len(bucket_dict[key])]=[]       
    inverse_len_dict[len(bucket_dict[key])].append(key)
    print(f'Bucket: {key}: members: ({len(bucket_dict[key])}) {bucket_dict[key]}')

print(inverse_len_dict, inverse_len_dict.keys())

key_list = inverse_len_dict.keys()
key_list = sorted(key_list)[::-1]
print(key_list)

end_matrix = np.ndarray([])

for idx in key_list:
    for row_idx in inverse_len_dict[idx]:
        end_matrix = np.vstack((end_matrix,bucket_dict[row_idx]))





#print(sorted_buckets)
# sorted_buckets = {k:bucket_dict[k] for k in sorted(bucket_dict)}


#sorted_matrix = np.empty()
#for k in sorted_buckets.reverse()
