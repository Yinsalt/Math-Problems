import numpy as np
import time
np.random.seed(int(time.time_ns()%10000))




def xor_and_matrices(matrix_A, matrix_B):# True if  A=True and B = False
    matrix_C = matrix_A ^ matrix_B
    matrix_C = matrix_C & matrix_A
    return matrix_C

def create_tier_matrices(conns,count):
    # Prüft Matrix ab nach bedingungen. Ist die Zahl größer/gleich seiner bucked-id? -> True
    # Metainfo, später nützlich
    collect = {}
    for i in range(len(count),2,-1):
        collect[i]=(conns>=i)
    return collect



def sum_tier_lists(tier_dict,info=False):
    sum_dict = {}
    for key in tier_dict.keys():
        row_sum = tier_dict[key].sum(axis=1)
        col_sum = tier_dict[key].sum(axis=0)
        if info:
            print("RowSum:",row_sum,"\nColSum",col_sum,"\n-","-"*60,"\n")
            print(f'Tier: {key}\n{tier_dict[key]}\n')
            print("="*60)
        sum_dict[key]=(row_sum,col_sum)
    return sum_dict

def data_preparation(a,b,adjacency_matrix=None,diag_cut=True,info=True,further_elimination=False):
    
    original = np.ones(shape=(a,b))#np.random.randint(2,size=(a,b)) if adjacency_matrix is None else adjacency_matrix
    if(info):
        print("Original: \n",original)
    
    if diag_cut:#eliminate reflexive connections
        for i in range(original.shape[0]):
            original[i][i]=0
    if info and diag_cut:
        print("original after setting diagonal to 0:\n",original)

    sort_idx = np.argsort(original.sum(axis=1))[::-1]
    sorted_matrix = original[sort_idx,:][:,sort_idx].copy()
    if info:
        print("Sorted Matrix: \n",sorted_matrix,"\n")
    old_count = None
    count_per_idx=[]
    for epoch in range(10):
        count_per_idx = sorted_matrix.sum(axis=1)
        print("EPOCH ",epoch)
        print("count_per_idx",count_per_idx)
        cut_idx = -1
        for i in range(len(count_per_idx)):
            if count_per_idx[i] < 3:
                cut_idx = i
                break
        if(cut_idx==-1):
            elimination = 0
        else:
            elimination =len(count_per_idx)-cut_idx
        print("\n\nlen(count_per_idx): ",len(count_per_idx)," cut_idx: ",cut_idx,"\n")
        print("Cropping Matrix to eliminate ",elimination," rows and columns")
        print(sorted_matrix)
        sorted_matrix = sorted_matrix[:cut_idx,:cut_idx].copy()
        sort_idx = (np.argsort(sorted_matrix.sum(axis=1))[::-1])[:cut_idx]
        sorted_matrix = sorted_matrix[sort_idx,:][:,sort_idx].copy()
        print("SORTED MATRIX: \n",sorted_matrix,"\n\n")
        count_per_idx = sorted_matrix.sum(axis=1)
        connection_matrix = np.zeros_like(sorted_matrix)
        for i in range(connection_matrix.shape[0]):#eventuell durch chape ersetzen
            for j in range(connection_matrix.shape[1]):
                if(sorted_matrix[i][j]==1) and count_per_idx[j]>2 and count_per_idx[i]>2:
                    connection_matrix[i][j]=count_per_idx[j]
                else:
                    continue
        print("CONNECTION MATRIX: \n",connection_matrix)
        if old_count is None:
            old_count = count_per_idx
            
            
        else:
            if old_count.shape == count_per_idx.shape:
                print("maximal bereinigt")
                break



    connection_matrix = np.zeros_like(sorted_matrix)
    for i in range(connection_matrix.shape[0]):#eventuell durch chape ersetzen
        for j in range(connection_matrix.shape[1]):
            if(sorted_matrix[i][j]==1) and count_per_idx[j]>2 and count_per_idx[i]>2:
                connection_matrix[i][j]=count_per_idx[j]
            else:
                continue

                # FURTHER ELIMINATION könnte helfen. eliminiere die zeilen, die weniger als 3 einträge haben in der conn-matrix haben
                # tracke die indices für die originalmatrix, erstelle einen view
                # du hast das bereits in den bool dicts, nimm einfach das selbe fenster
                # nimm diese dann als indizes, das geht ja irgendwie, wenn du ne matrix übergibst (bool)


    c = 0
    max_v = 0
    for i in count_per_idx:
        c+=1
        max_v = i if c >= i and max_v == 0 else max_v

    list_of_visited_nodes = {i:np.zeros_like(sorted_matrix) for i in range(max_v, 2,-1)}
    tier_matrices = create_tier_matrices(connection_matrix,count_per_idx)



    if info:
        print("adjacency_matrix\n",      sorted_matrix)
        print("connection_matrix\n->reduced to potential candidates with 3 or more connections\n",      connection_matrix)
        print("permutation_vector\n",      sort_idx)
        print("connections_per_node\n",      count_per_idx)
        print("maximally_possible_structure\n",      max_v)
        print("tier_boolean_matrices\n",      list_of_visited_nodes)

    tier_sum = sum_tier_lists(tier_matrices,info=info)

    return sorted_matrix, connection_matrix,sort_idx,count_per_idx,max_v,list_of_visited_nodes,tier_matrices,tier_sum




(
adjacency_matrix,#sortiert, oben dicht besetzte zeilen, unten alle zeilen mit mehr als 2 verbindungen.
connection_matrix,# statt 1 und 0 wird hier die anzahl der outgoing connections des verwiesenen nodes angezeigt. strategie: potentielle kandidaten für ein tier betrachten und andere zu verwerfen
permutation_vector,#welche nodes des originals wurden verwendet? hier originalnodes = zeilenvektoren. zeilenvektoren und ihre einträge in den spalten der anderen zeilenvektoren werden gelöscht
connections_per_node,#das ist der vektor, aus dem die matrix entstanden ist. dient als orientierung um tierklassen zu durchsuchen (wie viele zeilen kann man runtergehen)
maximally_possible_structure,#anhand der metainfo berechnete maximalle struktur
tracking_visits_per_tier_dict,#dictionary mit tier_label:np.zeros(nxn)
tier_boolean_matrices,#dictionary mit kandidatenverbindungen für das jeweilige tier. immer >=current_tier
tier_row_col_sums#dictionary mit tier_label:(summe_von_rows,summe_von_cols), in anderen Worten: (node_j_outgoing_connections, node_j_incoming_connections)
 ) = data_preparation(10,10,diag_cut=True)
    




# DIE DIAGONALE WENN VEKTOREN MITEINANDER GEXORT WERDEN UND SIE KEINE REFLEXIVEN VERBRINDUNGEN MEHR HABEN
# DANN IST DIE DIAGONALE GENAU DER ORT UM NACH DEM XOR NACHZUSCHAUEN OB SIE MITEINANDER VERBUNDEN SIND. WEIL BEIM ORIGINAL
# 0 INITIAL STEHEN WIRD, ABER WENN DER ANDERE VEKTOR MIT DIESEM VERBUNDEN IST, DANN WIRD ER DEN DIAGONALEN EINTRAG KIPPEN
# DER TRACE DER MATRIX GIBT UNS DIE MÖGLICHKEIT NACHZUPRÜFEN


# VERGLEICHE DIE WERTE DER CONN TABELLE miteinander!!! STARKER INDICATOR FÜR STRUKTUR

def get_matrx_sector(arr, row_range, col_range):
    return arr[row_range[0]:row_range[1],col_range[0]:col_range[1]]
# bei slicing einfach indexlisten übergeben


sector = get_matrx_sector(connection_matrix,(0,3),(0,10))
print("conn:\n",connection_matrix,"\n\n")
print("sector\n",sector)



print("connection_per_node:",connections_per_node)

# len(np.sum([x==current_size for x in range(start,stop)])) # bool summierung







"""
def create_intervalls(connections_per_node):
    result = {}
    start = 0
    for pos in range(len(connections_per_node)):
        if pos!=len(connections_per_node)-1:
            if connections_per_node[pos]==connections_per_node[pos+1]:
                continue
            else:
                result[int(connections_per_node[pos])]=(start,pos)
                start=pos+1
                continue
        else:
            result[int(connections_per_node[start])]=(start,len(connections_per_node)-1)
    return result

intervalls = create_intervalls(connections_per_node=connections_per_node)
print("Intervalls",intervalls)

"""
























