
import gzip
import random
import warnings
import jsonlines
import jsonlines
from gensim.models import word2vec, Word2Vec
import re
import numpy as np
import os
import json
import sys

from sklearn import decomposition

warnings.filterwarnings("ignore")


def w2v(filename,cwetype):
    print("generating word2vec...")
    if os.path.exists(os.path.split(filename)[0]+"/" + "word2vec_" + str(cwetype) + ".pkl"):
        print("Word2Vec already exists!")
        return
    words = []
    for root, dirs, files in os.walk(filename):  
      
        np.random.shuffle(files)
        for file in files:
            flag_vec = 0
            word = []
            with open(os.path.join(root + "/" + file), "r") as f:
                print(root + "/" + file)
                for line in f.readlines():
                    if "-" * 20 in line:
                        flag_vec = 1

                    if flag_vec == 1:  
                        if "^" * 20 in line:
                            for i in word:
                                words.append(i)
                           
                        if re.search('(?<=,).*', line):
                           
                            word.append(re.search('(?<=,).*', line).group().split(')')[0].split(" "))  # 将token加入数组
    model = Word2Vec(words, min_count=1, size=100, sg=1, window=5,
                     negative=3, sample=0.001, hs=1, workers=4)

    model.save(os.path.split(filename)[0]+"/"+ "word2vec_" + str(cwetype) + ".pkl")
    print("Word2Vec is ready")

def GetInfor(filename):
    print("\ngenerating vectors files...")
    import gzip
    random_use=np.random.rand(100)
    files_test = []
    for root, dirs, files in os.walk(filename): 
        np.random.shuffle(files)
        filenum = len(files)
        count = 0
        save = 0
        for fname in files:
           
            adj_ast_total = []
            adj_child = []
            adj_com = []
            adj_next = []
            adj_guared = []
            adj_lexical = []
            adj_jump = []
           
            adj_cdfg_a = []
            adj_cdfg_c = []
            adj_cdfg_p = []
            
            # init
            label_label = False
            label_child = False  # child
            label_from = False  # compute_form
            label_next = False  # next_token
            label_by = False  # garde_by
            label_negation = False  # garde_negation
            label_att = False  # node_attribute
            label_use = False  # Lexical_use
            label_jump = False  # jump
            label_joern = False  # cdfg
            label_joern_word = False # joern_word
            joern_word = []
            
            with open(root +'/'+ fname, "r") as f:
                data = f.readlines()
                for line in data:
                    if (line.strip().find("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^") >= 0): 
                        break
                    
                    nodes = line.split('\n')[0].split(',')
                    if (line.find("-----label-----") >= 0):
                        label_label = True
                        continue
                    if (label_label):
                        label_single = line.strip()
                        label_label = False
                        continue

                    if (line.find("-----children-----") >= 0):
                        label_child = True
                        continue
                    if (label_child):
                        if line.find("-----nextToken-----") >= 0:
                            label_child = False
                        else:
                            adj_child.append((int(nodes[0]), int(nodes[1])))

                    if (line.find("-----nextToken-----") >= 0):
                        label_next = True
                        continue
                    if (label_next):
                        if line.find("-----computeFrom-----") >= 0:
                            label_next = False
                        else:
                           
                            for i in range(len(nodes)):
                                if i != len(nodes) - 1:
                                    adj_next.append((int(nodes[i]), int(nodes[i + 1])))

                    if (line.find("-----computeFrom-----") >= 0):
                        label_from = True
                        continue
                    if (label_from):
                        if line.find("-----guardedBy-----") >= 0:
                            label_from = False
                        else:
                            adj_com.append((int(nodes[0]), int(nodes[1])))

                    if (line.find("-----guardedBy-----") >= 0):
                        label_by = True
                        continue
                    if (label_by):
                        if line.find("-----guardedByNegation-----") >= 0:
                            label_by = False
                        else:
                            adj_guared.append((int(nodes[0]), int(nodes[1])))

                    if (line.find("-----guardedByNegation-----") >= 0):
                        label_negation = True
                        continue
                    if (label_negation):
                        if line.find("-----lastLexicalUse-----") >= 0:
                            label_negation = False
                        else:
                            adj_guared.append((int(nodes[0]) , int(nodes[1])))

                    if (line.find("-----lastLexicalUse-----") >= 0):
                        label_use = True
                        continue
                    if (label_use):
                        if line.find("-----jump-----") >= 0:
                            label_use = False
                        else:
                            adj_lexical.append((int(nodes[0]), int(nodes[1])))

                    if (line.find("-----jump-----") >= 0):
                        label_jump = True
                        continue
                    if (label_jump):
                        if line.find("-----attribute-----") >= 0:
                            label_jump = False
                        else:
                            adj_jump.append((int(nodes[0]), int(nodes[1])))

                    if (line.find("-----attribute-----") >= 0):
                        label_att = True
                        continue
                    if (label_att):
                        if line.find("-----ast_node-----") >= 0:
                            label_att = False
                        else:
                            num = line.split(';')
                            for x in num:
                                if (x == "" or x == '\n'):
                                    num.remove(x)
                            nodeNum = len(num)
                            label_adj = False
                           
                    if (line.find("-----joern-----") >= 0):
                        label_joern = True
                        continue
                    if (label_joern):
                        if line.find("-----------------------------------") >= 0:
                            label_joern = False
                        else:
                            threedot = line.strip().split("(")[1].split(")")[0].split(",") 
                            try:
                                adj_single = (int(threedot[0]), int(threedot[1]))

                                if int(threedot[2]) == 0:
                                    adj_cdfg_c.append(adj_single)
                                    continue
                                if int(threedot[2]) == 1:
                                    adj_cdfg_c.append(adj_single)
                                    continue
                                if int(threedot[2]) == 2:
                                    adj_cdfg_c.append(adj_single)
                                    continue
                            except:
                                continue 
                                
                    if line.find("-----------------------------------") >= 0:
                        label_joern_word = True
                        continue
                    if (label_joern_word):
                        if re.search('(?<=,).*', line):
                            joern_word.append(re.search('(?<=,).*', line).group().split(')')[0])


          
            i = 0
            while i < len(adj_child):
                l1 = adj_child[i][0]
                l2 = adj_child[i][1]
                if l1 >= len(num) or l2 >= len(num):
                    adj_child.remove((l1, l2))
                i = i + 1

            i = 0
            while i < len(adj_com):
                l1 = adj_com[i][0]
                l2 = adj_com[i][1]
                if l1 >= len(num) or l2 >= len(num):
                    adj_com.remove((l1, l2))
                i = i + 1

            i = 0
            while i < len(adj_next):
                l1 = adj_next[i][0]
                l2 = adj_next[i][1]
                if l1 >= len(num) or l2 >= len(num):
                    adj_next.remove((l1, l2))
                i = i + 1

            i = 0
            while i < len(adj_guared):
                l1 = adj_guared[i][0]
                l2 = adj_guared[i][1]
                if l1 >= len(num) or l2 >= len(num):
                    adj_guared.remove((l1, l2))
                i = i + 1

            i = 0
            while i < len(adj_lexical):
                l1 = adj_lexical[i][0]
                l2 = adj_lexical[i][1]
                if l1 >= len(num) or l2 >= len(num):
                    adj_lexical.remove((l1, l2))
                i = i + 1

            i = 0
            while i < len(adj_jump):
                l1 = adj_jump[i][0]
                l2 = adj_jump[i][1]
                if l1 >= len(num) or l2 >= len(num):
                    adj_jump.remove((l1, l2))
                i = i + 1

          
            vectors_cdfg = []
            model = word2vec.Word2Vec.load(
                os.path.split(filename)[0] + "/word2vec_" + str(os.path.split(filename)[1]) + '.pkl')

            for i in range(len(joern_word)):

                word_single = joern_word[i].split(" ")
               
                try:
                    vector = model.wv[word_single]  # 查词
                except:
                    vector = np.reshape(random_use, (1, 100))
                    
                if np.size(vector) > 100: 
                    vector = vector.T
                    kpca = decomposition.KernelPCA(kernel='rbf', gamma=10, n_components=1)
                  
                    vector = kpca.fit_transform(vector).T

                vector = vector[-1, 0:100]
                vectors_cdfg.append(vector.tolist())
           
            vectors = []
        
            with open(os.path.split(filename)[0]+"/our_map_all.txt", "r") as f:
                s = f.read()
                s = s.replace('\'', '\"')
                mapping = json.loads(json.dumps(eval(s)))
            for i in range(len(num)):
                vector = []
                word_single = num[i]
                try:
                    vector = mapping[word_single]
                except:
                    vector = random_use.tolist()
                vectors.append(vector)
            label = int(label_single) + 0.0

            adj_singel = []
            adj_ast_total.append(adj_singel)
            adj_singel = [adj_cdfg_c]
            adj_cdfg_total = []
            adj_cdfg_total.append(adj_singel)
            
            with jsonlines.open(os.path.split(filename)[0]+'/'+str(os.path.split(filename)[1])+'_ast.jsonl', mode='a') as writer:
                writer.write(
                            {"Property": label, "graph": {"node_features": vectors, "adjacency_lists": adj_ast_total[0]}})
            with jsonlines.open(os.path.split(filename)[0]+'/'+str(os.path.split(filename)[1])+'_cdfg.jsonl', mode='a') as writer:
                writer.write(
                            {"Property": label, "graph": {"node_features": vectors_cdfg, "adjacency_lists": adj_cdfg_total[0]}})
            count = count + 1
            print("\rprocess : {:.2f}".format((count / (1.0 * files.__len__()) * 100)) + "%",end=' ')

    print("vectors files is ready")
    
def mkdir(path):
   
    import os
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path + ' ready now')
        return True
    else:
        print(path + ' already')
        return False
    
def Split(train,valid,test,path):
    print("\nspliting datasets...")
    tem_ast=[]
    mkdir(os.path.split(path)[0]+'/'+'tem_'+os.path.split(path)[1]+'/ast')
    with open(os.path.split(path)[0] + '/' + str(os.path.split(path)[1]) + '_ast.jsonl', "r+", encoding="utf8") as f:
        for item in jsonlines.Reader(f):
            tem_ast.append(item)
            
    randomtem = np.arange(len(tem_ast))
    pos_tem=[]
    neg_tem=[]

    for step,i in enumerate(randomtem):
        ast=tem_ast[i]
        if ast['Property']==0:
            neg_tem.append(ast)
        else:
            pos_tem.append(ast)
    length=min(len(pos_tem),len(neg_tem))
    neg_tem=neg_tem[:length]
    pos_tem=pos_tem[:length]

    tem_train=neg_tem[:int(length*train)]+pos_tem[:int(length*train)]
    np.random.shuffle(tem_train)
    tem_valid=(neg_tem[int(length * train):int(length * (train+valid))])+(pos_tem[int(length * train):int(length * (train+valid))])
    np.random.shuffle(tem_valid)
    tem_test=(neg_tem[int(length * (train+valid)):])+(pos_tem[int(length * (train+valid)):])
    np.random.shuffle(tem_test)
    path_tem=os.path.split(path)[0]+'/'+'tem_'+os.path.split(path)[1]+'/ast/ast.jsonl'
    for i in tem_train:
        with jsonlines.open(path_tem,
                            mode='a') as writer:
            writer.write(i)
    f_in = open(path_tem, 'rb')
    f_out = gzip.open(os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/ast/train.jsonl.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(path_tem)

    for i in tem_valid:
        with jsonlines.open(path_tem,
                            mode='a') as writer:
            writer.write(i)
    f_in = open(path_tem, 'rb')
    f_out = gzip.open(os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/ast/valid.jsonl.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(path_tem)

    for i in tem_test:
        with jsonlines.open(path_tem,
                            mode='a') as writer:
            writer.write(i)
    f_in = open(path_tem, 'rb')
    f_out = gzip.open(os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/ast/test.jsonl.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(path_tem)
    tem_cdfg=[]
    mkdir(os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/cdfg')
    with open(os.path.split(path)[0]+'/'+str(os.path.split(path)[1])+'_cdfg.jsonl', "r+", encoding="utf8") as f:
        for item in jsonlines.Reader(f):
            tem_cdfg.append(item)
            
    randomtem = np.arange(len(tem_cdfg))
    pos_tem=[]
    neg_tem=[]

    for step,i in enumerate(randomtem):
        ast=tem_cdfg[i]
        if ast['Property']==0:
            neg_tem.append(ast)
        else:
            pos_tem.append(ast)
    length=min(len(pos_tem),len(neg_tem))
    neg_tem=neg_tem[:length]
    pos_tem=pos_tem[:length]
    

    tem_train=neg_tem[:int(length*train)]+pos_tem[:int(length*train)]
    np.random.shuffle(tem_train)
    tem_valid=(neg_tem[int(length * train):int(length * (train+valid))])+(pos_tem[int(length * train):int(length * (train+valid))])
    np.random.shuffle(tem_valid)
    tem_test=(neg_tem[int(length * (train+valid)):])+(pos_tem[int(length * (train+valid)):])
    np.random.shuffle(tem_test)
    path_tem=os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/cdfg/cdfg.jsonl'
    for i in tem_train:
        with jsonlines.open(path_tem,
                            mode='a') as writer:
            writer.write(i)
    f_in = open(path_tem, 'rb')
    f_out = gzip.open(os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/cdfg/train.jsonl.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(path_tem)

    for i in tem_valid:
        with jsonlines.open(path_tem,
                            mode='a') as writer:
            writer.write(i)
    f_in = open(path_tem, 'rb')
    f_out = gzip.open(os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/cdfg/valid.jsonl.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(path_tem)

    for i in tem_test:
        with jsonlines.open(path_tem,
                            mode='a') as writer:
            writer.write(i)
            
    f_in = open(path_tem, 'rb')
    f_out = gzip.open(os.path.split(path)[0] + '/' + 'tem_'+os.path.split(path)[1]+'/cdfg/test.jsonl.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(path_tem)
    print("data ready")

   
def Preprocess(path):
    cwetype = os.path.split(path)[1]
 
    os.path.split(path)[0] + '/' + str(os.path.split(path)[1]) + '_ast.jsonl'
    
    a=os.path.split(path)[0]+'/'+str(os.path.split(path)[1])+'_ast.jsonl'
    if os.path.exists(os.path.split(path)[0]+'/'+str(os.path.split(path)[1])+'_ast.jsonl') and os.path.exists(os.path.split(path)[0]+'/'+str(os.path.split(path)[1])+"_cdfg.jsonl"):
        Split(0.8,0.1,0.1,path)
    else:
        GetInfor(path)
        Split(0.8, 0.1, 0.1, path)
