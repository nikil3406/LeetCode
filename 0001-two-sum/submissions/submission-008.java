/*
 * LeetCode Submission
 * Submission ID: 2149781122
 * Status: Accepted
 * Language: java
 * Runtime: 44 ms
 * Memory: 47.1 MB
 * Submitted: 2026-09-22 13:53:01 UTC
 */
/*
 * INTUITION
 * This solution uses a brute-force approach to check every possible pair of elements in the array. By fixing one element with an outer loop and searching through all subsequent elements with an inner loop, it directly tests if their sum equals the target. It avoids using the same element twice by always starting the inner search at the index immediately following the outer loop's index.
 *
 * APPROACH
 * 1. Iterate through the array using an outer loop with index i running from index 0 up to the end of the array.
 * 2. For each element at index i, run an inner loop with index j starting from i + 1 to the end of the array.
 * 3. Calculate the sum of nums[i] and nums[j] and check if it equals target.
 * 4. When a matching pair is found, immediately construct and return an array containing the indices [i, j].
 * 5. If no pair is found after checking all combinations, return an empty array.
 *
 * WHY IT WORKS
 * By examining every index pair (i, j) where j > i, the code exhaustively evaluates all distinct pairs in the array without using any element twice. Because the problem statement guarantees that exactly one valid answer exists, the algorithm is sure to hit the matching pair and return its indices.
 *
 * COMPLEXITY
 * Time Complexity: O(n^2), where n is the length of nums. In the worst case, the nested loops will iterate through approximately n * (n - 1) / 2 pairs before finding the target sum.
 * Space Complexity: O(1) auxiliary space, as the algorithm only uses a few integer variables for loop iteration and returns a fixed-size array without allocating extra data structures.
 */

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
