/*
 * LeetCode Submission
 * Submission ID: 2184362213
 * Status: Accepted
 * Language: java
 * Runtime: 1 ms
 * Memory: 47.8 MB
 * Submitted: 2026-10-29 02:31:58 UTC
 */
/*
 * INTUITION
 * This solution uses a standard two-pointer technique to reverse the character array from the outside in. By starting one pointer at the beginning and another at the end, elements are swapped pair by pair until the pointers meet in the middle. This transforms the original array directly without needing to create a new array.
 *
 * APPROACH
 * 1. Initialize a pointer `left` to index 0 and a pointer `right` to index `s.length - 1`.
 * 2. Enter a `while` loop that continues as long as `left` is strictly less than `right`.
 * 3. Store the character at `s[left]` in a temporary variable `temp`.
 * 4. Assign the character at `s[right]` to `s[left]`, and then assign `temp` to `s[right]` to complete the swap.
 * 5. Increment `left` by 1 and decrement `right` by 1 to move the pointers closer to the center.
 * 6. Terminate the loop when the pointers meet or cross, leaving the array fully reversed.
 *
 * WHY IT WORKS
 * Reversing an array means swapping the $i$-th element from the front with the $i$-th element from the back. The two-pointer approach systematically pairs these symmetrical positions together. Stopping when `left >= right` guarantees that every position is swapped exactly once and elements are not redundantly swapped back to their original positions.
 *
 * COMPLEXITY
 * - Time Complexity: O(N), where N is the length of the character array `s`. The loop runs N / 2 times, performing a constant number of operations in each iteration.
 * - Space Complexity: O(1), because all swaps are performed in-place using a single scalar variable `temp` for memory overhead.
 */

class Solution {
    public void reverseString(char[] s) {
        int left = 0;
        int right = s.length - 1;
        
        while (left < right) {
            char temp = s[left];
            s[left] = s[right];
            s[right] = temp;
            left++;
            right--;
        }
    }
}
