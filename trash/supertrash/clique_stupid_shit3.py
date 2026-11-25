import numpy as np
import time
np.random.seed(int(time.time_ns()%10000))

def test_adjacency(a,b,diag_cut=False):
    original = np.random.randint(2,size=(a,b))
    sort_idx = np.argsort(original.sum(axis=1))[::-1]
    sorted_matrix = original[sort_idx,:][:,sort_idx]
    count_per_idx = sorted_matrix.sum(axis=1)
    if diag_cut:#eliminate reflexive connections
        for i in range(len(sorted_matrix)):
            if sorted_matrix[i][i]!=0:
                sorted_matrix[i][i]=0
                if count_per_idx[i]>0:
                    count_per_idx[i]-=1
                #connection_matrix[i][i]=0
    connection_matrix = np.zeros_like(sorted_matrix)
    for i in range(len(sorted_matrix[0])):
        for j in range(len(sorted_matrix[1])):
            if(sorted_matrix[i][j]==1):
                connection_matrix[i][j]=count_per_idx[j]

    c = 0
    max_v = 0
    for i in count_per_idx:
        c+=1
        max_v = i if c >= i and max_v == 0 else max_v

    list_of_visited_nodes = {i:np.zeros_like(sorted_matrix) for i in range(max_v, 2,-1)}

    return sorted_matrix, connection_matrix,sort_idx,count_per_idx,max_v,list_of_visited_nodes




sorted,conns,idx,count,max_c,visited_dict = test_adjacency(10,10,diag_cut=True)
    


def get_info(sorted,conns,idx,count,max_c,visited_dict,big=False):
    print("Transformed Matrix:\n",sorted,"\n")
    print("Candidate Matrix:\n",conns,"\n")
    print("Node-Connection amount:",count,"\n")
    print("Maximum size of possible structure:",max_c,"\n")
    print("Permutation:",idx)
    if big:
        for key in visited_dict.keys():
            print(f"Visited so far: {key}\n",visited_dict[key],"\n**************\n\n")


get_info(sorted,conns,idx,count,max_c,visited_dict,big=True)


def create_tier_matrices(conns,count):
    collect = {}
    for i in range(count[0],2,-1):
        collect[i]=(conns>=i)
    return collect
#hier cols durchzählen, summieren, schauen ob's passt

tier_dict = create_tier_matrices(conns,count)

def sum_tier_lists(tier_dict):
    sum_dict = {}
    for key in tier_dict.keys():
        row_sum = tier_dict[key].sum(axis=1)
        col_sum = tier_dict[key].sum(axis=0)
        print("RowSum:",row_sum,"\nColSum",col_sum,"\n----------------------\n")

        print(f'Tier: {key}\n{tier_dict[key]}\n')
        print("#####################################")
        sum_dict[key]=(row_sum,col_sum)
    return sum_dict

sum_dict = sum_tier_lists(tier_dict)
print(conns)



def xor_and_matrices(matrix_A, matrix_B):# A=True, B = False
    matrix_C = matrix_A ^ matrix_B
    matrix_C = matrix_C & matrix_A
    return matrix_C


# or die listen, die für den aktuellen wert und den werten darüber entsprechen
# vielleicht ganzen spaltenvektoren -1 hinzufügen, sobald ein max_c kandidat ausgeschieden ist. bringt das was?
# ja, bringt was. sobald n zeilenvektor ausgeschieden ist, reduziere alle zahlen in der conn matrix in der gleich-
# wertigen spalte um -1
#NUR BEI UNGERICHTETEN GRAPHEN FUCK


# or die listen, die für den aktuellen wert und den werten darüber entsprechen
# vielleicht ganzen spaltenvektoren -1 hinzufügen, sobald ein max_c kandidat ausgeschieden ist. bringt das was?
# ja, bringt was. sobald n zeilenvektor ausgeschieden ist, reduziere alle zahlen in der conn matrix in der gleich-
# wertigen spalte um -1
#NUR BEI UNGERICHTETEN GRAPHEN FUCK


#aber wir können truncaten


#aber wir können truncaten

def truncate():
    pass

def search():


    pass





for i in count:
    pass
    #print(xor_and_matrices(tier_dict[i]),tier_dict[i])

















"""
def step(sorted,conns,idx,count,max_c,visited_list,min_c=3):


    candidates_max = []
    candidates_below = []
    for current_c in range(max_c,min_c,-1):
        for row in range(max_c,min_c-1,-1):
            counter = 0
            temp_candidates = []
            for col in range(conns.shape[1]):
                if conns[row][col]<current_c and conns[row][col]>min_c:
                    #AUSLÖSCHEN. BEIM BETRETEN CONNECTIONS CUTTEN, TODO
                    continue
                elif conns[row][col]>=current_c:
                    temp_candidates.append((row,col))
                    continue
                else:
                    conns[row][col]=0
            if len(temp_candidates)>=current_c:
                # geh sie durch und schau,ob c vorhanden ist
                print("Jep, ",len(temp_candidates))
            elif True:
                # geh doch erstmal die ganzen matrizen durch und prüf einfach für jede matrize ob dort die bedingung 
                # min_c < element < max_c... du weißt schon, die boolean tabellen. dann extrahierst du noch mehr info
                # und mit den matrizen werden wir arbeiten.

                # matrizenweises xor und dann and mit einem original. 
                # xor um ungleiche werte zu filtern und and zur bestätigung der richtigen elemente.
                # dann elemente zählen/wählen
                #vergiss nicht, wir arbeiten hier mit boolean matrizen, die auf zahlenwerte geprüft wurden. war in der vorbereitung
                #immer noch in polynomial space und polynomial time, nix crazy hier. mehrere kopien sind vll unwirklich, aber machbar.
                # wir haben jetzt die metainformationen für jede nachbarschaftsbeziehung
                #das and mit der oberen originalmatrix anwenden und nicht mit dem darunterliegenden tier

                #vergiss nicht meta-infos rauszugeben in form von vektoren, die die information bündeln
                # welche zeilen wie viele einträge in ihrem jeweiligen tier haben.
                # also weitere metainfo ohne nachzuschauen als vektoren.

                    


            pass


"""



























