% Copyright (c) 2016 Diego Furtado Silva, Chin-Chia Michael Yeh, Yan Zhu,
% Gustavo E. A. P. A. Batista, and Eamonn Keogh
%
% Permission is hereby granted, free of charge, to any person obtaining a copy
% of this software and associated documentation files (the "Software"), to 
% deal in the Software without restriction, including without limitation the 
% rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
% sell copies of the Software, and to permit persons to whom the Software is 
% furnished to do so, subject to the following conditions:
%
% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
% OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
% AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
% FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
% DEALINGS IN THE SOFTWARE.  

% Compute the similarity join of a given time series A with another time 
% series B
%
% [MatrixProfile, MatrixProfileIndex] = SiMPle(A, B, SubsequenceLength)
% Output:
%     MatrixProfile: matrix porfile of the join (vector)
%     MatrixProfileIndex: matrix porfile index of the join (vector)
% Input:
%     A: first input time series (matrix - in the case of 12-chroma, 
%			the matrix shall be 12xN)
%     B: second input time series (matrix)
%     SubsequenceLength: interested subsequence length (scalar)
%

function [MatrixProfile, MPindex] = SiMPle_SelfFast(A, SubsequenceLength)
%% we want the features in the columns
if (size(A,2) > size(A,1))
    A = A';
end

%% set trivial match exclusion zone
exclusionZone = round(SubsequenceLength/2);

%% initialization
MatrixProfileLength = size(A,1) - SubsequenceLength + 1;
MatrixProfile = zeros(MatrixProfileLength, 1);
MPindex = zeros(MatrixProfileLength, 1);
nD = size(A,2);

%% compute necessary values
[X, n, sumx2] = fastfindNNPre(A, SubsequenceLength);

%% compute first distance profile
subsequence = A(1:SubsequenceLength,:);
[distanceProfile, currz, dropval, sumy2] = fastfindNN(X, subsequence, ...
    n, SubsequenceLength, nD, sumx2);
firstz = currz;

distanceProfile(1:exclusionZone) = inf;
[MatrixProfile(1), MPindex(1)] = min(distanceProfile);

nz = size(currz,1);

%% compute the remainder of the matrix profile
for i = 2:MatrixProfileLength
    
    subsequence = A(i:i+SubsequenceLength-1,:);

    sumy2 = sumy2-dropval.^2+subsequence(end,:).^2;
    
    for iD = 1 : nD
        currz(2:nz,iD) = currz(1:nz-1,iD) + subsequence(end,iD) .* ...
            A(SubsequenceLength+1:SubsequenceLength+nz-1,iD) - ...
            dropval(iD) .* A(1:nz-1,iD);
    end
    currz(1,:) = firstz(i,:);
    dropval=subsequence(1,:);

    distanceProfile = zeros(length(sumx2),1);
    for iD = 1 : nD
        distanceProfile = distanceProfile + sumx2(:,iD) - ...
            2 * currz(:,iD) + sumy2(iD);
        %dist = sqrt(dist);
    end
    
    exclusionZoneStart = max(1, i-exclusionZone);
    exclusionZoneEnd = min(MatrixProfileLength, i+exclusionZone);
    distanceProfile(exclusionZoneStart:exclusionZoneEnd) = inf;

    [MatrixProfile(i), MPindex(i)] = min(distanceProfile);

end

    
end


%% The following two functions are modified from the code provided in the following URL
%  http://www.cs.unm.edu/~mueen/FastestSimilaritySearch.html
function [X, n, sumx2] = fastfindNNPre(x, m)
n = size(x,1);
nD = size(x,2);
x(n+1:2*n,:) = 0;
X = fft(x);
cum_sumx2 =  cumsum(x.^2);
sumx2 = cum_sumx2(m:n,:)-[zeros(1,nD);cum_sumx2(1:n-m,:)];
end

function [dist, z, dropval, sumy2] = fastfindNN(X, y, n, m, nD, sumx2)
dropval=y(1,:);
%x is the data, y is the query
y = y(end:-1:1,:);
y(m+1:2*n,:) = 0;

%The main trick of getting dot products in O(n log n) time
Y = fft(y);
Z = X.*Y;
z = ifft(Z);

%compute y stats -- O(n)
sumy2 = sum(y.^2); 

% computing the distances -- O(n) time
z=real(z(m:n,:));
dist = zeros(length(sumx2),1);
% keyboard
for iD = 1 : nD
    dist = dist + sumx2(:,iD)-2*z(:,iD)+sumy2(iD);
    %dist = sqrt(dist);
end
end