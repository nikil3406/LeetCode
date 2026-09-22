# LeetCode Submission
# Submission ID: 1971929570
# Status: Accepted
# Language: java
# Runtime: 46 ms
# Memory: 47.1 MB
# Submitted: 2026-04-07 18:55:00 UTC
#
# This file contains the actual code submitted to LeetCode.
#

class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{};
    }
}
