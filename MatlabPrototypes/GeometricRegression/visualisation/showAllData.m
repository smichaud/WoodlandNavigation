nbOfSamples = length(dataset);
for i=1:nbOfSamples
    showSingleData(dataset(i), areaOfInterest);
    uiwait;
end


