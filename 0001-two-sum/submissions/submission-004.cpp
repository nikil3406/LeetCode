# LeetCode Submission
# Submission ID: 1796383289
# Status: Accepted
# Language: cpp
# Runtime: 3 ms
# Memory: 15 MB
# Submitted: 2025-10-09 13:46:36 UTC
#
# This file contains the actual code submitted to LeetCode.
#

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        map<int,int> a;
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
