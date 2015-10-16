function [accuracies, losses] = KNNiter( filename, ks )
%Iterate through parameters (k and distance function)

Xtrain = csvread(strcat('trainX_', filename));
Ytrain = csvread(strcat('trainY_', filename));
Xtest = csvread(strcat('testX_', filename));
Ytest = csvread(strcat('testY_', filename));

accuracies = [[]];
losses = [[]];
for i=1:8
    k = ks(i);
    disp(num2str(k))
    [acc,loss] = KNN(Xtrain, Ytrain, Xtest, Ytest, 'cosine', k, 'exhaustive');
    accuracies(i,1) = acc;
    losses(i,1) = loss;
    %[acc,loss] = KNN(Xtrain, Ytrain, Xtest, Ytest, 'euclidean', k, 'kdtree');
    %accuracies(i,2) = acc;
    %losses(i,2) = loss;
    [acc,loss] = KNN(Xtrain, Ytrain, Xtest, Ytest, 'correlation', k, 'exhaustive');
    accuracies(i,3) = acc;
    losses(i,3) = loss;
    %[acc,loss] = KNN(Xtrain, Ytrain, Xtest, Ytest, 'jaccard', k, 'exhaustive');
    %accuracies(i,4) = acc;
    %losses(i,4) = loss;
    [acc,loss] = KNN(Xtrain, Ytrain, Xtest, Ytest, 'spearman', k, 'exhaustive');
    accuracies(i,5) = acc;
    losses(i,5) = loss;
end

end

