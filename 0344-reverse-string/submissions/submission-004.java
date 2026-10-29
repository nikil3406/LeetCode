/*
 * LeetCode Submission
 * Submission ID: 2184362739
 * Status: Accepted
 * Language: java
 * Runtime: 1 ms
 * Memory: 47.8 MB
 * Submitted: 2026-10-29 02:33:26 UTC
 */
/*
 * INTUITION
 * To reverse a sequence in-place, the outermost elements must trade places, followed by the second outermost elements, moving progressively inward. This code uses a standard two-pointer technique starting at both ends of the character array. By iteratively swapping symmetric elements and moving the pointers toward each other, the string is reversed without requiring extra array storage.
 *
 * APPROACH
 * 1. Initialize a pointer named left to 0 (the start of the array) and a pointer named right to s.length - 1 (the end of the array).
 * 2. Enter a while loop that continues as long as left is less than or equal to right.
 * 3. Perform an in-place swap using a temporary character variable temp to exchange s[left] and s[right].
 * 4. Increment left to move toward the middle from the left side.
 * 5. Decrement right to move toward the middle from the right side.
 * 6. Terminate when the pointers meet or cross in the center, leaving the array fully reversed.
 *
 * WHY IT WORKS
 * Reversing an array of length N requires moving the character at index i to index N - 1 - i. The left and right pointers start at symmetrical positions (0 and N - 1) and move inward at the same speed. Swapping s[left] and s[right] directly places both characters into their correct final positions for a reversed string.
 *
 * COMPLEXITY
 * Time Complexity: O(n), where n is the length of array s. The while loop runs n / 2 times, performing O(1) constant-time swap operations during each iteration.
 * Space Complexity: O(1) auxiliary space. The algorithm modifies the input array in-place using only three primitive local variables (left, right, and temp).
 */

class Solution {
    public void reverseString(char[] s) {
        int left = 0;
        int right = s.length - 1;
        
        while (left <= right) {
            char temp = s[left];
            s[left] = s[right];
            s[right] = temp;
            left++;
            right--;
        }
    }
}
