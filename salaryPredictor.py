#!/usr/bin/python
#
#   Assignment 1, Salary Prediction v2
#
#   Alan Haverty,   Program to extract data from URL
#   C12410858       Weight the discrete values 
#   DT211/2         Calculate whether person is likely to earn >50k or <50k
#

import urllib.request

"""BEGIN FUNCTION LIST"""

def collect_discrete(discrete_attr,value):
    """
    Function: collect_discrete
    ----------------------------
    Adds an element into its respective key in dictionary
 
    discrete_attr:  Dictionary that counts how many elements
                    per attribute for weighting.
                    
    value:          The elements value i.e unemployed
 
    returns: Dictionary with count of each element of attribute
    """
    if value in discrete_attr:
        discrete_attr[value] += 1;
    else:
        discrete_attr[value] = 1;
    return(discrete_attr);


def weight_discrete(discrete_attr):
    """
    Function: weight_discrete
    ----------------------------
    Weights the completed dictionary's attributes
 
    discrete_attr:  Pass of the elements to be weighted
 
    returns: Dictionarys of attribute weights
    """
    attr_weight={};
    discrete_total = sum(discrete_attr.values())
    
    for key,value in discrete_attr.items():
        weight_value=value/discrete_total
        attr_weight[key]=weight_value;

    return(attr_weight);

"""END FUNCTION LIST"""


def main():

    # Allow user to choose which source to read from [a or b]
    url_type=input("Choose Data Source:\nOnline File (Slow): a\nLocal File  (Fast): b\n: ")
    if url_type=='a':
        URL = "http://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
    else:
        URL = "sampledata.txt"

    f, h = urllib.request.urlretrieve(URL)
    print(h.as_string())
    file = open(f, 'r')

    # Count how many lines are in the file, for dividing into training and test
    # Gets 70% of the file for training purposes
    num_lines = sum(1 for line in file)
    training_len = int((num_lines/100)*70)

    attr_weight={};
    # Define the columns ID's for with discrete values
    discrete_cols=(1,5,6,7,8,9)
    # Define the columns ID's for all workable columns
    working_cols=(0,1,4,5,6,7,8,9,10,11,12)

    # Creating two 2D dictionaries for weights values
    weight_matrix = [{} for k in range(0,15)];
    weight_attribute = [{} for j in range(0,15)];

    count=0
    row_count=[0,1]


    """ WEIGHTING DISCRETE ATTRIBUTES """
    """ DESCRIPTION:
        Reset cursor to 0.
        Split row into values.
        Cycle through the dicsrete columns and collect the data for later weighting.
        Break at 70% of file.
        Weight the values that have been collected
    """
    file.seek(0)
    for row in file:
        split_row = row.split(', ')

        # Weight only the elements in each rows discrete columns
        for i in discrete_cols:
            weight_attribute[i]=collect_discrete(weight_attribute[i], split_row[i]);

        # Break training for loop at 70% of file
        count+=1
        if(count>training_len):
            break;

    # Weight the collected data values
    for i in discrete_cols:  
        weight_matrix[i]=weight_discrete(weight_attribute[i]);


    """ TRAINING DATA """
    file.seek(0)
    count=0
    row_count[1]=0;
    # Create 2D array for >50K & <50K attribute averages
    sal_att_average=[[0 for j in range(13)] for i in range(2)]
    midpoint_matrix=[]
    direction_mid=[]

    for row in file:
        element = row.split(', ')

        # Flag salary class for current row
        if element[14] == '<=50K\n':
            #Row is in <=50k class
            salary_class=0;
        else:
            #Row is in >50k class
            salary_class=1;

        # attr_flat = integer value of the current [col][row]
        for col in working_cols:
            if element[col] in weight_matrix[col]:
                # If descrete attribute then return integer weight value
                attr_flat=weight_matrix[col][element[col]]
            else:
                #else for non-discrete columns
                attr_flat=element[col]

            # Adds total of attributes values to array[>50k OR <50k)][column]
            sal_att_average[salary_class][col] += float(attr_flat)

        row_count[salary_class]+=1;

        #Break training at 70% of file
        count+=1
        if(count>training_len):
            break;

    # Get average of <=>50K lists
    for j in range(0,2):
        for i in working_cols:
            sal_att_average[j][i]=sal_att_average[j][i]/row_count[j]
            

    """ MIDPOINTS """
    # Incase <50k has midpoints higher than >=50k list
    # e.g <50k average age is higher than >=50k average age,
    # then direction will be = -1
    
    # Record which COL is going in different direction
    for i in range(0,13):
        if (sal_att_average[1][i]-sal_att_average[0][i]) < 0:
            direction_mid.append(-1)
        else:
            direction_mid.append(1)
        
        midpoint_matrix.append((sal_att_average[0][i]+sal_att_average[1][i])/2)


    """ TESTING DATA """
    perc_count=0
    correct=0
    incorrect=0
    for row in file:
        
        count+=1
        temp_attr_win=0;
        element = row.split(', ')

        ## Breaks before EOF as there were three blank lines at end causing bugs
        if element[0] == '\n':
            break;
            
        # attr_flat = integer value of the current [col][row]
        for col in working_cols:
            if element[col] in weight_matrix[col]:
                # If descrete attribute then return integer weight value
                attr_flat=weight_matrix[col][element[col]]
            else:
                #else for non-discrete columns
                attr_flat=element[col]

            # Compares attr_flats with the attributes midpoints
            # also adjusting for the direction of the midpoints
            if float(attr_flat) >= midpoint_matrix[col]:
                temp_attr_win = temp_attr_win +(1*direction_mid[col])
            else:
                temp_attr_win = temp_attr_win +(-1*direction_mid[col])


        ### Check if correct or incorrect ###
        ###   +1 is >50k || -1 is <50k    ###

        # Count total rows tested
        perc_count+=1

        # If total attribute wins are UP
        # and the salary matches
        # then its correct else incorrect
        if (int(temp_attr_win) > 0):
            if element[14]=='>50K\n':
                correct+=1
            else:
                incorrect+=1

        # If total attribute wins are DOWN
        # and the salary matches
        # then its correct else incorrect
        else:
            if element[14]=='<=50K\n':
                correct+=1
            else:
                incorrect+=1

                
    
    print("correct",correct,"|","incorrect",incorrect,"|","count",perc_count)
    # CALCULATE ACCURACY
    accuracy_score=(correct/perc_count)*100
    print("%.2f" %accuracy_score,"% accuracy for Test section.")

if __name__ == "__main__":
    main()
