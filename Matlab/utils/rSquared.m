function r2 = rSquared(realLabels, predictions)
% Return the R^2 metric for 2 vector (real labels and predicted labels)
meanValue = mean(realLabels);
nbOfValues = size(realLabels,1);
meanVector = repmat(meanValue, nbOfValues, 1);

SSE = sum(sum((realLabels - predictions).^2));
SST = sum(sum((realLabels - meanVector).^2));

r2 = 1 - (SSE/SST);
end