# LeetCode Submission
# Submission ID: 1796369105
# Status: Accepted
# Language: cpp
# Runtime: 143 ms
# Memory: 14 MB
# Submitted: 2025-10-09 13:30:11 UTC
#
# This file contains the actual code submitted to LeetCode.
#

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        vector<int> a;
        int c=0;
        int b=target-nums[c];
        for(int i=0;i<nums.size();i++){
            if(nums[i]==b&& i!=c) {
                a.push_back(c);
                a.push_back(i);
                break;
            }
            if(i==nums.size()-1){
                c++;
                if(c>=nums.size()) break;
                b=target-nums[c];
                i=-1;
            }

        }
        return a;

    }
};
