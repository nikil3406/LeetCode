# LeetCode Submission
# Submission ID: 1796397279
# Status: Accepted
# Language: cpp
# Runtime: 0 ms
# Memory: 14.9 MB
# Submitted: 2025-10-09 14:01:35 UTC
#
# This file contains the actual code submitted to LeetCode.
#

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int,int> a;
        int b;
        for(int i=0;i<nums.size();i++){
            b=target-nums[i];
            if(a.find(b)!= a.end()){
                return {a[b],i};
            }
            a[nums[i]]=i;
        }
        return {0,0};
    }
};
