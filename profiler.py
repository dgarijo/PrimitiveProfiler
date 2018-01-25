"""
This module attempts to create a profile detecting the preconditions needed for primitives
Created by Daniel Garijo
"""
from os import listdir
from os.path import isfile, join
import json
import pandas as pd
from d3m import index
import primitive_interfaces
import sys
import numpy as np

#Data: dataset to test (from the test datasets that illustrate different requirements)
#Primitive: primitive being tested. We assume it follows d3m interfaces
def passTest(data, primitive):
    target = data.iloc[:,-1]
    train = data.drop(data.columns[[len(data.columns)-1]], axis=1) #drop target column (the last one)
    #if (isinstance(primitive,primitive_interfaces.transformer.TransformerPrimitiveBase)): 
    #in theory the ifs simplify the tests, but many primitives extend an interface that is not the correct one.
    try:
        primitive.produce(inputs=train)
        return True
    except Exception as e2: 
        print("Exception just produce: ",e2)
    #elif (isinstance(primitive,primitive_interfaces.unsupervised_learning.UnsupervisedLearnerPrimitiveBase)): 
        try:
            primitive.produce(train[1])
            return True
    #Unsupervised
        except Exception as e: 
            print("Exception produce column",e)
            try:
                primitive.set_training_data(inputs=train)
                primitive.fit()
                primitive.produce(inputs=train)
                return True
            except Exception as e1:
                print("Exception fitproduce ",e1)
    #supervised
                try:
                    primitive.set_training_data(inputs=train,outputs=target)
                    primitive.fit()
                    primitive.produce(inputs=train)
                    return True
                except Exception as e:
                    print("Exception set fit produce",e)
                    return False

#Path: String with the path to the dataset folders. The system assumes to have two : clean_data and requirement_data 
#Primitive module name: string with the module name. E.g., 'sklearn.svm'
#Primitive name: class object of the primitive
def getPrimitiveRequirements(path, primitiveName, primitiveClass):
    CLEAN = path + "clean_data"
    REQ = path + "requirement_data"
    #Clean data files: all primitives should pass these tests
    data_clean_int = pd.read_csv(CLEAN +'/int_clean_data.csv')
    data_clean_float = pd.read_csv(CLEAN +'/float_clean_data.csv')
    data_clean_int.name = "CLEAN DATA INT" 
    data_clean_float.name = "CLEAN DATA FLOAT"
    prim = {}
    try:
        hyperparams_class = primitiveClass.metadata.query()['primitive_code']['class_type_arguments']['Hyperparams']
        #print(hyperparams_class.defaults())
        primExec = primitiveClass(hyperparams=hyperparams_class.defaults())
    except:
        print("Error while loading primitive" + primitiveName)
        prim["Error"] = ["COULD-NOT-LOAD-PRIMITIVE"]
        return prim
    
    #if not hasattr(primExec, 'produce'):
    #    print("Primitive does not have produce method. No requirements considered")
    #    return -1
    passed = (passTest(data_clean_int, primExec)) and (passTest(data_clean_float, primExec))
    if(not passed):
        print("The primitive "+primitiveName+" cannot execute the clean datasets. No further requirements addressed")
        prim["Error"] = ["COULD-NOT-LOAD-TABULAR-DATA"]
        return prim
        
    onlyfiles = [f for f in listdir(REQ) if isfile(join(REQ, f))]
    requirements = []
    for d in onlyfiles:
        data = pd.read_csv(REQ+"/"+d)
        data.name = d
        passed = passTest(data, primExec)
        if ("missing" in data.name) and (not passed) and ("NO_MISSING_VALUES" not in requirements):
            #print("Primitive cannot handle missing values")
            requirements.append("NO_MISSING_VALUES")
        if ("categorical" in data.name) and (not passed) and ("NO_CATEGORICAL_VALUES" not in requirements):
            #print("Primitive cannot handle string/categorical values")
            requirements.append("NO_CATEGORICAL_VALUES")
        if ("unique" in data.name) and (not passed) and ("NOT_UNIQUE" not in requirements):
            #print("Primitive cannot handle having a column of unique values")
            requirements.append("NOT_UNIQUE")
        if ("negative" in data.name) and (not passed) and ("POSITIVE_VALUES" not in requirements):
            #print("Primitive cannot handle negative values")
            requirements.append("POSITIVE_VALUES")
        #if(array):
        #    #prim.isArray = True
        #    prim["IsArray"] = True
    prim["Requirements"] = requirements

    return prim


    
#Main script        
DATADIR = "data_profiler/" #Dir with the profiling datasets
d = {}
for primitive_name, primitive in index.search().items():
    #print ("Detecting requirements for : " +primitive_name)
    #if(primitive_name == "d3m.primitives.common_primitives.PCA"):
    #if(primitive_name == "d3m.primitives.test.SumPrimitive"):
    
        #print ("   " + json.dumps(getPrimitiveRequirements(DATADIR,primitive_name, primitive)))
    d[primitive_name] = getPrimitiveRequirements(DATADIR,primitive_name, primitive)
print (json.dumps(d))
    

