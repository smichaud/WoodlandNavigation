% This is the main script, run it and answer the questions !
tic

% Set the 'justRunAll' to true to run all the script (unsupervised run)
justRunAll = false;

rng(1987,'twister'); % Seed for random number generator

if justRunAll || ~exist('dataset','var') ...
        || strcmp(questdlg('Reset all ?', '','Yes','No','No'),'Yes')
    % ========== Init/Reset ===============================================
    clc;
    clearvars -except 'justRunAll';
    close all;
    clc;
    addpath(genpath('.'));
    addpath(genpath('../Utils/'));
    
    % ========== Define global variables and data structures ==============
    dataDirectory = '../../../WoodlandNavigationData/RegressionV2/';
    datasetName = 'data.mat';
    %     slopeCorrectionFile = '../Data/SlopeCorrection/slopeCorrection.mat';
    %     load(slopeCorrectionFile);
    
    dataset = []; % Variable to contain the dataset
    regressor = []; % Variable to contain the regressor
    
    robotSpeed = 0.3; % m/s
    areaOfInterest = struct(...
        'distFromRobot', 1.0,...
        'depth', 2.6,...
        'width', 1.0,...
        'height', 1.4,...
        'xTfAdjustment', 0.00,... % base_link + adjust = body front
        'groundThreshold', 0.12); % Lower than half wheel and robot body
    
    traversabilityCostInfo = struct(...
        'wantToCorrectSlope', false,...
        'motorCurrentsIntegralMetric', 1,...
        'motorCurrentsVarianceMetric', 2,...
        'inertiaVarianceMetric', 3,...
        'odometryErrorMetric', 4,...
        'randomValueMetric', 5,...
        'traversabilityMetrics', 4);
    
    datasetStruct = struct(...
        'name', '',...
        'rawCurrents', [],...
        'dftCurrents', [],...
        'rawIMU', [],...
        'dftIMU', [],...
        'rollPitchYaw', [],...
        'icpOdometry', [],...
        'traversabilityStartTime', [],...
        'traversabilityStopTime', [],...
        'traversabilityCost', [],...
        'userTraversabilityCost', [],...
        'rawPointCloud', [],...
        'groundHeight', [],...
        'areaOfInterest', [],...
        'image', [],...
        'features', containers.Map);
    regressionInfo = struct(...
        'featureNames', [],...
        'featuresImportance', [],...
        'trainingFeatures', [],...
        'trainingLabels', [],...
        'testFeatures', [],...
        'testLabels', [],...
        'nbOfTrees', 500,...
        'nbOfLeaves', 5);
    evaluationStruct = struct(...
        'name', [],...
        'labels', [],...
        'meanSquaredError', [],...
        'rSquared', []);
    evaluations = []; % To store all leaveresults
    
    testRegressor = [];
end

if justRunAll || isempty(dataset) ||...
        strcmp(questdlg('Reload data ?', '','Yes','No','No'),'Yes')
    if ~justRunAll &&...
            exist(strcat(dataDirectory, 'data.mat'), 'file') == 2 && ...
            strcmp(questdlg('Load from .mat ?', '','Yes','No','Yes'),'Yes')
        loadSavedData;
    else
        loadRawData;
        computeImuDft;
        computeCurrentsDft;
        extractTraversabilityCost; % add the label to the structure
        extractAreaOfInterest; % point cloud area of interest
        extractAllFeatures;
    end
end

if ~justRunAll && strcmp(questdlg('Show all processed samples ?',...
        '','Yes','No','No'),'Yes')
    showDataset;
end

prepareDataForRegression;
if justRunAll || ...
        strcmp(questdlg('Analyse data ?', '','Yes','No','Yes'),'Yes')
    findLeafSize;
    estimateFeatureImportance;
    % findOutliers;
end

evaluations = [];
if justRunAll || ...
        strcmp(questdlg('Do the leave-one-out evaluation ?', '',...
        'Yes','No','No'),'Yes')
    evalMeanAsPrediction;
    evalTotalMeanAsPrediction;
    %     evalMedianAsPrediction;
    %     evalRandomAsPrediction;
    
    evalRobustFitDensity;
    %     evalRobustFitAllFeatures;
    
    %     evalRandomForestDensity;
    evalRandomForestBestFeatures;
    evalRandomForestAllFeatures;
end

if ~justRunAll && ...
        strcmp(questdlg('Show evaluations ?', '','Yes','No','Yes'),'Yes')
    showFeaturesImportanceEstimation;
    showEvaluations;
end

runTimeInMinutes = toc/60 % put it here to be saved

if justRunAll || ...
        strcmp(questdlg('Save data to file ?', '','Yes','No','No'),'Yes')
    saveData;
end

% clearUselessVariables;


