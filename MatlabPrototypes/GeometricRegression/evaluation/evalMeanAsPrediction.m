evaluation = evaluationStruct;
evaluation.name = 'mean as label';

nbOfTrainingSamples = length(regressionInfo.trainingLabels);
leaveOneOutPrediction = zeros(nbOfTrainingSamples, 1);

for i = 1:nbOfTrainingSamples
    otherIndexes = 1:nbOfTrainingSamples;
    otherIndexes(:,i) = [];
    
    leaveOneOutPrediction(i) =...
        mean(regressionInfo.trainingLabels(otherIndexes,:));
end

evaluation.labels = leaveOneOutPrediction;
evaluation.meanSquaredError = ...
    mean((evaluation.labels - regressionInfo.trainingLabels).^2);

evaluations = [evaluations ; evaluation];