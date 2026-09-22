# LeetCode Submission
# Submission ID: 1796349563
# Status: Accepted
# Language: cpp
# Runtime: 143 ms
# Memory: 13.9 MB
# Submitted: 2025-10-09 13:06:23 UTC
#
# This file contains the actual code submitted to LeetCode.
#

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        vector<int> a;
        for(int i=0;i<nums.size();i++){
            for(int j=i+1;j<nums.size();j++){
                if(nums[i]+nums[j]==target){
                    a.push_back(i);
                    a.push_back(j);
                }
            }
        }
        return a;
    }
};
