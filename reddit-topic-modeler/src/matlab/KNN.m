function [accuracy,kloss] = KNN(Xtrain, Ytrain, Xtest, Ytest, distance, k, nsmethod)
  
   model = ClassificationKNN.fit(Xtrain, Ytrain, 'distance', distance, 'NSMethod', nsmethod);
   model.NumNeighbors = k;
   
   xvalmodel = crossval(model, 'kfold', 5);
   kloss = kfoldLoss(xvalmodel);
   
   predictions = [];
   for i=1:size(Xtest,1)
       predictions(i) = predict(model, Xtest(i,:));
   end
   
   accuracy = sum(predictions' == Ytest)/size(Ytest,1);
end

