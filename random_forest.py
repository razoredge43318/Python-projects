import numpy as np
import csv

# This function computes entropy for information gain

def entropy(class_y):
    entropy = 0.0
    a,b,c,d = 0.0
    l = len(class_y)
    if l==0:
        l=1
    for x in class_y:
        if x == 0:
            a+=1
        else:
            b+=1
    c = a/l
    d = b/l
    if c != 0 and d != 0:
        entropy = abs(((c*np.log2(c))+(d*np.log2(d))))
    elif c == 0 and d != 0:
        entropy = abs((d*np.log2(d)))
    elif c != 0 and d == 0:
        entropy = abs((c*np.log2(c)))
    return entropy

# This function partitions a data matrix X and label list y based on split attribute or column and split value

def partition_classes(X, y, split_attribute, split_val):

    X_left = []
    X_right = []

    y_left = []
    y_right = []


    if isinstance(split_val, (int,float)) == True:
        for i in range(0,len(y)):
            if X[i][split_attribute]<=split_val:
                X_left.append(X[i])
                y_left.append(y[i])
            else:
                X_right.append(X[i])
                y_right.append(y[i])
    elif isinstance(split_val, (str)) == True:
        for i in range(0,len(y)):
            if X[i][split_attribute]==split_val:
                X_left.append(X[i])
                y_left.append(y[i])
            else:
                X_right.append(X[i])
                y_right.append(y[i])


    return (X_left, X_right, y_left, y_right)

# This function computes information gain after splitting previous_y label list into 2 sub-lists current_y[0] and current_y[1]

def information_gain(previous_y, current_y):

    info_gain = 0.0

    IG = entropy(previous_y)

    IGleft = entropy(current_y[0])

    IGright = entropy(current_y[1])

    leftprob = float(len(current_y[0]))/len(previous_y)

    rightprob = float(len(current_y[1]))/len(previous_y)

    info_gain = IG - (IGleft*leftprob+IGright*rightprob)

    return info_gain


class DecisionTree(object):
    def __init__(self):
        self.tree = {}
        self.val = 0
        pass

    def learn(self, X, y):
        #This method builds a tree recursively

        def tree_builder(X,y):

            if len(list(set(y))) == 1:
                return {'label':list(set(y))[0]}

            numrows = len(X)
            numcols = len(X[0])
            iglist = []
            split_val_list = []
            split_val_sublist = []
            igsublist = []

            for i in range(numcols):
                if isinstance(X[0][i], (int,float)) == True:
                    avg = sum([item[i] for item in X])/float(numrows)
                    Xleft,Xright,yleft,yright = partition_classes(X, y, i, avg)
                    ig = information_gain(y,[yleft,yright])
                    iglist.append(ig)
                    split_val_list.append(avg)
                elif isinstance(X[0][i], (str)) == True:
                    for j in list(set(item[i] for item in X)):
                        Xleft,Xright,yleft,yright = partition_classes(X, y, i, j)
                        ig = information_gain(y,[yleft,yright])
                        igsublist.append(ig)
                        split_val_sublist.append(j)
                    iglist.append(max(igsublist))
                    split_val_list.append(split_val_sublist[igsublist.index(max(igsublist))])

            colindex = iglist.index(max(iglist))

            splitval = split_val_list[iglist.index(max(iglist))]

            Xleft,Xright,yleft,yright = partition_classes(X, y, colindex, splitval)

            return {'split_attr':colindex, 'split_value':splitval, 'left': tree_builder(Xleft,yleft), 'right': tree_builder(Xright,yright)}

        self.tree = tree_builder(X,y)

        pass

    def classify(self, record):
        # This method classifies the record using self.tree and returns the predicted label

        def predict(treedict,record):

            if treedict.has_key('label'):
                self.val = treedict['label']
            else:
                for i,v in enumerate(record):
                    if isinstance(v, (int,float)) == True:
                        if v<= treedict['split_value'] and i== treedict['split_attr']:
                            predict(treedict['left'],record)
                        elif v> treedict['split_value'] and i== treedict['split_attr']:
                            predict(treedict['right'],record)
                    elif isinstance(v, (str)) == True:
                        if v== treedict['split_value'] and i== treedict['split_attr']:
                            predict(treedict['left'],record)
                        elif v!= treedict['split_value'] and i== treedict['split_attr']:
                            predict(treedict['right'],record)
            return self.val

        prediction = predict(self.tree,record)

        return prediction

        pass

class RandomForest(object):
    num_trees = 0
    decision_trees = []
    bootstraps_datasets = []
    bootstraps_labels = []

    def __init__(self, num_trees):
        self.num_trees = num_trees
        self.decision_trees = [DecisionTree() for i in range(num_trees)]


    def _bootstrapping(self, XX, n):
        #Creating a sample dataset of size n by sampling with replacement from the original dataset XX.
        samples = [] # sampled dataset
        labels = []  # class labels for the sampled records

        resample_index = list(np.floor(np.random.rand(n)*n).astype(int))

        for i in resample_index:
            samples.append(XX[i][0:-1])
            labels.append(XX[i][-1])
        return samples, labels


    def bootstrapping(self, XX):
        # Initializing the bootstap datasets for each tree
        for i in range(self.num_trees):
            data_sample, data_label = self._bootstrapping(XX, len(XX))
            self.bootstraps_datasets.append(data_sample)
            self.bootstraps_labels.append(data_label)


    def fitting(self):
        # Training `num_trees` decision trees using the bootstraps datasets
        for i in range(self.num_trees):
            self.decision_trees[i].learn(self.bootstraps_datasets[i], self.bootstraps_labels[i])
            print 'building tree number {}'.format(i+1)
        pass


    def voting(self, X):
        y = []

        for record in X:
            votes = []
            for i in range(len(self.bootstraps_datasets)):
                dataset = self.bootstraps_datasets[i]
                if record not in dataset:
                    OOB_tree = self.decision_trees[i]
                    effective_vote = OOB_tree.classify(record)
                    votes.append(effective_vote)

            counts = np.bincount(votes)

            if len(counts) == 0:
                yclassify = self.decision_trees[0].classify(record)
                y = np.append(y, yclassify)
                pass
            else:
                y = np.append(y, np.argmax(counts))

        return y

def main():
    X = list()
    y = list()
    XX = list()  # Contains data features and data labels
    numerical_cols = set([1, 2, 7, 10, 13, 14, 15]) # indices of numeric attributes (columns)

    # Loading data set
    print 'reading data'
    with open("data.csv") as f:
        next(f, None)

        for line in csv.reader(f, delimiter=","):
            xline = []
            for i in range(len(line)):
                if i in numerical_cols:
                    xline.append(ast.literal_eval(line[i]))
                else:
                    xline.append(line[i])

            X.append(xline[:-1])
            y.append(xline[-1])
            XX.append(xline[:])

    forest_size = 10

    # Initializing a random forest.
    randomForest = RandomForest(forest_size)

    # Creating the bootstrapping datasets
    print 'creating the bootstrap datasets'
    randomForest.bootstrapping(XX)

    # Building trees in the forest
    print 'fitting the forest'
    randomForest.fitting()

    # Calculating an unbiased error estimation of the random forest
    # based on out-of-bag (OOB) error estimate.
    y_predicted = randomForest.voting(X)

    # Comparing predicted and true labels
    results = [prediction == truth for prediction, truth in zip(y_predicted, y)]

    # Accuracy
    accuracy = float(results.count(True)) / float(len(results))

    print "accuracy: %.4f" % accuracy
    print "OOB estimate: %.4f" % (1-accuracy)


if __name__ == "__main__":
    main()

